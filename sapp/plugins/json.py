"""
This hack allows to encode uuid4 in json
"""
from json import JSONEncoder
from uuid import UUID

from pyramid.renderers import JSON
from sapp.plugin import Plugin


class JsonPlugin(Plugin):
    def start(self, configurator):
        default = JSONEncoder.default

        def new_default(newself, o):
            if isinstance(o, UUID):
                return o.hex
            return default(newself, o)

        JSONEncoder.default = new_default

    def start_pyramid(self, pyramid):
        json_renderer = JSON()
        json_renderer.add_adapter(UUID, self._to_string_adapter)
        pyramid.add_renderer("json", json_renderer)

    def _to_string_adapter(self, obj, request):
        if obj is not None:
            return obj.hex
