from qq.plugins.jsonhack.encoders import Encoder


class MyInt(int):
    ENCODED_TYPENAME = "something"


class SampleEncoder(Encoder):
    TYPE = MyInt

    def _encode(self, value):
        pass  # pragma: no cover

    def _decode(self, value):
        pass  # pragma: no cover)


class TestEncoder:
    def test_typename(self):
        """
        .TYPENAME should return ENCODED_TYPENAME from .TYPE
        """
        SampleEncoder.TYPE = MyInt

        assert SampleEncoder().TYPENAME == "something"

    def test_typename2(self):
        """
        .TYPENAME should return __name__ from TYPE class
        """
        SampleEncoder.TYPE = int

        assert SampleEncoder().TYPENAME == "int"
