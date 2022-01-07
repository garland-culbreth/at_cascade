# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ------------------------------------------------------------------------------
import csv
import os
import dismod_at
import at_cascade.ihme
# ------------------------------------------------------------------------------
def write_message_type_file(
    result_dir, message_type, fit_goal_set, root_node_database
) :
    #
    # all_node_database
    all_node_database = at_cascade.ihme.all_node_database
    #
    # message_dict
    message_dict = at_cascade.check_log(
        message_type       = message_type,
        all_node_database  = all_node_database,
        root_node_database = root_node_database,
        fit_goal_set       = fit_goal_set,
    )
    #
    # file_name
    file_name = f'{result_dir}/summary/{message_type}'
    #
    # file_ptr
    file_ptr = open(file_name, 'w')
    #
    first_key = True
    for key in message_dict :
        #
        # first_key
        if not first_key :
            file_ptr.write('\n')
        first_key = False
        #
        file_ptr.write( f'{key}\n' )
        for message in message_dict[key] :
            file_ptr.write( f'{message}\n' )
    #
    file_ptr.close()
# ------------------------------------------------------------------------------
def combine_predict_files(
    result_dir, fit_goal_set, root_node_database
) :
    #
    # all_node_database
    all_node_database = at_cascade.ihme.all_node_database
    #
    #
    # node_table, covariate_table
    new        = False
    connection      = dismod_at.create_connection(root_node_database, new)
    node_table      = dismod_at.get_table_dict(connection, 'node')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # all_option_table, node_split_table, split_reference_table
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_option_table =  dismod_at.get_table_dict(connection, 'all_option')
    node_split_table =  dismod_at.get_table_dict(connection, 'node_split')
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    connection.close()
    #
    # node_split_set
    node_split_set = set()
    for row in node_split_table :
        node_split_set.add( row['node_id'] )
    #
    # root_node_id
    root_node_name = at_cascade.get_parent_node(root_node_database)
    root_node_id   = at_cascade.table_name2id(
            node_table, 'node', root_node_name
    )
    #
    # root_split_reference_id
    if len(split_reference_table) == 0 :
        root_split_refernence_id = None
    else :
        cov_info = at_cascade.get_cov_info(
            all_option_table      = all_option_table ,
            covariate_table       = covariate_table ,
            split_reference_table = split_reference_table,
        )
        root_split_reference_id = cov_info['split_reference_id']
    #
    # job_table
    job_table = at_cascade.create_job_table(
        all_node_database          = all_node_database       ,
        node_table                 = node_table              ,
        start_node_id              = root_node_id            ,
        start_split_reference_id   = root_split_reference_id ,
        fit_goal_set               = fit_goal_set            ,
    )
    #
    # predict_csv_file_list
    predict_csv_file_list = list()
    #
    # job_id, job_row
    for (job_id, job_row) in enumerate(job_table) :
        #
        # job_name, fit_node_id, fit_split_reference_id
        job_name               = job_row['job_name']
        fit_node_id            = job_row['fit_node_id']
        fit_split_reference_id = job_row['split_reference_id']
        #
        # database_dir
        database_dir           = at_cascade.get_database_dir(
            node_table              = node_table               ,
            split_reference_table   = split_reference_table    ,
            node_split_set          = node_split_set           ,
            root_node_id            = root_node_id             ,
            root_split_reference_id = root_split_reference_id  ,
            fit_node_id             = fit_node_id              ,
            fit_split_reference_id  = fit_split_reference_id   ,
        )
        #
        # file_in
        file_in = f'{result_dir}/{database_dir}/predict.csv'
        #
        # predict_csv_file_list
        if os.path.exists(file_in) :
            predict_csv_file_list.append(file_in)
    #
    # predict.csv
    file_out_name = f'{result_dir}/summary/predict.csv'
    file_obj_out  = open(file_out_name, "w")
    writer        = None
    for file_in_name in predict_csv_file_list :
        file_obj_in   = open(file_in_name, 'r')
        reader     = csv.DictReader(file_obj_in)
        for row in reader :
            if writer is None :
                keys   = row.keys()
                writer = csv.DictWriter(file_obj_out, fieldnames=keys)
                writer.writeheader()
            writer.writerow(row)
        file_obj_in.close()
    file_obj_out.close()
# ------------------------------------------------------------------------------
def summary(
    result_dir         = None,
    root_node_database = None,
    fit_goal_set       = None
) :
    assert type(result_dir) == str
    assert type(root_node_database) == str
    assert type(fit_goal_set) == set
    #
    # summary_dir
    summary_dir = f'{result_dir}/summary'
    if not os.path.exists(summary_dir) :
        os.mkdir(summary_dir)
    #
    # error
    message_type = 'error'
    write_message_type_file(
        result_dir, message_type, fit_goal_set, root_node_database
    )
    #
    # warning
    message_type = 'warning'
    write_message_type_file(
        result_dir, message_type, fit_goal_set, root_node_database
    )
    #
    # predict.csv
    combine_predict_files(
        result_dir, fit_goal_set, root_node_database
    )
