# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin continue_cascade}

Continue Cascade From a Fit Node
################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

Purpose
*******
Sometimes when running the cascade, the fit or statistics for a node fails.
This may be becasue of something that happend on the system,
or becasue of some of the settings in the :ref:`glossary.root_node_database`.
This routine enables you to continue the cascade from such a node.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db<all_node_db>`
relative to the current working directory.
This argument can't be ``None``.

fit_node_database
*****************
is a python string specifying the location of a dismod_at database
relative to the current working directory.
This is a :ref:`glossary.fit_node_database` with the
final state after running :ref:`cascade_root_node` on this database.
The necessary state of *fit_node_database* is reached before
cascade_root_node starts runs on any of its child nodes.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary.fit_goal_set` .
This argument can't be ``None``.

trace_fit
*********
if ``True``, ( ``False`` ) the progress of the dismod at fit commands
will be printed on standard output during the optimization.

{xsrst_end   continue_cascade}
'''
import time
import os
import multiprocessing
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def add_log_entry(connection, message) :
    #
    # log_table
    log_table = dismod_at.get_table_dict(connection, 'log')
    #
    # seconds
    seconds   = int( time.time() )
    #
    # message_type
    message_type = 'at_cascade'
    #
    # cmd
    cmd = 'insert into log'
    cmd += ' (log_id,message_type,table_name,row_id,unix_time,message) values('
    cmd += str( len(log_table) ) + ','     # log_id
    cmd += f'"{message_type}",'            # message_type
    cmd += 'null,'                         # table_name
    cmd += 'null,'                         # row_id
    cmd += str(seconds) + ','              # unix_time
    cmd += f'"{message}")'                 # message
    dismod_at.sql_command(connection, cmd)
# ----------------------------------------------------------------------------
def move_table(connection, src_name, dst_name) :
    #
    command     = 'DROP TABLE IF EXISTS ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME COLUMN '
    command    += src_name + '_id TO ' + dst_name + '_id'
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME TO ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    # log table
    message      = f'move table {src_name} to {dst_name}'
    add_log_entry(connection, message)
# ----------------------------------------------------------------------------
def continue_cascade(
# BEGIN syntax
# at_cascade.continue_cascade(
    all_node_database = None,
    fit_node_database = None,
    fit_goal_set      = None,
    trace_fit         = False,
# )
# END syntax
) :
    assert not all_node_database is None
    assert not fit_node_database is None
    assert not fit_goal_set is None
    #
    # node_table, covariate_table
    new             = False
    connection      = dismod_at.create_connection(fit_node_database, new)
    node_table      = dismod_at.get_table_dict(connection, 'node')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # split_reference_table, all_option, node_split_table
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    node_split_table = dismod_at.get_table_dict(connection, 'node_split')
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    connection.close()
    #
    # root_node_id
    root_node_name   = None
    for row in all_option_table :
        if row['option_name'] == 'root_node_name' :
            root_node_name = row['option_value']
    assert root_node_name is not None
    root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
    #
    # root_split_reference_id
    root_split_reference_id = None
    for row in all_option_table :
        if row['option_name'] == 'root_split_reference_id' :
            root_split_reference_id = row['option_value']
    #
    # fit_integrand
    fit_integrand = at_cascade.get_fit_integrand(fit_node_database)
    #
    # fit_node_id
    fit_node_name = at_cascade.get_parent_node(fit_node_database)
    fit_node_id   = at_cascade.table_name2id(node_table, 'node', fit_node_name)
    #
    # fit_split_reference_id
    if len(split_reference_table) == 0 :
        fit_split_reference_id = None
    else :
        cov_info = at_cascade.get_cov_info(
            all_option_table, covariate_table, split_reference_table
        )
        fit_split_reference_id = cov_info['split_reference_id']
    #
    # job_table
    job_table = at_cascade.create_job_table(
        all_node_database          = all_node_database,
        node_table                 = node_table,
        start_node_id              = fit_node_id,
        start_split_reference_id   = fit_split_reference_id,
        fit_goal_set               = fit_goal_set,
    )
    #
    # check job_table[0]
    assert fit_node_id == job_table[0]['fit_node_id']
    assert fit_split_reference_id == job_table[0]['split_reference_id']
    #
    # start_child_job_id, end_child_job_id
    start_child_job_id = job_table[0]['start_child_job_id']
    end_child_job_id   = job_table[0]['end_child_job_id']
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    #
    # move avgint -> c_root_avgint
    move_table(connection, 'avgint', 'c_root_avgint')
    #
    # node_split_set
    node_split_set = set()
    for row in node_split_table :
        node_split_set.add( row['node_id'] )
    #
    # shift_databases
    shift_databases = dict()
    for job_id in range(start_child_job_id, end_child_job_id) :
        #
        # shift_node_id
        shift_node_id = job_table[job_id]['fit_node_id']
        #
        # shift_split_reference_id
        shift_split_reference_id = job_table[job_id]['split_reference_id']
        #
        # shift_database_dir
        shift_database_dir = at_cascade.get_database_dir(
            node_table              = node_table,
            split_reference_table   = split_reference_table,
            node_split_set          = node_split_set,
            root_node_id            = root_node_id,
            root_split_reference_id = root_split_reference_id,
            fit_node_id             = shift_node_id ,
            fit_split_reference_id  = shift_split_reference_id,
        )
        if not os.path.exists(shift_database_dir) :
            os.makedirs(shift_database_dir)
        #
        # shift_node_database
        shift_node_database = f'{shift_database_dir}/dismod.db'
        #
        # shift_name
        shift_name = shift_database_dir.split('/')[-1]
        #
        # shfit_databases
        shift_databases[shift_name] = shift_node_database
    #
    # create shifted databases
    at_cascade.create_shift_db(
        all_node_database,
        fit_node_database,
        shift_databases
    )
    #
    # move c_root_avgint -> avgint
    move_table(connection, 'c_root_avgint', 'avgint')
    #
    # connection
    connection.close()
    #
    # start_job_id
    start_job_id = 0
    #
    # lock
    lock = multiprocessing.Lock()
    #
    # skip_start_job
    skip_start_job = True
    #
    # max_number_cpu
    max_number_cpu = 1
    #
    # run_parallel_job
    at_cascade.run_parallel(
        job_table         = job_table ,
        start_job_id      = start_job_id,
        all_node_database = all_node_database,
        node_table        = node_table,
        fit_integrand     = fit_integrand,
        trace_fit         = trace_fit,
        skip_start_job    = skip_start_job,
        max_number_cpu    = max_number_cpu,
    )
