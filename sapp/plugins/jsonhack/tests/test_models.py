import json
from datetime import date
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from pytest import fixture
from pytest import raises

from sapp.plugins.jsonhack.errors import UnknownObjectError
from sapp.plugins.jsonhack.models import object_hook
from sapp.plugins.jsonhack.stubs import DecoderStub
from sapp.plugins.jsonhack.stubs import EncoderStub

data = {
    "0": 0,
    "1": datetime.now(),
    "2": uuid4(),
    "3": date.today(),
    "nested": {
        "n0": 0,
        "n1": datetime.now(),
        "n2": uuid4(),
        "n3": date.today(),
    },
}


class FakeClass:
    pass


class TestEncodingJson:
    @fixture(autouse=True)
    def stub(self):
        encoder_stub = EncoderStub(json.JSONEncoder, "default")
        decoder_stub = DecoderStub(json.JSONDecoder, "decode")
        encoder_stub.stub()
        decoder_stub.stub()
        yield
        encoder_stub.unstub()
        decoder_stub.unstub()

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
        mock = mocker.patch("sapp.plugins.jsonhack.models.get_encoders")
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
