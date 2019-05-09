from example import app
from example.thandlers import MainHandler
from example.thandlers import TaskHandler


def start():
    app.start("default")
    app.tornado.add_handlers(
        ".*", [(r"/", MainHandler, {}), (r"/task", TaskHandler, {})]
    )
    app.start_tornado_loop()


if __name__ == "__main__":
    start()
