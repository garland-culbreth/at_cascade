#! /bin/bash -e
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
# bash function that echos and executes a command
echo_eval() {
    echo $*
    eval $*
}
# -----------------------------------------------------------------------------
if [ "$0" != 'bin/check_all.sh' ]
then
    echo 'bin/check_all.sh must be run from its parent directory.'
    exit 1
fi
# -----------------------------------------------------------------------------
echo_eval bin/run_sphinx.sh
echo_eval python3 example/one_at_function.py
echo_eval python3 test/child_avgint_table.py
echo_eval python3 test/omega_constraint.py
# -----------------------------------------------------------------------------
echo 'check_all.sh: OK'
exit 0