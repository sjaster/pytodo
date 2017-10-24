# Pytodo

## Description
Web Interface based on python and flask for managing tasks

---

## Deployment
Light Deployment with Docker and Docker-Compose

### Install Dependencies
For the deploy process you only need to packages installed on your system.

**docker** and **docker-compose**

Install them with the package manager of your choice.
```
$ pacman -S docker docker-compose
```

### Start Docker Engine
```
$ systemctl start docker.service
```

### Run Docker Container
```
$ cd pytodo
$ docker-compose up
```
Access through localhost:5000

---
### Database Migrations

If you want to alter the Database you can use the flask-migration package which is installed inside the Docker Container.

To run a migration on the database the following steps are required.

1. Change the Model Structure in `models.py` 
2. Find the ID of your docker container with `docker ps`
3. Run `docker exec <container-id> flask db migrate` to create a migration
4. Run `docker exec <container-id> flask db upgrde` to apply the migration on the database

---
## Project colorsheet based on materialize css colors

### Navbar

```
class="indigo darken-4"
```

### Buttons and clickable elements

```
class="teal lighten-1"
```

### FAB Subbuttons

#### Delete Button

```
class="red lighten-1"
```

#### Archive Button

```
class="yellow darken-1"
```

#### Edit Button

```
class="teal lighten-2"
```

