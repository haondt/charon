#!/bin/bash

# tests individual files + encryption

export PYTHONPATH="../"
echo "this is some testing text" > first_file.txt
python3 -m charon -f charon.test.yml styx apply test_1
mkdir revert_output
python3 -m charon -f charon.test.yml styx revert test_1 revert_output


expected_output="revert_output
└── first_file.txt

0 directories, 1 file
this is some testing text"

real_output="$(tree revert_output)
$(cat revert_output/first_file.txt)"

if [ "$real_output" == "$expected_output" ]; then
    echo "test passed!"
else
    echo "test failed!"
    diff -y <(echo "$expected_output") <(echo "$real_output")
fi

rm -r revert_output apply_output first_file.txt 2>/dev/null
