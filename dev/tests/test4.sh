#!/bin/bash

# tests individual rolling snapshots

green="\e[32m"
red="\e[31m"
reset="\e[0m"

echo "this is some testing text" > file.txt
charon -f charon.test.yml apply test_4
echo  "more" >> file.txt
charon -f charon.test.yml apply test_4
echo  "more" >> file.txt
charon -f charon.test.yml apply test_4
echo  "more" >> file.txt
charon -f charon.test.yml apply test_4

expected_output="3"
real_output="$(RESTIC_PASSWORD=abcdefghijkl restic -r repo_4 snapshots --json | jq length)"

if [ "$real_output" == "$expected_output" ]; then
    echo -e "${green}test 4 passed!${reset}"
else
    echo -e "${red}test 4 failed!${reset}"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi

rm -r revert_output apply_output file.txt 2>/dev/null
rm -rf repo_4
