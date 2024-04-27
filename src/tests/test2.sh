#!/bin/bash

mkdir -p input_directory/nested_directory
echo "this is the foo file" > input_directory/file1.txt
echo "this is the baz file" > input_directory/nested_directory/file2.txt
python3 ../charon.py -f charon.test.yml styx apply test_2
mkdir revert_output
python3 ../charon.py -f charon.test.yml styx revert test_2 revert_output
tree revert_output
cat revert_output/file1.txt
cat revert_output/nested_directory/file2.txt
rm -r revert_output apply_archive.tar.gz input_directory

# expected output:
# -----------------
# applying job: test_2
# reverting job: test_2 into /home/noah/projects/charon/tests/revert_output
# revert_output
# ├── file1.txt
# └── nested_directory
#     └── file2.txt
#
# 1 directory, 2 files
# this is the foo file
# this is the baz file
