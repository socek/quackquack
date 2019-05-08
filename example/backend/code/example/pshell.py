from example import app


def setup(env):
    env["app"] = app
    env["ctx"] = app._enter_context()
