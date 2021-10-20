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
{xsrst_begin get_split_info}
{xsrst_spell
    dict
}

Splitting Covariate Reference Index
###################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

all_option_table
****************
This is the :ref:`all_option_table` as a python list
of python dictionaries.
This argument can't be ``None``.

covariate_table
****************
This is the dismod_at covariate table as a python list
of python dictionaries.
This argument can't be ``None``.

split_info
**********
If :ref:`all_option_table.split_list` is not in the
all_option table, the return value *split_info* is ``None``.
Otherwise, it is a `dict` with the following keys:

split_list
==========
if *key* is split_level, *split_info[key]* is a ``str``
representation of :ref:`all_option_table.split_list`.

split_level
===========
if *key* is split_level, *split_info[key]* is an ``int``
representation of :ref:`all_option_table.split_list.split_level`.

split_covariate_name
====================
if *key* is split_covariate_name, *split_info[key]* is a ``str``
representation of :ref:`all_option_table.split_list.split_covariate_name`.

split_reference_list
====================
if *key* is split_reference_list, *split_info[key]* is a
``list`` of ``float`` representation of
:ref:`all_option_table.split_list.split_reference_list`.

split_reference_id
====================
if *key* is split_reference_id, *split_info[key]* is an ``int``
containing an index in the split_reference_list.
The corresponding value is split_reference_list is equal to
to reference value for split_covariate_name in the covariate table.

{xsrst_end get_split_info}
'''
import at_cascade
#
def get_split_info(
# BEGIN syntax
# split_info = get_split_info(
    all_option_table = None ,
    covariate_table  = None ,
# )
# END syntax
) :
    #
    # split_list
    split_list = None
    for row in all_option_table :
        if row['option_name'] == 'split_list' :
            split_list           = row['option_value']
    if split_list is None :
        return None
    #
    # split_level, split_covarate_name, split_reference_list
    temp_list = split_list.split()
    split_level          = int( temp_list[0] )
    split_covariate_name = temp_list[1]
    split_reference_list = temp_list[2:]
    for k in range( len(split_reference_list) ) :
        split_reference_list[k] = float( split_reference_list[k] )
    #
    # split_covariate_id
    split_covariate_id   = at_cascade.table_name2id(
        covariate_table, 'covariate', split_covariate_name
    )
    #
    # split_reference
    split_reference = covariate_table[split_covariate_id]['reference']
    #
    # split_reference_id
    if not split_reference in split_reference_list :
        msg  = 'Cannot find covaraite table value for splitting covariate '
        msg += 'in split_reference_list\n'
        msg += f'split_list = {split_list}, '
        msg += f'split_covariate_id = {split_covariate_id}, '
        msg += f'covariate table reference = {split_reference}'
        assert False, msg
    split_reference_id = split_reference_list.index( split_reference )
    #
    split_info = {
        'split_list':            split_list,
        'split_level':           split_level,
        'split_covariate_name':  split_covariate_name,
        'split_reference_list':  split_reference_list,
        'split_reference_id':    split_reference_id,
    }
    #
    return split_info
