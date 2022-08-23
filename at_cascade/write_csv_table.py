# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import csv
"""
{xrst_begin write_csv_table}
{xrst_spell
   len
}

Create A CSV File from a Table
##############################

Syntax
******
{xrst_literal
   BEGIN_SYNTAX
   END_SYNTAX
}

table
*****
This must be  a ``list`` of ``dict``.

columns
*******
This is a ``list`` of ``str`` specifying the keys in the table dictionary
that are written to the file.
If this argument is ``None`` ,
*table* [0].keys() is used as its default value.

file_name
*********
is a ``str`` with the name of the CSV file.
Upon return, this file has ``len(`` *table* ``)`` + 1 lines,
``len(`` *columns* ``)`` columns, with the following values

.. list-table::

   * - columns[0]
     - columns[1]
     - columns[2]
     - ...
   * - table[0][ columns[0] ]
     - table[0][ columns[1] ]
     - table[0][ columns[2] ]
     - ...
   * - table[1][ columns[0] ]
     - table[1][ columns[1] ]
     - table[1][ columns[2] ]
     - ...
   * - \:
     - \:
     - \:
     - ...

Example
*******
:ref:`csv_table`


{xrst_end write_csv_table}
"""
def write_csv_table(
# BEGIN_SYNTAX
# table = at_cascade.write_csv_table(
   file_name  = None,
   table      = None,
   columns    = None,
# )
# END_SYNTAX
) :
   assert type(file_name)  == str
   assert type(table)      == list
   assert type(columns) == list or columns == None
   if columns == None :
      columns = table[0].keys()
   #
   file_ptr    = open(file_name, 'w')
   writer      = csv.DictWriter(file_ptr, fieldnames = columns)
   writer.writeheader()
   writer.writerows( table )
   file_ptr.close()
