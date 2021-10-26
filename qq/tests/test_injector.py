from unittest.mock import MagicMock

from pytest import fixture
from pytest import raises

from qq import ApplicationNotStartedError
from qq import Context
from qq import InjectApplication
from qq import SimpleInjector
from qq.application import Application
from qq.errors import InjectorNotInicialized
from qq.injector import QQ_PARAMETER
from qq.injector import Injector
from qq.injector import get_injectors
from qq.injector import get_runners
from qq.injector import injector_runner
from qq.injector import is_injector_ready
from qq.plugins import SettingsPlugin


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
        assert is_injector_ready(mparameter, "key", mbound_args) is False

    def test_when_parameter_is_already_provided(self, mparameter, mbound_args):
        mbound_args.arguments["key"] = 1
        mparameter._default = Injector(None)

        assert is_injector_ready(mparameter, "key", mbound_args) is False

    def test_when_parameter_is_not_provided(self, mparameter, mbound_args):
        mparameter._default = Injector(None)
        result = is_injector_ready(mparameter, "key", mbound_args)
        assert result is True


app = Application()


def not_injected_fun():
    pass


injected_fun = InjectApplication(None)(not_injected_fun)


def example_fun(
    first, second, third=SimpleInjector(app, "key"), fourth=injected_fun
):
    return [first, second, third, fourth]


class TestInjectors:
    def test_when_arguments_provided(self):
        assert list(get_injectors(example_fun, [1, 2, 3, 4], {})) == []

    def test_when_arguments_not_provided(self):
        """
        When injector argument not provided, injectors fun should return this
        injector.
        """
        context = Context(Application())
        context.values["key"] = 333

        name, value = list(get_injectors(example_fun, [1, 2], {}))[0]

        assert name == "third"
        assert value(context, "key") != value


class TestInjectedApplication:
    def test_when_arguments_provided(self):
        assert list(get_runners(example_fun, [1, 2, 3, 4], {})) == []

    def test_when_arguments_not_provided(self):
        """
        When injector argument not provided, injectors fun should return this
        injector.
        """
        context = Context(Application())
        context.values["key"] = 333

        name, value = list(get_runners(example_fun, [1, 2], {}))[0]

        assert name == "fourth"
        assert value == injected_fun


def default_settings():
    return {"settings": True}


class ExampleApplication(Application):
    def create_plugins(self):
        self.plugins["settings"] = SettingsPlugin("qq.tests.test_injector")


class TestInitializeInjectors:
    @fixture
    def app(self):
        return ExampleApplication()

    @fixture
    def fun(self, app):
        def example_fun(
            first, second, third=SimpleInjector("settings"), fourth=injected_fun
        ):
            return [first, second, third, fourth]

        return InjectApplication(app)(example_fun)

    @fixture
    def errorfun(self, app):
        def example_fun(
            first, second, third=SimpleInjector, fourth=injected_fun
        ):
            return [first, second, third, fourth]

        return InjectApplication(app)(example_fun)

    def test_when_arguments_provided(self, fun):
        assert fun(1, 2, 3, 4) == [1, 2, 3, 4]

    def test_when_arguments_not_provided_and_app_not_started(self, fun):
        with raises(ApplicationNotStartedError):
            fun(1, 2)

    def test_when_arguments_not_provided_and_app_started(self, app, fun):
        app.start("default_settings")
        result = fun(1, 2)
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == {"settings": True}
        assert getattr(result[3], QQ_PARAMETER) == app

    def test_swap_application(self, fun):
        secondfun = injector_runner(fun, None)
        assert getattr(secondfun, QQ_PARAMETER) is None

    def test_when_not_initialized(self, app, errorfun):
        """
        Injected function should raise InjectorNotInicialized error when
        the Injector is wrongly used.
        """
        app.start("default_settings")
        with raises(InjectorNotInicialized):
            errorfun(1, 2)
