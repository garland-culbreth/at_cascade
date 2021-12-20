# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import os
import csv
import dismod_at
import at_cascade.ihme
# -----------------------------------------------------------------------------
def write_table(connection, table, tbl_name, col_list) :
    col_name_list = list()
    col_type_list = list()
    for (col_name, col_type) in col_list :
        col_name_list.append( col_name )
        col_type_list.append( col_type )
    #
    row_list = list()
    for row_in in table :
        row_out = list()
        for col_name in col_name_list :
            row_out.append( row_in[col_name] )
        row_list.append( row_out )
    dismod_at.create_table(
        connection, tbl_name, col_name_list, col_type_list, row_list
    )
# -----------------------------------------------------------------------------
# write_all_node_database()
# all_option_table, root_node_database
def write_all_node_database() :
    #
    # all_node_database
    all_node_database = at_cascade.ihme.all_node_database
    if os.path.exists( all_node_database ) :
        print( f'Using existing {all_node_database}' )
        return
    else :
        print( f'Creating {all_node_database}' )
    #
    # intermediate files
    all_option_table_file    = at_cascade.ihme.all_option_table_file
    mulcov_freeze_table_file = at_cascade.ihme.mulcov_freeze_table_file
    omega_age_table_file     = at_cascade.ihme.omega_age_table_file
    omega_time_table_file    = at_cascade.ihme.omega_time_table_file
    all_mtall_table_file     = at_cascade.ihme.all_mtall_table_file
    mtall_index_table_file   = at_cascade.ihme.mtall_index_table_file
    #
    # root_node_database
    root_node_database = at_cascade.ihme.root_node_database
    #
    # root_table
    root_table = dict()
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    root_table['covariate'] = dismod_at.get_table_dict(connection, 'covariate')
    root_table['node']      = dismod_at.get_table_dict(connection, 'node')
    root_table['age']       = dismod_at.get_table_dict(connection, 'age')
    root_table['time']      = dismod_at.get_table_dict(connection, 'time')
    connection.close()
    #
    # connection
    new        = True
    connection = dismod_at.create_connection(all_node_database, new)
    #
    # all_option
    all_option_table = at_cascade.ihme.get_table_csv(all_option_table_file)
    tbl_name = 'all_option'
    col_list = [ ('option_name', 'text'), ('option_value', 'text') ]
    write_table(connection, all_option_table, tbl_name, col_list)
    #
    # split_refererence_table
    split_reference_table = list()
    sex_info_dict         = at_cascade.ihme.sex_info_dict
    for sex_name in sex_info_dict :
        row                = sex_info_dict[sex_name]
        covariate_value    = row['covariate_value']
        split_reference_id = row['split_reference_id']
        row_out = {
            'split_reference_name'  : sex_name,
            'split_reference_value' : covariate_value,
            'split_reference_id'    : split_reference_id,
        }
        split_reference_table.append( row_out )
    fun = lambda row : row['split_reference_id']
    split_reference_table = sorted(split_reference_table, key = fun)
    tbl_name = 'split_reference'
    col_list = [
        ('split_reference_name', 'text'),
        ('split_reference_value', 'real'),
    ]
    write_table(connection, split_reference_table, tbl_name, col_list)
    #
    # all_option
    all_option = dict()
    for row in all_option_table :
        option_name  = row['option_name']
        option_value = row['option_value']
        all_option[option_name] = option_value
    #
    # not_relative_set
    not_relative_set = set( all_option['absolute_covariates'].split() )
    not_relative_set.add( all_option['split_covariate_name'] )
    #
    # covariate_set
    covariate_set = set()
    for row in root_table['covariate'] :
        covariate_set.add( row['covariate_name'] )
    #
    # realtive_set
    relative_set = covariate_set - not_relative_set
    #
    # all_cov_reference_table
    # Note the value 0.0 does not matter becasue it will be replaced using
    # data4cov_reference
    all_cov_reference_table = list()
    for node_id in range( len( root_table['node'] ) ) :
        for covariate_id in range( len( root_table['covariate'] ) ) :
            for split_reference_id in range( len(split_reference_table) ) :
                row = {
                    'node_id'            : node_id,
                    'covariate_id'       : covariate_id,
                    'split_reference_id' : split_reference_id,
                    'reference'          : 0.0,
                }
                all_cov_reference_table.append( row )
    tbl_name = 'all_cov_reference'
    col_list = [
        ('node_id', 'integer'),
        ('covariate_id', 'integer'),
        ('split_reference_id', 'integer'),
        ('reference', 'real'),
    ]
    write_table(connection, all_cov_reference_table, tbl_name, col_list)
    #
    # node_split_table
    node_split_table = list()
    for node_name in at_cascade.ihme.split_node_name_set :
        node_split_table.append( { 'node_name' : node_name } )
    tbl_name = 'node_split'
    col_list = [ ('node_name', 'text') ]
    write_table(connection, node_split_table, tbl_name, col_list)
    #
    # mulcov_freeze_table
    mulcov_freeze_table = at_cascade.ihme.get_table_csv(
        mulcov_freeze_table_file
    )
    for row in mulcov_freeze_table :
        row['fit_node_id']        = int( row['fit_node_id'] )
        row['split_reference_id'] = int( row['split_reference_id'] )
        row['mulcov_id']          = int( row['mulcov_id'] )
    tbl_name = 'mulcov_freeze'
    col_list = [
        ('fit_node_id', 'integer'),
        ('split_reference_id', 'integer'),
        ('mulcov_id', 'integer'),
    ]
    write_table(connection, mulcov_freeze_table, tbl_name, col_list)
    #
    # omega_age_grid_table
    omega_age_table  = at_cascade.ihme.get_table_csv(omega_age_table_file)
    age_list         = list()
    for row in root_table['age'] :
        age_list.append( row['age'] )
    omega_age_grid_table = list()
    for row in omega_age_table :
        age    = float( row['age'] )
        age_id = age_list.index( age )
        omega_age_grid_table.append( { 'age_id' : age_id } )
    tbl_name = 'omega_age_grid'
    col_list = [ ('age_id', 'integer') ]
    write_table(connection, omega_age_grid_table, tbl_name, col_list)
    #
    # omega_time_grid_table
    omega_time_table  = at_cascade.ihme.get_table_csv(omega_time_table_file)
    time_list         = list()
    for row in root_table['time'] :
        time_list.append( row['time'] )
    omega_time_grid_table = list()
    for row in omega_time_table :
        time    = float( row['time'] )
        time_id = time_list.index( time )
        omega_time_grid_table.append( { 'time_id' : time_id } )
    tbl_name = 'omega_time_grid'
    col_list = [ ('time_id', 'integer') ]
    write_table(connection, omega_time_grid_table, tbl_name, col_list)
    #
    # mtall_index_table
    mtall_index_table = at_cascade.ihme.get_table_csv(mtall_index_table_file)
    tbl_name = 'mtall_index'
    col_list = [
        ('node_id', 'integer'),
        ('split_reference_id', 'integer'),
        ('all_mtall_id', 'integer'),
    ]
    write_table(connection, mtall_index_table, tbl_name, col_list)
    #
    # all_mtall_table
    all_mtall_table   = at_cascade.ihme.get_table_csv(all_mtall_table_file)
    tbl_name = 'all_mtall'
    col_list = [ ('all_mtall_value', 'real') ]
    write_table(connection, all_mtall_table, tbl_name, col_list)
    #
    # mtspecific_table
    all_mtspecific_table   = list()
    tbl_name = 'mtall_specific'
    col_list = [ ('all_mtspecific_value', 'real') ]
    write_table(connection, all_mtspecific_table, tbl_name, col_list)
    #
    # connection
    connection.close()