import json
from dataclasses import dataclass

from qq.plugins.jsonhack.models import get_encoders
from qq.plugins.jsonhack.models import object_hook


@dataclass(init=False)
class EncoderStub:
    obj: object
    param_name: str
    default: object

    def __init__(self, obj: object, param_name: str):
        self.obj = obj
        self.param_name = param_name
        self.default = getattr(obj, param_name)

    def _get_function(self):
        def encoder(selfsecond, o):
            for encoder in get_encoders():
                if encoder.is_encodable(o):
                    return encoder.encode(o)
            return self.default(selfsecond, o)

        return encoder

    def stub(self):
        setattr(self.obj, self.param_name, self._get_function())

    def unstub(self):
        setattr(self.obj, self.param_name, self.default)


@dataclass(init=False)
class DecoderStub(EncoderStub):
    def _get_function(self):
        def decoder(selfsecond, *args, **kwargs):
            selfsecond.object_hook = object_hook
            selfsecond.scan_once = json.scanner.make_scanner(selfsecond)
            return self.default(selfsecond, *args, **kwargs)

        return decoder
