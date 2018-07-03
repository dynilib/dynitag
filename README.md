Dynitag is a web-based collaborative audio annotator tool, heavily based on https://github.com/CrowdCurio/audio-annotator.

# Install

## Clone repository

`$ git clone https://github.com/dynilib/dynitag.git`

## Go to repository root and create directories to be mounted as docker volumes

```
$ cd dynitag
$ mkdir -p data/db data/upload
```

## Run postgres container

```
$ docker run --name dynitag_db -v $(pwd)/data/db:/var/lib/postgresql/data/pgdata \
-e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=dynitag_db \
-e PGDATA=/var/lib/postgresql/data/pgdata -d postgres
```

## Build and run dynitag container (and link to dynitag_db postgres container)

```
$ docker build -t dynitag web
$ docker run -d --name dynitag --link dynitag_db:dynitag_db -p 8000:80 \
-v $(pwd)/web/dynitag:/myapp -v $(pwd)/data/upload:/upload dynitag
```

## Create database (check [flask-migrate](https://github.com/miguelgrinberg/Flask-Migrate) for details)

```
$ docker exec dynitag flask db init
$ docker exec dynitag flask db migrate
$ docker exec dynitag flask db upgrade
```

## create admin user (default password is specified in web/dynitag/instance/filldb.py)

`$ docker exec dynitag python instance/filldb.py`


# Create and use test project

An annotation project consists in:
* a set of files to be annotated
* a set of labels to annotate files

1 - Login as admin at http://127.0.0.1:8000/admin/

2 - Create a project at http://127.0.0.1:8000/admin/project/, with the following values:

* Name: test
* Audio Root Url: http://127.0.0.1:8000/static/audio/test
* Allow Regions: Yes (tick the checkbox)
* Number of annotations per file: 2 (every file must be annotated by 2 users)
* Audios Filename: audios.txt
* Annotations Filename: labels.csv

with

**audios.txt** (flies found in http://127.0.0.1:8000/static/audio/test)
```
ID0043.wav
ID0047.wav
ID0049.wav
ID0052.wav
ID0057.wav
ID0058.wav
ID0059.wav
```

**labels.csv** (Some random label examples)
```
Bird species, crow
Bird species, warbler
Bird species, other
Proximity, close
Proximity, medium
Proximity, far
```

3 - You can now start annotating your files by selecting the *test* project at http://127.0.0.1:8000/projects.

4 - Once the project is completed, the annotations can be downloaded as json data at http://127.0.0.1:8000/admin/






