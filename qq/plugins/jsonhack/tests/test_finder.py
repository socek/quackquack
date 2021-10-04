from dataclasses import dataclass
from unittest.mock import MagicMock

from pytest import fixture

from qq.finder import CustomBaseTypeFinder
from qq.finder import DataclassFinder
from qq.finder import ObjectFinder
from qq.types import CustomBaseType


@dataclass
class SimpleDataclass:
    pass


class CustomStr(str, CustomBaseType):
    pass


class FakeFinder(ObjectFinder):
    def is_collectable(self, element: object):
        return type(element) is str


class TestObjectFinder:
    @fixture
    def finder(self):
        return FakeFinder(["something"])

    @fixture
    def mmodule(self):
        mmodule = MagicMock()
        mmodule.__name__ = "something"
        mmodule.__path__ = ["/somewhere/something"]
        return mmodule

    @fixture
    def melement(self):
        return MagicMock()

    @fixture
    def mwalk_packages(self, mocker, mmodule):
        mock = mocker.patch("qq.finder.walk_packages")
        mock.return_value = [mmodule]
        return mock

    @fixture
    def mimport_module(self, mocker, mmodule):
        mimport_module = mocker.patch("qq.finder.import_module")
        mimport_module.return_value = mmodule
        return mimport_module

    @fixture
    def mis_defined_in(self, mocker):
        return mocker.patch("qq.finder.is_defined_in")

    @fixture
    def mfind(self, mocker, finder):
        return mocker.patch.object(finder, "_find")

    @fixture
    def mfind_in_package(self, mocker, finder, melement):
        mock = mocker.patch.object(finder, "_find_in_package")
        mock.return_value = [melement]
        return mock

    def test_find_when_no_cache(self, finder, mfind):
        """
        .find should do full find if cache is empty
        """
        finder.process_cache = {}

        assert finder.find() == mfind.return_value
        mfind.assert_called_once_with()

    def test_find_when_find_forced(self, finder, mfind):
        """
        .find should do full find if cache is empty
        """
        finder.process_cache = {finder.cache_key: "something"}

        assert finder.find(True) == mfind.return_value
        mfind.assert_called_once_with()

    def test_find_when_cache(self, finder, mfind):
        """
        .find should do full find if cache is empty
        """
        finder.process_cache = {finder.cache_key: "something"}

        assert finder.find() == "something"
        assert not mfind.called

    def test_find_raw_when_ok(
        self,
        finder,
        mwalk_packages,
        mimport_module,
        mfind_in_package,
        mmodule,
        melement,
    ):
        """
        ._find should walk thru all packages and find all elements in those packages
        """
        assert finder._find() == [melement]

    def test_find_raw_when_not_ok(
        self,
        finder,
        mwalk_packages,
        mimport_module,
        mfind_in_package,
        mmodule,
        melement,
    ):
        """
        ._find should ignore package which can not be imported
        """
        mimport_module.side_effect = RuntimeError()
        assert finder._find() == []

    def test_find_raw_when_ignored(
        self,
        finder,
        mwalk_packages,
        mimport_module,
        mfind_in_package,
        mmodule,
        melement,
    ):
        """
        ._find should ignore package which are in ignored list
        """
        finder.ignore_list = [mmodule.name]
        assert finder._find() == []

    def test_find_in_package(self, finder, mis_defined_in):
        package = MagicMock()
        package.__name__ = "something"
        package.two = "something2"
        assert list(finder._find_in_package(package)) == [
            "something",
            "something2",
        ]


class TestDataclassFinder:
    def test_is_collectable(self):
        """
        DataclassFinder.is_collectable should return True only if element is an dataclass
        """
        finder = DataclassFinder(["something"])
        assert finder.is_collectable(SimpleDataclass) is True
        assert finder.is_collectable(str) is False


class TestCustomBaseTypeFinder:
    def test_is_collectable(self):
        """
        CustomBaseTypeFinder.is_collectable should return True only if element is an dataclass
        """
        finder = CustomBaseTypeFinder(["something"])
        assert finder.is_collectable(CustomStr) is True
        assert finder.is_collectable(str) is False
