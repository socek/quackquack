"""
This module provide tests for the main functionality of the Quack Quack.
"""

from pytest import raises

from qq import Application
from qq import Context
from qq.errors import ApplicationNotStartedError
from qq.injectors import ContextInicjator
from qq.injectors import SetApplication
from qq.injectors import SetInicjator
from qq.plugin import Plugin
from qq.plugins import SettingsPlugin
from qq.plugins.types import Settings


class SamplePlugin(Plugin):
    key = "first"

    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def start(self, application: Application):
        return {
            "data": self.value,
        }

    def enter(self, context: Context):
        return context.globals[self.key]


class SecondSamplePlugin(Plugin):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def start(self, application: Application):
        return {
            "data": self.value,
        }

    def enter(self, context: Context):
        return context.globals[self.key]


class MyApplication(Application):
    def create_plugins(self):
        self.plugins(SamplePlugin("one"))
        self.plugins["second"] = SecondSamplePlugin("two")


application = MyApplication()
application.start()


def test_normal_function():
    @SetApplication(application)
    @SetInicjator("first", ContextInicjator("first"))
    @SetInicjator("second", ContextInicjator("second"))
    def mytest(first, second):
        return first, second

    assert mytest() == ({"data": "one"}, {"data": "two"})


async def test_async_function():
    @SetApplication(application)
    @SetInicjator("first", ContextInicjator("first"))
    @SetInicjator("second", ContextInicjator("second"))
    async def mytest(first, second):
        return first, second

    assert await mytest() == ({"data": "one"}, {"data": "two"})


def test_set_only_application():
    @SetApplication(application)
    def mytest():
        return "one"

    assert mytest() == "one"


def test_set_only_inicjator():
    @SetInicjator("first", ContextInicjator("first"))
    def mytest():
        return "one"

    with raises(ApplicationNotStartedError):
        mytest()


def test_error_function():
    @SetApplication(application)
    @SetInicjator("first", ContextInicjator("first"))
    def mytest(first):
        raise RuntimeError("X")

    with raises(RuntimeError):
        mytest()


def test_dependency_injection():
    @SetApplication(application)
    @SetInicjator("first", ContextInicjator("first"))
    @SetInicjator("second", ContextInicjator("second"))
    def mytest(first, second):
        return first, second

    assert mytest("one", "two") == ("one", "two")


def test_dependency_injection_kwargs():
    @SetApplication(application)
    @SetInicjator("first", ContextInicjator("first"))
    @SetInicjator("second", ContextInicjator("second"))
    def mytest(first, second):
        return first, second

    assert mytest(second="two", first="one") == ("one", "two")


def test_repr():
    def mytest():
        pass

    assert repr(SetApplication(application)(mytest)) == repr(mytest)
