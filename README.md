# charon

charon is a utility for automating data backups. charon uses [`restic`](https://restic.net/) for managing the backups.

# table of contents

- [installation](#installation)
- [usage](#usage)
- [configuration](#configuration)
  - [sources](#sources)
  - [repository](#repository)
  - [schedule](#schedule)
- [cli](#cli)
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

charon uses the `sched` library for scheduling tasks, which introduces some caveats:

- charon will exit when there are no more jobs to run. this is possible depending on the configuration
- all jobs are run on the same thread, sequentially
- the duration of the execution of a job can interfere with it's schedule. if a job misses a run due to the previous run still completing, the run is skipped and rescheduled at the next repetition

# configuration

configuration is given as a yaml file with the following structure:

```yml
jobs:
  my_job:
    source: # where data is coming from
      type: type_of_source
      # ...
    repository: # configuration for restic repository
      password: myresticpassword
      # ...
    schedule:# how often to run job
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
```

the data from the source will be backed up using `restic`. If the source is coming from somewhere external, like an http request, it will be cached in a temporary directory before being run through `restic`.

below are the possible ways you can configure the source object, based on the `type` key.

**local**

this pulls from a local file

```yml
source:
  type: local
  path: /path/to/data # path to data to back up. can be a file or a directory. does not use variable expansion
```

you can also instead include a list of paths. only one of `path` or `paths` should be included.
```yml
source:
  type: local
  paths: 
   - /path/to/data1
   - /path/to/data2
```

If using a single path, charon will use a relative path. For example, `path: /path/to/data` will only backup and restore `data`. Using `paths` (e.g. `paths: [/path/to/data]`) will keep the full directory structure.

**http**

performs an http request, and saves the response body to a file

```yml
source:
  type: http
  url: http://example.com/ # url to make request to
  method: get # optional, request method, defaults to get
  ext: json # optional, extension to use for saved file, defaults to txt
  auth: # optional, authentication configuration
    bearer: eyJhbGc... # optional, bearer token
  transform: # optional, list of transforms to perform on the response body
    - jq: .[] + 1 # uses the jq library to run `jq.compile(<PATTERN>).input_text(<PAYLOAD>).first()`
```

you can also make multiple requests and save the results to multiple files

```yml
source:
  type: http
  targets:
    com: # will be saved to com.json
      url: http://example.com/ # url to make request to
      method: get # optional, request method, defaults to get
      ext: json # optional, extension to use for saved file, defaults to txt
      auth: # optional, authentication configuration
        bearer: eyJhbGc... # optional, bearer token
    uk: # will be saved to uk.zip
      url: http://example.co.uk/
      ext: zip
```

`url` and `targets` can both be provided, but at least one _must_ be provided.

**sqlite**

performs a backup on an sqlite3 db

```yml
source:
  type: sqlite
  db_path: /path/to/db_file.db
```

## repository

the `repository` section is for configuring the `restic` repository.

```yml
repository:
  password: my-restic-password # password for repository
  create: false # optional, whether or not charon should create the repository if it doesn't exist. default is true
  max_snapshots: 3 # optional, prune old snapshots to keep this amount or fewer snapshots in the repository
  backend: # configuration for the restic backend
    type: local # determines how to interpret the backend config
```

below are the possible ways you can configure the `repository.backend` object, based on the `type` key.

**local**

this pushes to a local directory

```yml
backend:
  type: local
  path: ./foo/bar # must be a directory
```

**gcs_bucket**

uploads to a google cloud storage bucket

```yml
backend:
  type: gcs_bucket
  bucket: 9e4376a1-a0ce-4ff4-a67b-8af4a54d15c1-foo # bucket name
  credentials: ./credentials.json # path to credentials file for service account with access to bucket
  path: /path/to/repo # path to repository inside bucket
```

**rclone**

uses rclone as a target.

the `backend.rclone_config` object will be used to configure rclone. each key in that map will be configured to an environment variable named `f'{RCLONE_CONFIG_{job.upper()}_{key.upper()}'}`. for example, the config `jobs.myjob.backend.rclone_config.host: myhost.com` would be converted to `RCLONE_CONFIG_MYJOB_HOST=myhost.com`.

> [!NOTE]
> the password needs to be stored in its obscured form, **charon will not obscure the password for you**. you can obscure your password using `rclone obscure`

```yml
backend:
  type: rclone
  path: path/to/repo # path within rclone target for repository
  rclone_config: # configuration to pass through to rclone env vars
    type: ftp
    host: my-host.com
    user: my-username
    pass: ... # obscured password
    port: 21
    explicit_tls: "true"
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

**timeout**

optionally, you can specify a job timeout. if the job (both the fetch and the upload) do not complete within the timeout, the job will be cancelled.

```yml
schedule:
  every: 1d
  timeout: 15m
```

# cli

charon provides a cli for manual work. the `apply` command can be used to run a job once, immediately.

```bash
charon apply MY_JOB
```

charon can also run the job in reverse, pulling it from the destination and dumping it to a given directory

```bash
charon revert MY_JOB OUTPUT_DIRECTORY
```

you can specify the config file before running either command

```bash
charon -f MY_CONFIG.yml apply MY_JOB
```

see tests for more examples.

## tests

each `test*.sh` file will run some commands (must be run inside the tests folder, with a python environment set up for charon), and has a comment in the file detailing the expected output.

```bash
cd dev
make docker-build
make run-tests
```
