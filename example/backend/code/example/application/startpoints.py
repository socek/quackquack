from example import app


def wsgi(settings):
    app.start("wsgi")
    return app.make_wsgi_object()
