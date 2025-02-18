#!/bin/bash


# tests nested directories + non-encrypted

green="\e[32m"
red="\e[31m"
reset="\e[0m"


export PYTHONPATH="../"
mkdir -p input_directory/nested_directory
echo "this is the foo file" > input_directory/file1.txt
echo "this is the baz file" > input_directory/nested_directory/file2.txt
python3 -m charon -f charon.test.yml apply test_2
mkdir revert_output
python3 -m charon -f charon.test.yml revert test_2 revert_output


expected_output="revert_output
├── file1.txt
└── nested_directory
    └── file2.txt

1 directory, 2 files
this is the foo file
this is the baz file"

real_output="$(tree revert_output)
$(cat revert_output/file1.txt)
$(cat revert_output/nested_directory/file2.txt)"


if [ "$real_output" == "$expected_output" ]; then
    echo -e "${green}test passed!${reset}"
else
    echo -e "${red}test failed!${reset}"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi

rm -r revert_output apply_archive.tar.gz input_directory 2>/dev/null
rm -rf repo_2

