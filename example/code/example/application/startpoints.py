from example import app


def wsgi(settings):
    app.start("default")
    return app.make_wsgi_app()


def celery():
    app.start("default")
