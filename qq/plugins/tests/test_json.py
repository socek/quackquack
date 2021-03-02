from unittest.mock import MagicMock

from pytest import fixture

from qq.plugins.jsonhack.plugin import JsonPlugin


class TestJsonPlugin:
    @fixture
    def configurator(self):
        return MagicMock()

    @fixture
    def pyramid(self):
        return MagicMock()

    @fixture
    def stub(self):
        return MagicMock()

    @fixture
    def finder(self):
        return MagicMock()

    @fixture
    def minit_encoders(self, mocker, finder):
        return mocker.patch("qq.plugins.jsonhack.plugin.init_encoders")

    @fixture
    def mget_encoders(self, mocker):
        return mocker.patch("qq.plugins.jsonhack.plugin.get_encoders")

    @fixture
    def mrenderer(self, mocker):
        return mocker.patch("qq.plugins.jsonhack.plugin.JSON")

    @fixture
    def mcreate_pyramid_json_adapter(self, mocker):
        return mocker.patch("qq.plugins.jsonhack.plugin.create_pyramid_json_adapter")

    @fixture
    def plugin(self, stub, finder):
        return JsonPlugin([stub], finder)

    def test_start(self, plugin, configurator, minit_encoders, stub, finder):
        """
        .start should start all stubs
        """
        plugin.start(configurator)

        minit_encoders.assert_called_once_with(finder)
        stub.stub.assert_called_once_with()

    def test_start_pyramid(self, plugin, pyramid, mget_encoders, mrenderer, mcreate_pyramid_json_adapter):
        """
        .start_pyramid should append JSON renderer to pyramid's confiugration
        """
        encoder = MagicMock()
        encoder.is_encodable.return_value = True
        mget_encoders.return_value = [encoder]
        plugin.start_pyramid(pyramid)

        mrenderer.assert_called_once_with()
        mrenderer.return_value.add_adapter(encoder.TYPE, mcreate_pyramid_json_adapter.return_value)
        mcreate_pyramid_json_adapter.assert_called_once_with(encoder)
