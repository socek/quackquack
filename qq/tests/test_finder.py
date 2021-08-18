from unittest.mock import MagicMock
from unittest.mock import call

from pytest import fixture

from qq import application
from qq.application import Application
from qq.finder import ObjectFinder
from qq.finder import is_defined_in


class TestIsDefinedIn:
    def test_when_true(self):
        assert is_defined_in(Application, application)

    def test_when_false(self):
        assert is_defined_in(is_defined_in, application) is False


class SampleFinder(ObjectFinder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_cache = {}

    def is_collectable(self, element):
        return getattr(element, "is_collectable") or False


class TestObjectFinder:
    @fixture
    def finder(self):
        return SampleFinder(["parent.one", "parent.two"], ["parent.one.arg1"])

    @fixture
    def mfind(self, mocker, finder):
        return mocker.patch.object(finder, "_find")

    @fixture
    def mget_all_packages(self, mocker, finder):
        return mocker.patch.object(finder, "_get_all_packages")

    @fixture
    def mfind_in_package(self, mocker, finder):
        return mocker.patch.object(finder, "_find_in_package")

    @fixture
    def mimport_module(self, mocker):
        return mocker.patch("qq.finder.import_module")

    @fixture
    def mwalk_packages(self, mocker):
        return mocker.patch("qq.finder.walk_packages")

    @fixture
    def module(self, mwalk_packages):
        module = MagicMock()
        mwalk_packages.return_value = [module]
        return module

    def test_find_when_cache_not_exists(self, finder, mfind):
        """
        .find should start find procedure if the cache for this class is not
        exsiting.
        """
        assert finder.find() == mfind.return_value
        mfind.assert_called_once_with()

    def test_find_when_cache_exists(self, finder, mfind):
        """
        .find should not start find procedure if the cache for this class is not
        exsiting.
        """
        finder.process_cache[finder.cache_key] = 123
        assert finder.find() == 123
        assert not mfind.called

    def test_find(self, finder, mget_all_packages, mfind_in_package):
        """
        ._find should get all packages and list add all elements from there.
        """
        mget_all_packages.return_value = [1]
        mfind_in_package.return_value = [2]

        assert finder._find() == [2, 2]

    def test_get_all_packages_when_import_failed(
        self, finder, mimport_module, mwalk_packages
    ):
        """
        ._get_all_packages should skip if import failed
        """
        mimport_module.side_effect = RuntimeError()

        list(finder._get_all_packages("parent"))

        mimport_module.assert_called_once_with(
            "parent",
        )
        assert not mwalk_packages.called

    def test_get_all_packages_when_module_in_ignore_list(
        self, finder, mimport_module, mwalk_packages, module
    ):
        """
        ._get_all_packages should skip if module in ignore list
        """
        module.name = "parent.one.arg1"
        mimport_module.return_value.__name__ = "prefixpkg"
        mimport_module.return_value.__path__ = "prefixpkg"

        list(finder._get_all_packages("parent"))

        mimport_module.assert_called_once_with(
            "parent",
        )
        mwalk_packages.assert_called_once_with("prefixpkg", "prefixpkg.")

    def test_get_all_packages_when_module_import_failed(
        self, finder, mimport_module, mwalk_packages, module
    ):
        """
        ._get_all_packages should skip packages that failed to import
        """
        module.name = "parent.one"
        parent = MagicMock()
        mimport_module.side_effect = [parent, RuntimeError()]
        parent.__name__ = "prefixpkg"
        parent.__path__ = "prefixpkg"

        list(finder._get_all_packages("parent"))

        mwalk_packages.assert_called_once_with("prefixpkg", "prefixpkg.")
        assert mimport_module.call_args_list == [
            call("parent"),
            call("parent.one"),
        ]

    def test_get_all_packages_when_module_import_success(
        self, finder, mimport_module, mwalk_packages, module
    ):
        """
        ._get_all_packages should return list of all collected modules
        """
        module.name = "parent.one"
        parent = MagicMock()
        child = MagicMock()
        mimport_module.side_effect = [parent, child]
        parent.__name__ = "prefixpkg"
        parent.__path__ = "prefixpkg"

        assert list(finder._get_all_packages("parent")) == [child]

        mwalk_packages.assert_called_once_with("prefixpkg", "prefixpkg.")
        assert mimport_module.call_args_list == [
            call("parent"),
            call("parent.one"),
        ]
