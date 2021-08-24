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
{xsrst_begin cascade_fit_node}
{xsrst_spell
    dir
    csv
    var
}

Cascade a Fit Starting at a Node
################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

all_node_database
*****************
is a python string specifying the location of the all node database
relative to the current working directory.
This argument can't be ``None``.

all_node_dir
============
is the directory where the all node database is located.

fit_node_database
*****************
is a python string specifying the location of the
:ref:`glossary.fit_node_database` relative to *all_node_dir*.
This must be a valid :ref:`glossary.root_node_database`.
This argument can't be ``None``.

fit_node
========
The *fit_node_database* must be *fit_node*\ ``/dismod.db``,
or end with the text ``/``\ *fit_node*\ ``/dismod.db``
where *fit_node* is the name of the :ref:`glossary.fit_node` for this database.

fit_node_dir
============
is the directory where the fit node database is located.

node_table
**********
This is a python list where
*node_table*[*node_id*] is a python dictionary representation of the
corresponding row of the dismod_at node table.
This node table is the same as the node table in *fit_node_database*.
It is the same for all the fits and this avoids reading it each time.)
This argument can't be ``None``.

fit_children
************
is a python list of python lists.
For each valid node_id, *fit_children[node_id]* is a list of child_node_id.
Each child_node_id is a child of node_id and is between the root node and the
fit goal set inclusive.
These are the children of node_id that must be fit to
obtain of fit of all the goal nodes.

default
=======
If *fit_children* is None, it will be computed by ``cascade_fit_node``
and reused by recursive calls to this routine.

dismod.db
*********
The results for this fit are in the
*fit_node_dir*\ ``/dismod.db`` dismod_at database.
The corresponding *fit_node_dir/\*.csv* , create by the
dismod_at db2csv command, are also the *fit_node_dir* directory.
Furthermore there is a sub-directory, for each child node of *fit_node_name*,
with the results for that child node.

fit_var
=======
The fit_var table correspond to the posterior
mean for the model variables for the fit node.

sample
======
The sample table contains the corresponding samples from the posterior
distribution for the model variables for the fit node.

predict
=======
The predict table contains predictions corresponding to the sample table and the
avgint table in the root node database except that the node_id column
has been replaced by the node_id for this fit node.

c_predict_fit_var
=================
The c_predict_fit_var table contains predictions corresponding to the
fit_var table and the avgint table in the root node database except that
the node_id column has been replaced by the node_id for this fit node.

{xsrst_end cascade_fit_node}
'''
import os
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def child_node_id_list(node_table, parent_node_id) :
    result = list()
    for (node_id, row) in enumerate(node_table) :
        if row['parent'] == parent_node_id :
            result.append(node_id)
    return result
# ----------------------------------------------------------------------------
def node_table_name2id(node_table, row_name) :
    for (node_id, row) in enumerate(node_table) :
        if row['node_name'] == row_name :
            return node_id
    assert False
# ----------------------------------------------------------------------------
def move_table(connection, src_name, dst_name) :
    command     = 'DROP TABLE IF EXISTS ' + dst_name
    dismod_at.sql_command(connection, command)
    command     = 'ALTER TABLE ' + src_name + ' RENAME COLUMN '
    command    += src_name + '_id TO ' + dst_name + '_id'
    dismod_at.sql_command(connection, command)
    command     = 'ALTER TABLE ' + src_name + ' RENAME TO ' + dst_name
    dismod_at.sql_command(connection, command)
# ----------------------------------------------------------------------------
def set_avgint_node_id(connection, fit_node_id) :
    avgint_table = dismod_at.get_table_dict(connection, 'avgint')
    for row in avgint_table :
        row['node_id'] = fit_node_id
    dismod_at.replace_table(connection, 'avgint', avgint_table)
# ----------------------------------------------------------------------------
def cascade_fit_node(
# BEGIN syntax
# at_cascade.cascade_fit_node(
    all_node_database = None,
    fit_node_database = None,
    node_table        = None,
    fit_children      = None,
# )
# END syntax
) :
    # fit_children
    if fit_children is None :
        new              = False
        connection       = dismod_at.create_connection(all_node_database, new)
        all_option_table = dismod_at.get_table_dict(connection, 'all_option')
        fit_goal_table   = dismod_at.get_table_dict(connection, 'fit_goal')
        connection.close()
        root_node_name   = None
        for row in all_option_table :
            if row['option_name'] == 'root_node_name' :
                root_node_name = row['option_value']
        assert not root_node_name is None
        root_node_id = node_table_name2id(node_table, root_node_name)
        fit_children = at_cascade.get_fit_children(
            root_node_id, fit_goal_table, node_table
        )
    #
    # all_node_dir
    path_list = all_node_database.split('/')
    if len(path_list) == 1 :
        all_node_dir = '.'
    else :
        path_list = path_list[: -1]
        all_node_dir = '/'.join(path_list)
    #
    # fit_node_name
    path_list = fit_node_database.split('/')
    assert len(path_list) >= 2
    assert path_list[-1] == 'dismod.db'
    fit_node_name = path_list[-2]
    #
    # fit_node_id
    fit_node_id = node_table_name2id(node_table, fit_node_name)
    #
    # fit_node_dir, fit_node_database
    fit_node_dir = fit_node_database[ : - len('dismod.db') - 1 ]
    if all_node_dir != '.' :
        fit_node_dir      = all_node_dir + '/' + fit_node_dir
        fit_node_database = all_node_dir + '/' + fit_node_database
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    #
    # add omega to model
    at_cascade.omega_constraint(all_node_database, fit_node_database)
    #
    # move avgint -> c_avgint
    move_table(connection, 'avgint', 'c_avgint')
    #
    # avgint table for child predictions
    at_cascade.child_avgint_table(all_node_database, fit_node_database)
    #
    # init
    dismod_at.system_command_prc( [ 'dismod_at', fit_node_database, 'init' ] )
    #
    # fit
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'fit', 'both' ]
    )
    #
    # sample
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'sample', 'asymptotic', 'both', '20' ]
    )
    # c_predict_fit_var
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    )
    move_table(connection, 'predict', 'c_predict_fit_var')
    #
    # predict sample using child_avgint_table version of avgint
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    )
    #
    # child_node_list
    child_node_list = fit_children[fit_node_id]
    #
    # child_node_databases
    child_node_databases = dict()
    for node_id in child_node_list :
        node_name = node_table[node_id]['node_name']
        subdir    = fit_node_dir + '/' + node_name
        if not os.path.exists(subdir) :
            os.makedirs(subdir)
        child_node_databases[node_name] = subdir + '/dismod.db'
    #
    # create child node databases
    at_cascade.create_child_node_db(
        all_node_database,
        fit_node_database,
        child_node_databases
    )
    #
    # move c_avgint -> avgint (original version of this table)
    move_table(connection, 'c_avgint', 'avgint')
    #
    # node_id for predictions for fit_node
    set_avgint_node_id(connection, fit_node_id)
    #
    # c_predict_fit_var
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    )
    move_table(connection, 'predict', 'c_predict_fit_var')
    #
    # predict
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    )
    # db2csv
    dismod_at.system_command_prc(
        [ 'dismodat.py', fit_node_database, 'db2csv' ] )
    #
    # fit child node databases
    for node_name in child_node_databases :
        fit_node_database = child_node_databases[node_name]
        cascade_fit_node(all_node_database, fit_node_database, node_table)
    #
    # connection
    connection.close()
