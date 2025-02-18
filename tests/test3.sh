#!/bin/bash

# tests sqlite + encrypt

green="\e[32m"
red="\e[31m"
reset="\e[0m"

export PYTHONPATH="../"

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

python3 -m charon -f charon.test.yml apply test_3
mkdir revert_output
python3 -m charon -f charon.test.yml revert test_3 revert_output

expected_output="revert_output
└── test3.db

0 directories, 1 file
1|Alice|30
2|Bob|25
3|Charlie|35"
real_output="$(tree revert_output)
$(sqlite3 revert_output/test3.db 'SELECT * FROM users;')"

if [ "$real_output" == "$expected_output" ]; then
    echo -e "${green}test passed!${reset}"
else
    echo -e "${red}test failed!${reset}"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi

rm -r revert_output test_3_output_dest test3.db 2>/dev/null
rm -rf repo_3
