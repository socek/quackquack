from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture
from pytest import raises

from sapp.configurator import Configurator
from sapp.configurator import ConfiguratorNotStartedError
from sapp.context_manager import ContextManager
from sapp.decorators import Decorator
from sapp.plugin import Plugin


class ExamplePlugin(Plugin):
    def enter(self, context):
        context.example = sentinel.example
        context.example2 = sentinel.example2


class ExampleConfigurator(Configurator):
    def append_plugins(self):
        super().append_plugins()
        self.plugin1 = MagicMock()
        self.plugin2 = MagicMock()
        self.plugin3 = ExamplePlugin()

        self.add_plugin(self.plugin1)
        self.add_plugin(self.plugin2)
        self.add_plugin(self.plugin3)


class TestContextManager(object):
    @fixture
    def configurator(self):
        return ExampleConfigurator()

    def test_when_not_started(self, configurator):
        """
        Decorator should raise an error when it will be used without starting
        the configurator in the first place.
        """

        @Decorator(configurator)
        def method(ctx):
            pass

        with raises(ConfiguratorNotStartedError):
            method()

    def test_many_times(self, configurator):
        """
        Using configurator as decorator should enter and exit plugins only
        once.
        """
        configurator.start()

        @Decorator(configurator)
        def method1(ctx):
            pass

        @Decorator(configurator)
        def method2(ctx):
            method1()

        method2()

        configurator.plugin1.start.assert_called_once_with(configurator)
        configurator.plugin2.start.assert_called_once_with(configurator)

    def test_when_error_raised(self, configurator):
        """
        When using configurator as decorator and an exception is raised,
        all plugins should get that exception.
        """
        configurator.start()
        error = RuntimeError()

        @Decorator(configurator)
        def method(ctx):
            raise error

        with ContextManager(configurator) as ctx:
            with raises(RuntimeError):
                method()

        configurator.plugin1.exit.assert_called_once_with(ctx, None, None, None)
        configurator.plugin2.exit.assert_called_once_with(ctx, None, None, None)

    def test_when_using_argument(self, configurator):
        """
        When using configurator as decorator with an argument, it will pass
        proper object to the method.
        """
        configurator.start()

        @Decorator(configurator, "example")
        def method(example):
            assert example == sentinel.example

        method()

    def test_when_using_argument_as_list(self, configurator):
        """
        When using configurator as decorator with argument as list, it
        will pass proper objects to the method,
        """
        configurator.start()

        @Decorator(configurator, ["example"])
        def method(example):
            assert example == sentinel.example

        method()

    def test_when_wrong_argument_type(self, configurator):
        """
        When using configurator as decorator with wrong argument, it will
        raise AttributeError.
        """
        configurator.start()

        @Decorator(configurator, 1)
        def method(example):
            assert example == sentinel.example

        with raises(AttributeError):
            method()

    def test_usign_dependency_injection_for_ctx(self, configurator):
        """
        When using configurator as decorator, it should be able to make dependency
        injection using named vars.
        """
        configurator.start()

        @Decorator(configurator)
        def method(ctx):
            assert ctx == sentinel.ctx

        method(ctx=sentinel.ctx)

    def test_usign_dependency_injection(self, configurator):
        """
        When using configurator as decorator, it should be able to make dependency
        injection using named vars.
        """
        configurator.start()

        @Decorator(configurator, "example")
        def method(example):
            assert example == sentinel.injection

        method(example=sentinel.injection)

    def test_usign_dependency_injection_list(self, configurator):
        """
        When using configurator as decorator, it should be able to make dependency
        injection using named vars.
        """
        configurator.start()

        @Decorator(configurator, ["example"])
        def method(example):
            assert example == sentinel.injection

        method(example=sentinel.injection)
