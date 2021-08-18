from unittest.mock import MagicMock

from pytest import fixture

from qq.plugins.jsonhack.plugin import JsonPlugin
from qq.plugins.jsonhack.plugin import create_pyramid_json_adapter


class TestJsonPlugin:
    @fixture
    def mstub(self):
        return MagicMock()

    @fixture
    def mencoder(self):
        return MagicMock()

    @fixture
    def mpyramid(self):
        return MagicMock()

    @fixture
    def mget_encoders(self, mocker, mencoder):
        mock = mocker.patch("qq.plugins.jsonhack.plugin.get_encoders")
        mock.return_value = [mencoder]
        return mock

    @fixture
    def mcreate_pyramid_json_adapter(self, mocker):
        return mocker.patch("qq.plugins.jsonhack.plugin.create_pyramid_json_adapter")

    @fixture
    def mjson(self, mocker):
        return mocker.patch("qq.plugins.jsonhack.plugin.JSON")

    @fixture
    def plugin(self, mstub):
        return JsonPlugin([mstub])

    def test_start(self, plugin, mstub):
        """
        .start should start all stubs.
        """
        plugin.start(None)
        mstub.stub.assert_called_once_with()

    def test_start_pyramid(self, plugin, mget_encoders, mcreate_pyramid_json_adapter, mpyramid, mjson, mencoder):
        """
        .start_pyramid should create adapter from every encovder
        """
        plugin.start_pyramid(mpyramid)
        mpyramid.add_renderer.assert_called_once_with("json", mjson.return_value)
        mjson.return_value.add_adapter.assert_called_once_with(mencoder.TYPE, mcreate_pyramid_json_adapter.return_value)
        mcreate_pyramid_json_adapter.assert_called_once_with(mencoder)


class TestCreatePyramidJsonEncoder:
    @fixture
    def mencoder(self):
        return MagicMock()

    def test_create_pyramid_json_adapter_when_encoded(self, mencoder):
        """
        pyramid encoder works differently then normal encoders: encoder should
        return value only if the value can be encoded
        """
        mencoder.is_encodable.return_value = True

        pencoder = create_pyramid_json_adapter(mencoder)
        assert pencoder("x", None) == mencoder.encode.return_value
        mencoder.encode.assert_called_once_with("x")

    def test_create_pyramid_json_adapter_when_not_encoded(self, mencoder):
        """
        pyramid encoder works differently then normal encoders: encoder should
        return value only if the value can be encoded
        """
        mencoder.is_encodable.return_value = False

        pencoder = create_pyramid_json_adapter(mencoder)
        assert pencoder("x", None) is None
        assert not mencoder.encode.called
