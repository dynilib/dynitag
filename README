Create db

```
dropdb audiolabeling 
createdb -O flask audiolabeling
```

Restart uwsgi after code changes

`docker exec annotator supervisorctl restart uwsgi`

DB init and migrations

```
docker exec -it annotator_demo flask db init
docker exec -it annotator_demo flask db migrate
docker exec -it annotator_demo flask db upgrade
```
