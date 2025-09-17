#!/bin/bash

# tests nested directories + non-encrypted

green="\e[32m"
red="\e[31m"
reset="\e[0m"

        # - dir1/dir2
        # - dir1/dir3/dir4
        # - dir1/dir3/file1.txt
        # - dir2/file2.txt
        # - dir3

mkdir -p dir1/dir2
mkdir -p dir1/dir3/dir4
mkdir -p dir2

echo "fileA contents" > dir1/dir2/fileA.txt
echo "fileB contents" > dir1/dir2/fileB.txt
echo "fileC contents" > dir1/fileC.txt

echo "fileD contents" > dir1/dir3/fileD.txt
echo "fileE contents" > dir1/dir3/dir4/fileE.txt

echo "file1 contents" > dir1/dir3/file1.txt

echo "fileF contents" > dir2/fileF.txt
echo "fileG contents" > dir2/fileG.txt
echo "file2 contents" > dir2/file2.txt

charon -f charon.test.yml apply test_5
mkdir revert_output
charon -f charon.test.yml revert test_5 revert_output

expected_output='revert_output/
revert_output/test/
revert_output/test/dir1/
revert_output/test/dir1/dir2/
revert_output/test/dir1/dir2/fileA.txt
revert_output/test/dir1/dir2/fileB.txt
revert_output/test/dir1/dir3/
revert_output/test/dir1/dir3/dir4/
revert_output/test/dir1/dir3/dir4/fileE.txt
revert_output/test/dir1/dir3/file1.txt
revert_output/test/dir2/
revert_output/test/dir2/file2.txt
fileA contents
fileB contents
fileE contents
file1 contents
file2 contents'

real_output="$(tree -fiF --noreport revert_output)
$(tree -fiF --noreport revert_output | grep -v '/$' | xargs -d '\n' -r cat)"


if [ "$real_output" == "$expected_output" ]; then
    echo -e "${green}test 5 passed!${reset}"
else
    echo -e "${red}test 5 failed!${reset}"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi
