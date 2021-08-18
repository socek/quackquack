"""
This hack allows to encode uuid4, datetime and dataclases in json.
"""
from logging import getLogger
from typing import List

from pyramid.config import Configurator as PyramidConfigurator
from pyramid.renderers import JSON

from qq.application import Application
from qq.finder import ObjectFinder
from qq.plugin import Plugin
from qq.plugins.jsonhack.models import get_encoders
from qq.plugins.jsonhack.models import init_encoders
from qq.plugins.jsonhack.stubs import EncoderStub

logger = getLogger(__name__)


class JsonPlugin(Plugin):
    def __init__(
        self,
        stubs: List[EncoderStub],
        finders: List[ObjectFinder] = None,
    ):
        super().__init__()
        self.stubs = stubs
        self.finders = finders

    def start(self, application: Application):
        init_encoders(self.finders)
        for stub in self.stubs:
            stub.stub()

    def start_pyramid(self, pyramid: PyramidConfigurator):
        rendered = JSON()
        for encoder in get_encoders():
            rendered.add_adapter(
                encoder.TYPE, create_pyramid_json_adapter(encoder)
            )
        pyramid.add_renderer("json", rendered)


def create_pyramid_json_adapter(encoder):
    def encode(value, request):
        if encoder.is_encodable(value):
            return encoder.encode(value)

    return encode
