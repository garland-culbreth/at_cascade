# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import csv
import at_cascade.ihme
# -----------------------------------------------------------------------------
# age_group_id_table = get_age_group_id_table()
def get_age_group_id_table() :
    #
    # aggregate_age_group_id_set
    aggregate_age_group_id_set = at_cascade.ihme.aggregate_age_group_id_set
    #
    # age_group_inp_file
    age_group_inp_file         = at_cascade.ihme.age_group_inp_file
    #
    # age_group_id_table
    file_ptr            = open(age_group_inp_file)
    reader              = csv.DictReader(file_ptr)
    age_group_id_table  = list()
    for row_in in reader :
        age_group_id      = int( row_in['age_group_id'] )
        if age_group_id not in aggregate_age_group_id_set :
            row_out = dict()
            age_lower         = float( row_in['age_group_years_start'] )
            age_upper         = float( row_in['age_group_years_end'] )
            row_out = {
                'age_group_id' : age_group_id,
                'age_lower'    : age_lower ,
                'age_upper'    : age_upper ,
                'age_mid'      : (age_lower + age_upper) / 2.0,
            }
            age_group_id_table.append( row_out )
    #
    # check for overlapping age groups
    fun = lambda row : row['age_mid']
    age_group_id_table    = sorted(age_group_id_table, key = fun)
    previous_age_upper    = None
    previous_age_group_id = None
    for row in age_group_id_table :
        age_group_id = row['age_group_id']
        age_lower    = row['age_lower']
        age_upper    = row['age_upper']
        if age_lower > age_upper :
            msg  = f'In {age_group_inp_file}\n'
            msg += f'for age_group_id = {age_group_id}, '
            msg += 'age_lower is greater than age_upper'
            assert False, msg
        if previous_age_upper is not None and age_lower < previous_age_upper :
            msg  = f'In {age_group_inp_file}\n'
            msg += f'The age limits for age_group_id = {age_group_id}\n'
            msg += 'overlap the age limits for age_group_id = '
            msg += f'{previous_age_group_id}'
            assert False, msg
        previous_age_upper    = age_upper
        previous_age_group_id = age_group_id
    #
    return age_group_id_table