from abc import ABC
from abc import abstractmethod
from dataclasses import is_dataclass
from importlib import import_module
from inspect import getmodule
from logging import getLogger
from pkgutil import walk_packages
from typing import List

from qq.types import CustomBaseType

logger = getLogger(__name__)


def is_defined_in(element, module):
    return getmodule(element).__name__ == module.__name__


class ObjectFinder(ABC):
    """
    This class is responsible for importing all modules in a project and search
    for specyfic objects.
    """

    process_cache = {}

    def __init__(
        self,
        parents: List[str],
        ignore_list: List[str] = None,
        cache_key: str = None,
    ):
        self.parents = parents
        self._cache_key = cache_key
        self.ignore_list = ignore_list or []

    @property
    def cache_key(self):
        return self._cache_key or self.__class__.__name__

    def find(self, force: bool = False):
        if force or self.cache_key not in self.process_cache:
            self.process_cache[self.cache_key] = self._find()
        return self.process_cache[self.cache_key]

    def _find(self):
        elements = []
        for parent in self.parents:
            info = f"{self.cache_key}: Searching for all objects in {parent}"
            logger.info(info)
            for package in self._get_all_packages(parent):
                elements += list(self._find_in_package(package))
        return elements

    def _get_all_packages(self, parent: str):
        try:
            parentpkg = import_module(parent)
        except Exception:
            logger.error(f"Can not import parent module: {parent}")
            return

        prefix = f"{parentpkg.__name__}."
        for module in walk_packages(parentpkg.__path__, prefix):
            if module.name in self.ignore_list:
                continue

            try:
                yield import_module(module.name)
            except Exception:
                logger.warning(f"Can not import module: {module.name}")
                continue

    def _find_in_package(self, package):
        intro = False
        for elementname in dir(package):
            element = getattr(package, elementname)

            if self.is_collectable(element) and is_defined_in(element, package):
                if not intro:
                    logger.debug(f"Module found: {package.__name__}")
                    intro = True
                logger.debug(f"\tObject found: {elementname}")
                yield element

    @abstractmethod
    def is_collectable(self, element: object):
        pass  # pragma: no cover


class DataclassFinder(ObjectFinder):
    def is_collectable(self, element: object):
        return is_dataclass(element)


class CustomBaseTypeFinder(ObjectFinder):
    def is_collectable(self, element: object):
        return issubclass(element, CustomBaseType)
