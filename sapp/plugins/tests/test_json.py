from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

from pytest import fixture

from sapp.plugins.json import JsonPlugin


class TestJsonPlugin(object):
    @fixture
    def configurator(self):
        return MagicMock()

    @fixture
    def pyramid(self):
        return MagicMock()

    @fixture
    def m_jsonencoder(self):
        with patch("sapp.plugins.json.JSONEncoder") as mock:
            yield mock

    @fixture
    def m_renderer(self):
        with patch("sapp.plugins.json.JSON") as mock:
            yield mock

    @fixture
    def plugin(self):
        return JsonPlugin()

    def test_start(self, plugin, configurator, m_jsonencoder):
        """
        .start should append uuid4 converter to json serializer.
        """
        old_default = m_jsonencoder.default
        plugin.start(configurator)

        uuid = uuid4()
        assert m_jsonencoder.default({}, uuid) == uuid.hex
        assert m_jsonencoder.default({}, "temp") == old_default.return_value

    def test_start_pyramid(self, plugin, pyramid, m_renderer):
        """
        .start_pyramid should append JSON renderer to pyramid's confiugration
        """
        plugin.start_pyramid(pyramid)
        pyramid.add_renderer("json", m_renderer.return_value)
        m_renderer.assert_called_once_with()
        m_renderer.return_value.add_adapter.assert_called_once_with(
            UUID, plugin._to_string_adapter
        )

    def test_to_string_adapter(self, plugin):
        assert plugin._to_string_adapter(None, None) is None
        uuid = uuid4()
        assert plugin._to_string_adapter(uuid, None) == uuid.hex
