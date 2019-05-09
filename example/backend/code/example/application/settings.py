from decouple import config


def logging(settings):
    settings["logging"] = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "generic": {
                "format": "%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "generic",
            }
        },
        "loggers": {
            "root": {"level": "DEBUG", "handlers": ["console"]},
            "sqlalchemy": {
                "level": "ERROR",
                "handlers": ["console"],
                "qualname": "sqlalchemy.engine",
            },
            "alembic": {
                "level": "ERROR",
                "handlers": ["console"],
                "qualname": "alembic",
            },
            "iep": {"level": "DEBUG", "handlers": ["console"], "qualname": "iep"},
            "celery": {"handlers": ["console"], "level": "ERROR"},
        },
    }


def database(settings):
    settings["db:dbsession:url"] = config("BACKEND_DB_URL")
    settings["db:dbsession:default_url"] = config("BACKEND_DB_DEFAULT_URL")


def celery_specific(settings):
    settings["celery"] = {"broker": config("BROKER_URL")}


def default():
    settings = {"main": "this is example main setting"}
    logging(settings)
    database(settings)
    celery_specific(settings)
    return settings


def wsgi_specific(settings):
    pass


def tests_specific(settings):
    pass


# --- Start points


def wsgi():
    settings = default()
    wsgi_specific(settings)
    return settings

def celery():
    settings = default()
    wsgi_specific(settings)
    return settings

def command():
    return default()


def tests():
    settings = default()
    wsgi_specific(settings)
    tests_specific(settings)
    return settings
