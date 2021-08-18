from unittest.mock import MagicMock

from pytest import fixture


class PluginFixtures:
    @fixture
    def mconfigurator(self):
        return MagicMock()

    @fixture
    def mpyramid(self):
        return MagicMock()

    @fixture
    def mapplication(self):
        return MagicMock()
