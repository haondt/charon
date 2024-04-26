# charon


Note: this program uses [croniter](https://github.com/kiorky/croniter) for scheduling with the cron format. Croniter accepts seconds, but they must be at the _end_ (right hand side) of the cron string.

# usage

```bash
python3 charon.py
```

config file is `charon.yml` by default, but can be specified

```bash
python3 charon.py -f MY_CONFIG.yml
```


includes a command line utility, `styx`, that will apply a single job once, immediately, in either the direction of uploading it to the destination,

```bash
python3 charon.py styx apply MY_JOB
```

or in reverse, pulling it from the destination and dumping it to a given directory

```bash
python3 charon.py styx revert MY_JOB OUTPUT_DIRECTORY
```

you can specify the config file before calling styx

```bash
python3 charon.py -f MY_CONFIG.yml styx apply MY_JOB
```

see tests for more examples.

# running tests

```bash
cd tests
```

each `test*.sh` file will run some commands (must be run inside the tests folder, with a python environment set up for charon), and has a comment in the file detailing the expected output. 

# configuration

TODO
