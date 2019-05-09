# Sapp Example

This little project shows example project that can be implemented using sapp.
This project contains integration with Pyramid, Tornado, Celery and Sqlalchemy.
All these frameworks can share common settings module.

# How to start

Requiretments:

- docker
- docker-compose

```bash
 $ docker-compose build
 $ docker-compose up -d
```

# How to use

There are two webservers:

- pyramid on port 8000
- tornado on port 8001

There are couple of endpoints, which you can use:

- http://localhost:8000/

    Show all data saved by the other endpoints.

- http://localhost:8000/create

    Create new data using pyramid.

- http://localhost:8000/task

    Create new data using celery worker.

- http://localhost:8001/

    Create new data using tornado.

- http://localhost:8001/task

    Create new data using celery worker.
