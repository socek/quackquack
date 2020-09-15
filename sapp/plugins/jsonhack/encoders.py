from abc import ABC
from abc import abstractmethod
from datetime import date
from datetime import datetime
from typing import List
from uuid import UUID

from dateutil import parser
from marshmallow_dataclass import class_schema


class Encoder(ABC):
    _TYPENAME_PREFIX = "Appnexus"

    @property
    @abstractmethod
    def TYPE(self):
        pass  # pragma: no cover

    @property
    def TYPENAME(self):
        return self._TYPENAME_PREFIX + self.TYPE.__name__

    def is_encodable(self, value):
        return type(value) == self.TYPE

    def is_decodable(self, obj):
        return obj.get("_type") == self.TYPENAME

    def encode(self, value):
        return {"_type": self.TYPENAME, "value": self._encode(value)}

    def decode(self, obj):
        return self._decode(obj["value"])

    @abstractmethod
    def _encode(self, value):
        pass  # pragma: no cover

    @abstractmethod
    def _decode(self, value):
        pass  # pragma: no cover


class DatetimeEncoder(Encoder):
    TYPENAME = "datetime"
    TYPE = datetime

    def _encode(self, value):
        return value.isoformat()

    def _decode(self, value):
        return parser.parse(value)


class UUIDEncoder(Encoder):
    TYPENAME = "UUID"
    TYPE = UUID

    def _encode(self, value):
        return value.hex

    def _decode(self, value):
        return UUID(value)


class DateEncoder(Encoder):
    TYPENAME = "date"
    TYPE = date

    def _encode(self, value):
        return value.isoformat()

    def _decode(self, value):
        return parser.parse(value).date()


class DataclassEncoder(Encoder):
    def _get_schema(self):
        return class_schema(self.TYPE)()

    def _encode(self, obj):
        schema = self._get_schema()
        return schema.dump(obj)

    def _decode(self, data):
        schema = self._get_schema()
        return schema.load(data)


def encoder_for(dataclasses: List[object]):
    for dataclass in dataclasses:

        class Encoder(DataclassEncoder):
            TYPE = dataclass

        yield Encoder()
