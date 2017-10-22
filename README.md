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

## Project colorsheet based on materialize css colors

### Navbar

```
class="indigo darken-4"
```

### Buttons and clickable elements

```
class="teal lighten-1"
```


