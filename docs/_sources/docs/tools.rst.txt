*****
Tools
*****

This section provide documentation for some small classes and functions that
comes along with the Quack Quack framework.

Finders (ObjectFinder, DataclassFinder, CustomBaseTypeFinder)
=============================================================

This class is designed in order to auto import all the needed objects. This is
very helpful, for example, when you need to import all the dataclasses used in
project in order to make serialization, but you don't want to write the
configuration file. Finders will do that automaticly.

.. note::
    All automatic import mechanism have a downside: if the import will not be
    successful, then the mechanism needs to ignore this file. In order to
    mitigate this problem Finders logs everything, so please remember to configure
    the `qq.finder` logger for yourself.


ObjectFinder
------------

This class was created for searching objects across all needed packages.

.. code-block:: python

    from abc import ABC

    class ObjectFinder(ABC):
        def __init__(
            self,
            parents: List[str],
            ignore_list: List[str] = None,
            cache_key: str = None,
        ):

In order to crete an ObjectFinder you need to give list of packages in str
`parents: List[str]` where to search for the objects. You can add some ignore
list.

.. code-block:: python

    finder = ObjectFinder(["mypackage"], ["mypackage.notthis"])
    objects = finder.find()

Finders are cached by default, so if you wish to recreate the cache, just add
True to the method.

.. code-block:: python

    finder.find(force=True)


DataclassFinder
---------------

This finder will search for all the dataclasses in the project. It is used by
the `JsonPlugin` for finding all the objects that can be serialized.

CustomBaseTypeFinder
--------------------

This finder will search for all the CustomBaseType's in the project. It is used
by the `JsonPlugin` for finding all the objects that can be serialized.


Creating custom Finder
----------------------

Creating custom finder is very simple. You need to inherit from ObjectFinder and
overwrite the `is_collectable` method. This method return True if the object
which was found is the one we are looking for.

.. code-block:: python

    class StrFinder(ObjectFinder):
        def is_collectable(self, element: object):
            return isinstance(element, str)


    class DataclassFinder(ObjectFinder):
        def is_collectable(self, element: object):
            return is_dataclass(element)


    class CustomBaseTypeFinder(ObjectFinder):
        def is_collectable(self, element: object):
            return issubclass(element, CustomBaseType)

