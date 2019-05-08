from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture

from sapp.configurator import Configurator
from sapp.decorators import Decorator
from sapp.plugin import Plugin


class MockedPlugin(Plugin):
    def __init__(self, mocks=None):
        self.mocks = mocks or []

    def start(self, configurator):
        self.configurator = configurator
        for name in self.mocks:
            setattr(self.configurator, name, MagicMock())

    def enter(self, context):
        for name in self.mocks:
            value = getattr(self.configurator, name)
            setattr(context, name, value)


class SampleConfigurator(Configurator):
    def append_plugins(self):
        self.add_plugin(MockedPlugin(['var1', 'var2']))


class TestDecorator(object):
    @fixture
    def configurator(self):
        conf = SampleConfigurator()
        conf.start('tests')
        return conf

    def test_normal_context(self, configurator):
        """
        Decorator should append 'ctx' to the fun's arguments
        """
        @Decorator(configurator)
        def fun(ctx):
            assert ctx.var1 == configurator.var1
            assert ctx.var2 == configurator.var2

        fun()

    def test_with_specyfied_values_to_unpack(self, configurator):
        """
        Decorator should append values from ctx if specyfied.
        """
        @Decorator(configurator, ['var1', 'var2'])
        def fun(var1, var2):
            assert var1 == configurator.var1
            assert var2 == configurator.var2

        fun()

    def test_with_values_explicitly_passed(self, configurator):
        """
        Decorator should not append values from ctx if those values are
        passed thru as named argument specyfied.
        """
        @Decorator(configurator, ['var1', 'var2'])
        def fun(var1, var2):
            assert var1 == sentinel.var1
            assert var2 == configurator.var2

        fun(var1=sentinel.var1)
