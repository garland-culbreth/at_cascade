# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import os
import sys
import time
import numpy
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin example_csv_simulate}
{xrst_spell
    dir
    sim
}

Example Using csv_simulate
##########################

Node Tree
*********
::

                n0
          /-----/\-----\
        n1              n2

..  list-table::
    :header-rows: 1

    *   -   Symbol
        -   Documentation
    *   -   csv_dir
        -   :ref:`csv_interface@arguments@csv_dir`
    *   -   command
        -   :ref:`csv_interface@arguments@command`
    *   -   csv_file['option.csv']
        -   :ref:`csv_simulate@input_files@option.csv`
    *   -   csv_file['node.csv']
        -   :ref:`csv_simulate@input_files@node.csv`
    *   -   csv_file['covariate.csv']
        -   :ref:`csv_simulate@input_files@covariate.csv`
    *   -   csv_file['no_effect_rate.csv']
        -   :ref:`csv_simulate@input_files@no_effect_rate.csv`
    *   -   csv_file['multiplier_sim.csv']
        -   :ref:`csv_simulate@input_files@multiplier_sim.csv`
    *   -   csv_file['simulate.csv']
        -   :ref:`csv_simulate@input_files@simulate.csv`


{xrst_file
    BEGIN_PYTHON
    END_PYTHON
}


{xrst_end example_csv_simulate}
"""
# BEGIN_PYTHON
#
# csv_file
csv_file = dict()
#
# option.csv
random_seed = str( int( time.time() ) )
csv_file['option.csv'] = \
'''name,value
std_random_effects,.1
integrand_step_size,5
'''
csv_file['option.csv'] += f'random_seed,{random_seed}\n'
#
# node.csv
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
#
# covariate.csv
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega,haqi
n0,female,50,2000,0.01,1.0
n0,male,50,2000,0.01,1.0
n1,female,50,2000,0.01,0.5
n1,male,50,2000,0.01,0.5
n2,female,50,2000,0.01,1.5
n2,male,50,2000,0.01,1.5
'''
#
# no_effect_rate.csv
csv_file['no_effect_rate.csv'] = \
'''rate_name,age,time,rate_truth
iota,0.0,1980.0,0.01
'''
#
# multiplier_sim.csv
csv_file['multiplier_sim.csv'] = \
'''multiplier_id,rate_name,covariate_or_sex,multiplier_truth
0,iota,haqi,0.5
'''
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,percent_cv'
csv_file['simulate.csv'] = header + \
'''
0,Sincidence,n0,female,0,10,1990,2000,0.2
1,Sincidence,n1,male,10,20,2000,2010,0.2
2,Sincidence,n2,female,20,30,2010,2020,0.2
'''
#
def main() :
    #
    # eps99
    eps99 = 99.0 * numpy.finfo(float).eps
    #
    # csv_dir
    csv_dir = 'build/csv'
    if not os.path.exists(csv_dir) :
        os.mkdir(csv_dir)
    #
    # write csv files
    for name in csv_file :
        file_name = f'{csv_dir}/{name}'
        file_ptr  = open(file_name, 'w')
        file_ptr.write( csv_file[name] )
        file_ptr.close()
    #
    # simulate command
    command = 'simulate'
    at_cascade.csv_interface(csv_dir, command)
    #
    # csv_table
    csv_table = dict()
    for name in csv_file :
        file_name       = f'{csv_dir}/{name}'
        csv_table[name] = at_cascade.read_csv_table( file_name )
    #
    for name in [ 'random_effect.csv', 'data_sim.csv' ] :
        file_name       = f'{csv_dir}/{name}'
        csv_table[name] = at_cascade.read_csv_table( file_name )
    #
    # random_effect.csv
    for sex in [ 'male', 'female' ] :
        sum_random = 0.0
        sum_abs    = 0.0
        for row in csv_table['random_effect.csv'] :
            if row['node_name'] == 'n0' :
                assert float( row['iota'] ) == 0.0
            if row['sex'] == sex :
                sum_abs    += abs( float( row['iota'] ) )
                sum_random += float( row['iota'] )
        assert abs( sum_random ) < eps99 * sum_abs
    #
    # simulate.csv
    for (row_id, row) in enumerate( csv_table['simulate.csv'] ) :
        assert row_id == int( row['simulate_id'] )

    print('simulte.py: OK')
    sys.exit(0)
#
main()
# END_PYTHON
