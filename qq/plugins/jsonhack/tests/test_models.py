import json
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
from enum import Enum
from unittest.mock import MagicMock
from uuid import UUID
from uuid import uuid4

from pytest import fixture
from pytest import raises

from qq.plugins.jsonhack.encodergenerators import encoder_for
from qq.plugins.jsonhack.encoders import DateEncoder
from qq.plugins.jsonhack.encoders import DatetimeEncoder
from qq.plugins.jsonhack.encoders import DecimalEncoder
from qq.plugins.jsonhack.encoders import UUIDEncoder
from qq.plugins.jsonhack.errors import UnknownObjectError
from qq.plugins.jsonhack.models import ENCODERS_CACHE
from qq.plugins.jsonhack.models import add_encoder
from qq.plugins.jsonhack.models import init_encoders
from qq.plugins.jsonhack.models import object_hook
from qq.plugins.jsonhack.stubs import DecoderStub
from qq.plugins.jsonhack.stubs import EncoderStub
from qq.types import CustomBaseType


class CustomUuid(UUID, CustomBaseType):
    pass


class SampleEnum(Enum):
    FIRST = "first"
    SECOND = "second"


@dataclass
class SampleDataclass:
    name: str
    year: int


data = {
    "0": 0,
    "1": datetime.now(),
    "2": uuid4(),
    "3": date.today(),
    "4": Decimal("3.14"),
    "5": SampleDataclass(name="first", year=2019),
    "6": CustomUuid(uuid4().hex),
    "7": SampleEnum("first"),
    "nested": {
        "n0": 0,
        "n1": datetime.now(),
        "n2": uuid4(),
        "n3": date.today(),
        "n4": Decimal("6.14"),
        "n5": SampleDataclass(name="second", year=2020),
        "n6": CustomUuid(uuid4().hex),
        "n7": SampleEnum("second"),
    },
}


class FakeClass:
    pass


class TestEncodingJson:
    @fixture(autouse=True)
    def stub(self):
        encoder_stub = EncoderStub(json.JSONEncoder, "default")
        decoder_stub = DecoderStub(json.JSONDecoder, "decode")
        add_encoder(DatetimeEncoder())
        add_encoder(DateEncoder())
        add_encoder(UUIDEncoder())
        add_encoder(DecimalEncoder())
        for encoder in encoder_for([SampleDataclass, CustomUuid, SampleEnum]):
            add_encoder(encoder)

        encoder_stub.stub()
        decoder_stub.stub()
        yield
        encoder_stub.unstub()
        decoder_stub.unstub()
        ENCODERS_CACHE.clear()

    def test_normal(self):
        result = json.loads(json.dumps(data))

        assert data == result

    def test_failed_encoding(self):
        newdata = FakeClass()

        with raises(TypeError):
            json.loads(json.dumps(newdata))


class TestObjectHook:
    @fixture
    def mget_encoders(self, mocker, mencoder):
        mock = mocker.patch("qq.plugins.jsonhack.models.get_encoders")
        mock.return_value = [mencoder]
        return mock

    @fixture
    def mencoder(self):
        return MagicMock()

    @fixture
    def data(self):
        return {"_type": "something", "value": "here"}

    def test_when_normal_type(self, data):
        """
        object_hook should do nothing if the object to decode has no "_type" in
        keys
        """
        del data["_type"]
        assert object_hook(data) == data

    def test_when_encoded(self, mencoder, data, mget_encoders):
        """
        object_hook should decode the object if the encoder is found
        """
        assert object_hook(data) == mencoder.decode.return_value
        mencoder.decode.assert_called_once_with(data)
        mencoder.is_decodable.assert_called_once_with(data)

    def test_when_unknow_type(self, data, mget_encoders):
        """
        object_hook should raise an error if the encoder for the object is not found
        """
        mget_encoders.return_value = []
        with raises(UnknownObjectError):
            object_hook(data)


class TestInitEncoders:
    @fixture
    def finder(self):
        return MagicMock()

    @fixture(autouse=True)
    def clear_encoders(self):
        yield
        ENCODERS_CACHE.clear()

    def test_parse_encoders(self):
        init_encoders([])

        assert len(ENCODERS_CACHE) is not 0

    def test_with_finders(self, finder):
        init_encoders([finder])

        finder.find.return_value = [CustomUuid]

        init_encoders([finder])

        # I know this is strange, but I did not know how to test this behaviour
        # better
        for enc in ENCODERS_CACHE:
            if enc.TYPE == CustomUuid:
                assert True
                return

        assert False
