# CS3103 Assignment 4

## How to Run the Project

### Prerequisites
- Docker installed on your machine

### Starting the container
1. Navigate to the project directory, build the container:
```bash
docker compose build
```

### Start and monitor the container
- start container:
```bash
docker compose up -d receiver
```

- monitor container:
```bash
docker compose logs -f receiver
```

- run client:
```bash
docker compose run --rm sender
```
or
```bash
docker compose run --rm sender-slow
```

### Checking
- check for correct network conditions
```bash
docker compose exec sender-slow sh -c 'tc -s qdisc show dev eth0'
```

### Clean up
- end all containers, remove-orphans is optional
```bash
docker compose down --remove-orphans
```

### Others
- Checking container
```bash
docker ps -a
```
