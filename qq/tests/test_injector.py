from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture
from pytest import raises

from qq import ApplicationNotStartedError
from qq import Context
from qq import InjectApplicationContext
from qq import SimpleInjector
from qq.application import Application
from qq.injector import injectors
from qq.injector import is_injector_ready
from qq.plugins import SettingsPlugin


class TestSimpleInjector:
    RANDOM_KEY = "asduiwiuehiwuehq"

    @fixture
    def examplefun(self):
        @SimpleInjector
        def fun(settings):
            return settings

        return fun

    @fixture
    def mctx(self):
        return {self.RANDOM_KEY: sentinel.settings}

    def test_normal(self, examplefun, mctx):
        assert examplefun(mctx, self.RANDOM_KEY) == sentinel.settings


class TestIsInjectorReady:
    @fixture
    def mparameter(self):
        return MagicMock()

    @fixture
    def mbound_args(self):
        args = MagicMock()
        args.arguments = {}
        return args

    def test_when_parameter_is_not_an_injector(self, mparameter, mbound_args):
        mparameter._default = None

        assert is_injector_ready(mparameter, "key", mbound_args) is False

    def test_when_parameter_is_already_provided(self, mparameter, mbound_args):
        mbound_args.arguments["key"] = 1

        assert is_injector_ready(mparameter, "key", mbound_args) is False

    def test_when_parameter_is_not_provided(self, mparameter, mbound_args):
        assert is_injector_ready(mparameter, "key", mbound_args) is True


app = Application()


def example_fun(first, second, third=SimpleInjector(app, "key")):
    return [first, second, third]


class TestInjectors:
    def test_when_arguments_provided(self):
        assert list(injectors(example_fun, [1, 2, 3], {})) == []

    def test_when_arguments_not_provided(self):
        """
        When injector argument not provided, injectors fun should return this
        injector.
        """
        context = Context(Application())
        context.values["key"] = 333

        name, value = list(injectors(example_fun, [1, 2], {}))[0]

        assert name == "third"
        assert value(context, "key") == 333


def default_settings():
    return {"settings": True}


class ExampleApplication(Application):
    def append_plugins(self):
        self.plugins["settings"] = SettingsPlugin("qq.tests.test_injector")


class TestInjectApplicationContext:
    @fixture
    def app(self):
        return ExampleApplication()

    @fixture
    def fun(self, app):
        def example_fun(first, second, third=SimpleInjector(app, "settings")):
            return [first, second, third]

        return InjectApplicationContext(example_fun)

    def test_when_arguments_provided(self, fun):
        assert fun(1, 2, 3) == [1, 2, 3]

    def test_when_arguments_not_provided_and_app_not_started(self, fun):
        with raises(ApplicationNotStartedError):
            fun(1, 2)

    def test_when_arguments_not_provided_and_app_started(self, app, fun):
        app.start("default_settings")
        assert fun(1, 2) == [1, 2, {"settings": True}]
