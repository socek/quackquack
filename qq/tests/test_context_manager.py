from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import fixture
from pytest import raises

from qq.application import Application
from qq.context import ApplicationNotStartedError
from qq.context import Context
from qq.plugin import Plugin


class ExamplePlugin(Plugin):
    def enter(self, context):
        return {"one": sentinel.example, "two": sentinel.example2}


class ExampleApplication(Application):
    def create_plugins(self):
        super().create_plugins()
        self.plugins["plugin1"] = MagicMock(key=None)
        self.plugins["plugin2"] = MagicMock(key=None)
        self.plugins["plugin3"] = ExamplePlugin()


class TestContext:
    @fixture
    def app(self):
        return ExampleApplication()

    def test_when_not_started(self, app):
        """
        Application should raise an error when it will be used without starting
        it in the first place.
        """
        with raises(ApplicationNotStartedError):
            with Context(app):
                pass

    def test_context_names(self, app):
        """
        context.names() should return list of all vars in the context.
        """
        app.start()

        with Context(app) as context:
            assert (
                context["plugin1"] == app.plugins["plugin1"].enter.return_value
            )
            assert (
                context["plugin2"] == app.plugins["plugin2"].enter.return_value
            )
            assert context["plugin3"] == {
                "one": sentinel.example,
                "two": sentinel.example2,
            }

    def test_many_times(self, app):
        """
        Using app as context manager should enter and exit plugins only
        once.
        """
        app.start()

        with Context(app) as context1:
            with Context(app) as context2:
                assert not app.plugins["plugin1"].enter.called
                assert not app.plugins["plugin2"].enter.called

                assert context1["plugin1"] == context2["plugin1"]

        app.plugins["plugin1"].exit.assert_called_once_with(
            context1, None, None, None
        )
        assert not app.plugins["plugin2"].exit.called

    def test_when_error_raised(self, app):
        """
        When using app as context manager and an exception is raised,
        all plugins should get that exception.
        """
        app.start()
        error = RuntimeError()

        with raises(RuntimeError):
            with Context(app) as context:
                context["plugin1"]
                raise error

        app.plugins["plugin1"].start.assert_called_once_with(app)
        app.plugins["plugin2"].start.assert_called_once_with(app)

        call = app.plugins["plugin1"].exit.call_args_list[0][0]
        assert call[0] == context
        assert call[1] == RuntimeError
        assert call[2] == error
        assert call[3] is not None

        assert not app.plugins["plugin2"].exit.called

    def test_extra(self, app):
        app.start(kw=1)

        with Context(app) as ctx:
            assert ctx.extra == {"kw": 1}
