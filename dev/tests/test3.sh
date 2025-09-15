#!/bin/bash

# tests sqlite + encrypt

green="\e[32m"
red="\e[31m"
reset="\e[0m"

sqlite3 test3.db <<EOF

-- Create a table named 'users' with columns 'id', 'name', and 'age'
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
);

-- Insert some data into the 'users' table
INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 25), ('Charlie', 35);

EOF

charon -f charon.test.yml apply test_3
mkdir revert_output
charon -f charon.test.yml revert test_3 revert_output


expected_output='[
  {
    "type": "directory",
    "name": "revert_output",
    "contents": [
      {
        "type": "file",
        "name": "test3.db"
      }
    ]
  },
  {
    "type": "report",
    "directories": 1,
    "files": 1
  }
]
1|Alice|30
2|Bob|25
3|Charlie|35'

real_output="$(tree -J revert_output | jq)
$(sqlite3 revert_output/test3.db 'SELECT * FROM users;')"

if [ "$real_output" == "$expected_output" ]; then
    echo -e "${green}test 3 passed!${reset}"
else
    echo -e "${red}test 3 failed!${reset}"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi