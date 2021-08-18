from abc import ABC
from abc import abstractmethod
from dataclasses import is_dataclass
from enum import Enum
from typing import List

from qq.plugins.jsonhack.encoders import DataclassEncoder
from qq.plugins.jsonhack.encoders import DateEncoder
from qq.plugins.jsonhack.encoders import DatetimeEncoder
from qq.plugins.jsonhack.encoders import DecimalEncoder
from qq.plugins.jsonhack.encoders import EnumEncoder
from qq.plugins.jsonhack.encoders import UUIDEncoder


class EncoderCreator(ABC):
    def __init__(self, customtype):
        self.customtype = customtype

    @abstractmethod
    def is_suitable(self):
        pass  # pragma: no cover

    @abstractmethod
    def create(self):
        pass  # pragma: no cover


class DataclassEncoderCreator(EncoderCreator):
    def is_suitable(self):
        return is_dataclass(self.customtype)

    def create(self):
        class ObjEncoder(DataclassEncoder):
            TYPE = self.customtype

        return ObjEncoder()


class CustomTypeEncoderCreator(EncoderCreator):
    base_encoders = (
        DatetimeEncoder,
        UUIDEncoder,
        DateEncoder,
        DecimalEncoder,
    )

    def __init__(self, customtype):
        super().__init__(customtype)
        self.base_encoder = None

    def is_suitable(self):
        for encoder in self.base_encoders:
            if issubclass(self.customtype, encoder().TYPE):
                self.base_encoder = encoder
                return True
        return False

    def create(self):
        class ObjEncoder(self.base_encoder):
            TYPE = self.customtype
            TYPENAME = self.customtype.__name__

        return ObjEncoder()


class EnumEncoderCreator(EncoderCreator):
    def is_suitable(self):
        return issubclass(self.customtype, Enum)

    def create(self):
        class ObjEncoder(EnumEncoder):
            TYPE = self.customtype
            TYPENAME = self.customtype.__name__

        return ObjEncoder()


def encoder_for(types: List[object]):
    creators = (
        DataclassEncoderCreator,
        CustomTypeEncoderCreator,
        EnumEncoderCreator,
    )
    for customtype in types:
        for creator in creators:
            creator = creator(customtype)
            if creator.is_suitable():
                yield creator.create()
