# Pytodo

## Description
Web Interface based on python and flask for managing tasks

---

## Development
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

You can either run through a single docker container or through docker-compose.

### Build Docker Container

```
$ cd pytodo
$ docker build -t pytodo .
```

### Run Docker Container
```
$ docker run -p 5001:5001 -v /pathtodb:/pytodo/db/ pytodo
```
Access through localhost:5001

**Important Note:** The Database is not inside the docker container. You have to mount it on the docker run process as an extra volume.

### Run Docker Compose

```
$ docker-compose up
```

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

### Card Background Colors

```
class="blue-grey"
```
