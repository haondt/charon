# charon

charon is a utility for backing up data from one location to another at regular intervals.

# table of contents

- [installation](#installation)
- [usage](#usage)
- [configuration](#configuration)
    - [sources](#sources)
    - [destinations](#destinations)
    - [schedule](#schedule)
- [styx](#styx)
- [tests](#tests)

# installation

charon can be installed as a docker image

```bash
# from docker hub
docker pull haumea/charon
# from gitlab
docker pull registry.gitlab.com/haondt/cicd/registry/charon:latest
```

see `docker-compose.yml` for a sample docker compose setup.

charon can also be installed as a python package

```bash
# from pypi
pip install haondt-charon
# from gitlab
pip install haondt-charon --index-url https://gitlab.com/api/v4/projects/57154225/packages/pypi/simple
```

# usage

start charon with:

```bash
# if installed as a python package, or if running from source
python3 -m charon
# the pypi package also includes a standlone binary
charon
# from the docker image
docker run --rm -it -v ./charon.yml:/config/charon.yml registry.gitlab.com/haondt/cicd/registry/charon:latest
```

charon will look for a config file at `charon.yml`. a different path can be specified with:

```bash
charon -f MY_CONFIG.yml
```

charon uses the `sched` library for scheduling tasks, meaning charon will exit when there are no more tasks to run. this is possible depending on the configuration.

# configuration

configuration is given as a yaml file with the following structure:

```yml
# NOTE: to use gcp buckets, charon must be run in an environment where GOOGLE_APPLICATION_CREDENTIALS exists
gcp_buckets: # optional, configuration for gcp buckets
    my_bucket:
        bucket: 1234-name-of-my-bucket-in-gcp

jobs:
    my_job:
        source: # where data is coming from
            type: type_of_source
            # ...
        destination: # where data is going
            type: type_of_destination
            # ...
        schedule: # how often to run job
            # ...
    my_job_2:
        # ...
```

see `charon.yml` for an example config.

## sources

all sources will have a few shared fields:

```yaml
source:
    type: local # determines how to interpret the source config
    encrypt: 4B71... # optional, 32 byte hex-encoded encryption key

```

the data from the source will be archived in a gz'd tar file. if an encryption key is provided, the tar file will then be encrypted.


below are the possible ways you can configure the source object, based on the `type` key.

**local**

this pulls from a local file

```yml
source:
    type: local
    path: /path/to/data # path to data to back up. can be a file or a directory. does not use variable expansion

```

**http**

performs an http request, and saves the response body to a file

```yml
source:
    type: http
    url: http://example.com/ # url to make request to
    method: get # optional, request method, defaults to get
    ext: json # optional, extension to use for saved file, defaults to txt
    auth:  # optional, authentication configuration
        bearer: eyJhbGc... # optional, bearer token
```

## destinations

all destinations will also have some shared fields

```yml
destination:
    type: local # determines how to interpret the destination config
    name: my_output # the name of the output file, can include path seperators (foo/bar)
```

**note**: the name of the file (where applicable) in the destination will be `destination.name` + a file extension determined by the source.

bewlow are the possible ways you can configure the destination object, based on the `type` key.

**local**

this pushes to a local file

```yml
destination:
    type: local
    path: ./foo # must be a directory, file will be created inside this dir
    overwrite: false # optional, whether or not to overwrite an existing output file. defaults to false
```

**gcp_bucket**

uploads to a google cloud storage bucket. requires `gcp_buckets` to be configured, and `GOOGLE_APPLICATION_CREDENTIALS` envrionment variable.


```yml
destination:
    type: gcp_bucket
    config: my-bucket # name of config in gcp_buckets:
```

## schedule

how often the program is run. there are a few different ways to configure the schedule

**cron**

the schedule can be configured using a cron string.

note: this program uses [croniter](https://github.com/kiorky/croniter) for scheduling with the cron format. Croniter accepts seconds, but they must be at the _end_ (right hand side) of the cron string.

```yml
schedule:
    cron: "* * * * * */10" # every 10 seconds
```

**one shot**

this runs once, after the given delay. the delay is given in the `1d2h3m4s` format. numbers must be integers.

```yml
schedule:
    after: 1d # wait 1 day, then run once
```

**intervals**

this runs at regular intervals, using the one shot format, starting from the time charon is run. 

```yml
schedule:
    every: 1h30m # run every hour and a half
```

**combinations**

you can combine schedules, for example to run immediately, and then every other day

```yml
schedule:
    after: 0s
    every: 2d
```

# styx

charon includes a subcommand, `styx`, that will run a job once, immediately.

```bash
charon styx apply MY_JOB
```

styx can also run the job in reverse, pulling it from the destination and dumping it to a given directory

```bash
charon styx revert MY_JOB OUTPUT_DIRECTORY
```

you can specify the config file before calling styx

```bash
charon -f MY_CONFIG.yml styx apply MY_JOB
```

see tests for more examples.

# tests

each `test*.sh` file will run some commands (must be run inside the tests folder, with a python environment set up for charon), and has a comment in the file detailing the expected output. 

```bash
cd tests
./test.sh
./test2.sh
...
```
