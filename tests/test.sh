#!/bin/bash

echo "this is some testing text" > first_file.txt
python3 ../charon.py -f charon.test.yml styx apply test_1
mkdir revert_output
python3 ../charon.py -f charon.test.yml styx revert test_1 revert_output
tree revert_output
cat revert_output/first_file.txt
rm -r revert_output apply_output first_file.txt 

# expected output:
# ---------------------------
# applying job: test_1
# reverting job: test_1 into /home/noah/projects/charon/tests/revert_output
# revert_output
# └── first_file.txt
#
# 0 directories, 1 file
# this is some testing text
