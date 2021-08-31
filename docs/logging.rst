Logging
=======

Logging is a very simple plugin. It uses ``logging.config.dictConfig`` from the
standard python's library. Plugin will just get the settings['logging'] value
and push it to the dictConfig. The logging will start when the Configurator
instance will be started.

Exapmle of the configuration:

.. code-block:: python

   def logging(settings):
       return {
           'version': 1,
           'disable_existing_loggers': True,
           'formatters': {
               'generic': {
                   'format':
                   '%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s',
               },
           },
           'handlers': {
               'console': {
                   'level': "DEBUG",
                   'class': 'logging.StreamHandler',
                   'formatter': 'generic',
               },
           },
           'loggers': {
               '': {
                   'level': 'DEBUG',
                   'handlers': [],
               },
               'sqlalchemy': {
                   'level': 'ERROR',
                   'handlers': ['console'],
                   'qualname': 'sqlalchemy.engine',
               },
               'alembic': {
                   'level': 'ERROR',
                   'handlers': ['console'],
                   'qualname': 'alembic',
               },
               'celery': {
                   'handlers': ['console'],
                   'level': 'ERROR',
               },
               'myapp': {
                   'level': 'DEBUG',
                   'handlers': ['console'],
                   'qualname': 'myapp',
               },
           }
       }

