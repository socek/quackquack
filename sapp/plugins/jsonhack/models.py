"""
This hack allows to encode uuid4 and datetime in json
"""
from inspect import isabstract
from logging import getLogger

from sapp.plugins.jsonhack import encoders
from sapp.plugins.jsonhack.errors import UnknownObjectError

logger = getLogger(__name__)

ENCODERS_CACHE = []


def get_encoders():
    return ENCODERS_CACHE


def is_encoder(obj: object) -> bool:
    return issubclass(obj, encoders.Encoder) and not isabstract(obj)


def init_encoders(finder):
    """
    Get all encoders from sapp.plugins.jsonhack.encoders and from all dataclasses
    from the provided finder.
    """
    for name in dir(encoders):
        if name.startswith("_"):
            continue
        element = getattr(encoders, name)
        try:
            if is_encoder(element):
                ENCODERS_CACHE.append(element())
        except TypeError:
            continue

    if finder:
        # search for all dataclasses and generate encoder
        ENCODERS_CACHE.extend(encoders.encoder_for(finder.find()))


def object_hook(obj):
    if "_type" not in obj:
        return obj

    for encoder in get_encoders():
        if encoder.is_decodable(obj):
            return encoder.decode(obj)
    raise UnknownObjectError(obj)
