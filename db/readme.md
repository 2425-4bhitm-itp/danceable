# Development using a local docker compose database

## Starting

```bash
./start.sh
```

## delete all docker containers, images and volumes

```bash
./clean-docker.sh
```


## backup the database

```bash
docker exec -it postgres pg_dump -U demo
```

