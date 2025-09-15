#!/bin/bash

# tests nested directories + non-encrypted

green="\e[32m"
red="\e[31m"
reset="\e[0m"

mkdir -p input_directory/nested_directory
echo "this is the foo file" > input_directory/file1.txt
echo "this is the baz file" > input_directory/nested_directory/file2.txt
charon -f charon.test.yml apply test_2
mkdir revert_output
charon -f charon.test.yml revert test_2 revert_output

expected_output='[
  {
    "type": "directory",
    "name": "revert_output",
    "contents": [
      {
        "type": "file",
        "name": "file1.txt"
      },
      {
        "type": "directory",
        "name": "nested_directory",
        "contents": [
          {
            "type": "file",
            "name": "file2.txt"
          }
        ]
      }
    ]
  },
  {
    "type": "report",
    "directories": 2,
    "files": 2
  }
]
this is the foo file
this is the baz file'

real_output="$(tree -J revert_output | jq)
$(cat revert_output/file1.txt)
$(cat revert_output/nested_directory/file2.txt)"


if [ "$real_output" == "$expected_output" ]; then
    echo -e "${green}test 2 passed!${reset}"
else
    echo -e "${red}test 2 failed!${reset}"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi