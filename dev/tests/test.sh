#!/bin/bash

# tests individual files + encryption

green="\e[32m"
red="\e[31m"
reset="\e[0m"

echo "this is some testing text" > first_file.txt
charon -f charon.test.yml apply test_1
mkdir revert_output
charon -f charon.test.yml revert test_1 revert_output


expected_output='[
  {
    "type": "directory",
    "name": "revert_output",
    "contents": [
      {
        "type": "file",
        "name": "first_file.txt"
      }
    ]
  },
  {
    "type": "report",
    "directories": 1,
    "files": 1
  }
]
this is some testing text'

real_output="$(tree -J revert_output | jq)
$(cat revert_output/first_file.txt)"

if [ "$real_output" == "$expected_output" ]; then
    echo -e "${green}test 1 passed!${reset}"
else
    echo -e "${red}test 1 failed!${reset}"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi