from example.application.capp import cel
from example.application.startpoints import celery

print("ELO1", cel)
import example.tasks

celery()


print("ELO2", cel)
