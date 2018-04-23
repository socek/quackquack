from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import fixture

from sapp.plugins.pyramid.routing import Routing


class ExampleView(object):
    renderer = 'myrenderer'
    path_info = None


class TestRouting(object):
    @fixture
    def mconfig(self):
        return MagicMock()

    @fixture
    def routing(self, mconfig):
        return Routing(mconfig)

    @fixture
    def madd(self, routing):
        patcher = patch.object(routing, 'add')
        with patcher as mock:
            yield mock

    @fixture
    def madd_view(self, routing):
        patcher = patch.object(routing, 'add_view')
        with patcher as mock:
            yield mock

    @fixture
    def mread_from_file(self, routing):
        patcher = patch.object(routing, 'read_from_file')
        with patcher as mock:
            yield mock

    def test_add(self, routing, mconfig, madd_view):
        routing.add('view', 'route', 'url', 'arg', kw='arg')

        mconfig.add_route('route', 'url', 'arg', kw='arg')
        madd_view.assert_called_once_with('view', route_name='route')

    def test_add_view(self, routing, mconfig):
        mconfig.maybe_dotted.return_value = ExampleView
        routing.add_view(
            'impaf.tests.test_routing.ExampleView',
            route_name='something',
        )

        mconfig.add_view(
            'impaf.tests.test_routing.ExampleView',
            route_name='something',
            renderer='myrenderer',
        )
