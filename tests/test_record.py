# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import pytest
import _test_record_base

from ndef.record import Record
from io import BytesIO

valid_record_types = [
    ('urn:nfc:wkt:XYZ',              1, b'XYZ'),
    ('urn:nfc:wkt:xyz',              1, b'xyz'),
    ('application/octet-stream',     2, b'application/octet-stream'),
    ('http://example.com/type.dtd',  3, b'http://example.com/type.dtd'),
    ('urn:nfc:ext:example.com:type', 4, b'example.com:type'),
    ('unknown',                      5, b''),
    ('unchanged',                    6, b''),
]

wrong_record_types = [
    (int(), "record type string may be str or bytes, but not int"),
    ('invalid', "can not convert the record type string 'invalid'"),
    ('text/', "can not convert the record type string 'text/'"),
    ('urn:', "can not convert the record type string 'urn:'"),
    ('urn:nfc:', "can not convert the record type string 'urn:nfc:'"),
    ('urn:nfc:wkt', "can not convert the record type string 'urn:nfc:wkt'"),
    ('http:', "can not convert the record type string 'http:'"),
    ('http:/', "can not convert the record type string 'http:/'"),
    ('http:/a.b', "can not convert the record type string 'http:/a.b'"),
    ('urn:nfc:wkt:'+256*'a',"an NDEF Record TYPE can not be more than 255 octet"),
]

class TestDecodeType:
    @pytest.mark.parametrize("record_type, TNF, TYPE", valid_record_types)
    def test_pass(self, record_type, TNF, TYPE):
        assert Record._decode_type(TNF, TYPE) == record_type
        assert type(Record._decode_type(TNF, TYPE)) == str

    def test_fail(self):
        errstr = "ndef.record.Record NDEF Record TNF values must be 0 to 6"
        with pytest.raises((TypeError, ValueError)) as excinfo:
            Record._decode_type(7, b'')
        assert str(excinfo.value) == errstr

class TestEncodeType:
    @pytest.mark.parametrize("record_type, TNF, TYPE", valid_record_types)
    def test_pass(self, record_type, TNF, TYPE):
        assert Record._encode_type(record_type) == (TNF, TYPE)
        assert type(Record._encode_type(record_type)[1]) == bytes

    @pytest.mark.parametrize("record_type, errstr", wrong_record_types)
    def test_fail(self, record_type, errstr):
        with pytest.raises((TypeError, ValueError)) as excinfo:
            Record._encode_type(record_type)
        assert str(excinfo.value) == "ndef.record.Record " + errstr

valid_init_args = [
    ((),                           '', '', b''),
    ((None,),                      '', '', b''),
    ((None, None),                 '', '', b''),
    ((None, None, None),           '', '', b''),
    ((str(), None, None),          '', '', b''),
    ((bytes(), None, None),        '', '', b''),
    ((bytearray(), None, None),    '', '', b''),
    ((None, str(), None),          '', '', b''),
    ((None, bytes(), None),        '', '', b''),
    ((None, bytearray(), None),    '', '', b''),
    ((None, None, str()),          '', '', b''),
    ((None, None, bytes()),        '', '', b''),
    ((None, None, bytearray()),    '', '', b''),
    (('text/plain', None, None),   'text/plain', '', b''),
    (('text/plain', 'id', None),   'text/plain', 'id', b''),
    (('text/plain', 'id', 'text'), 'text/plain', 'id', b'text'),
    (('text/plain', None, 'text'), 'text/plain', '', b'text'),
    ((None, 'id', 'text'),         '', 'id', b'text'),
    ((None, 'id', None),           '', 'id', b''),
    (('a/'+253*'a', None, None),   'a/'+253*'a', '', b''),
    ((None, 255*'a', None),        '', 255*'a', b''),
]

wrong_init_args = [
    ((int(),), " record type string may be str or bytes, but not int"),
    (('ab',), " can not convert the record type string 'ab'"),
    (('', int()), ".name may be str or None, but not int"),
    (('', 256*'a'), ".name can not be more than 255 octets NDEF Record ID"),
    (('', '', int()), ".data may be sequence or None, but not int"),
]
class TestInitArguments:
    @pytest.mark.parametrize("args, _type, _name, _data", valid_init_args)
    def test_pass(self, args, _type, _name, _data):
        record = Record(*args)
        assert record.type == _type
        assert record.name == _name
        assert record.data == _data

    @pytest.mark.parametrize("args, errstr", wrong_init_args)
    def test_fail(self, args, errstr):
        with pytest.raises((TypeError, ValueError)) as excinfo:
            Record(*args)
        assert str(excinfo.value) == "ndef.record.Record" + errstr

class TestInitKeywords:
    def test_pass(self):
        record_1 = Record(type='text/plain', name='name', data='hello')
        record_2 = Record(b'text/plain', b'name', b'hello')
        assert record_1.type == record_2.type
        assert record_1.name == record_2.name
        assert record_1.data == record_2.data

    def test_fail(self):
        with pytest.raises(TypeError) as excinfo:
            Record(undefined_keyword='abc')

class TestTypeAttribute:
    def test_instance(self):
        assert isinstance(Record().type, str)

    def test_update(self):
        with pytest.raises(AttributeError) as excinfo:
            Record().type = ''

class TestNameAttribute:
    def test_instance(self):
        assert isinstance(Record().name, str)

    def test_update(self):
        record = Record()
        assert record.name == ''
        record.name = 255 * 'a'
        assert record.name == 255 * 'a'
        with pytest.raises(TypeError):
            record.name = 1
        with pytest.raises(ValueError):
            record.name = 256 * 'a'

class TestDataAttribute:
    def test_instance(self):
        assert isinstance(Record().data, bytearray)

    def test_update(self):
        record = Record('unknown', '', 'abc')
        assert record.data == b'abc'
        record.data.extend(b'def')
        assert record.data == b'abcdef'
        with pytest.raises(AttributeError):
            Record().data = bytearray(b'')

class TestStringFormat:
    format_args_data = [
        (('', '', ''), "'', '', bytearray(b'')"),
        (('unknown', 'id', 'data'), "'unknown', 'id', bytearray(b'data')"),
    ]
    format_str_data = [
        (('', '', ''),
         "TYPE '' ID '' PAYLOAD 0 byte"),
        (('text/plain', '', ''),
         "TYPE 'text/plain' ID '' PAYLOAD 0 byte"),
        (('text/plain', 'id', ''),
         "TYPE 'text/plain' ID 'id' PAYLOAD 0 byte"),
        (('text/plain', 'id', '\x00\x01'),
         "TYPE 'text/plain' ID 'id' PAYLOAD 2 byte '0001'"),
        (('text/plain', '', '0123456789'),
         "TYPE 'text/plain' ID '' PAYLOAD 10 byte '30313233343536373839'"),
        (('text/plain', '', '012345678901'),
         "TYPE 'text/plain' ID '' PAYLOAD 12 byte '30313233343536373839' ... 2 more"),
    ]
    @pytest.mark.parametrize("args, string", format_args_data)
    def test_format_args(self, args, string):
        assert "{:args}".format(Record(*args)) == string

    @pytest.mark.parametrize("args, string", format_args_data)
    def test_format_repr(self, args, string):
        string = "ndef.record.Record({})".format(string)
        assert "{!r}".format(Record(*args)) == string

    @pytest.mark.parametrize("args, string", format_str_data)
    def test_format_str(self, args, string):
        assert "{!s}".format(Record(*args)) == "NDEF Record " + string
        assert "{}".format(Record(*args)) ==  "NDEF Record " + string

class TestCompare:
    compare_data = [
        ('', '', ''),
        ('a/b', '', ''),
        ('', 'abc', ''),
        ('', '', 'abc'),
    ]
    @pytest.mark.parametrize("args", compare_data)
    def test_equal(self, args):
        assert Record(*args) == Record(*args)

    @pytest.mark.parametrize("args1,args2",zip(compare_data, compare_data[1:]))
    def test_noteq(self, args1, args2):
        assert Record(*args1) != Record(*args2)

class TestEncode:
    valid_encode_data = [
        (('', '', b''), '100000'),
        (('urn:nfc:wkt:X', '', b''), '110100 58'),
        (('text/plain', '', b''), '120a00 746578742f706c61696e'),
        (('http://a.b/c', '', b''), '130c00 687474703a2f2f612e622f63'),
        (('urn:nfc:ext:a.com:type', '', b''), '140A00 612e636f6d3a74797065'),
        (('unknown', '', b''), '150000'),
        (('unchanged', '', b''), '160000'),
        (('urn:nfc:wkt:X', 'id', b''), '19010002 586964'),
        (('urn:nfc:wkt:X', 'id', b'payload'), '19010702 5869647061796c6f6164'),
        (('urn:nfc:wkt:X', 'id', 256*b'p'), '09010000010002 586964'+256*'70'),
    ]
    @pytest.mark.parametrize("args, encoded", valid_encode_data)
    def test_pass(self, args, encoded):
        stream = BytesIO()
        record = Record(*args)
        octets = bytearray.fromhex(encoded)
        assert record._encode(stream=stream) == len(octets)
        assert stream.getvalue() == octets

    def test_limit(self):
        stream = BytesIO()
        record = Record('unknown', '', 0x100000 * b'\0')
        octets = bytearray.fromhex('050000100000') + 0x100000 * b'\0'
        assert record._encode(stream=stream) == len(octets)
        assert stream.getvalue() == octets        
        record = Record('unknown', '', 0x100001 * b'\0')
        errstr = "payload of more than 1048576 octets can not be encoded"
        with pytest.raises(ndef.EncodeError) as excinfo:
            record._encode(stream=stream)
        assert str(excinfo.value) == 'ndef.record.Record ' + errstr

    valid_struct_data = [
        ("B", (1,), "01"),
        ("BB", (1, 2), "0102"),
        ("BB*", (1, 2, b'123'), "0102313233"),
        ("BB+", (1, b'123'), "0102313233"),
    ]
    @pytest.mark.parametrize("fmt, values, octets", valid_struct_data)
    def test_struct_pass(self, fmt, values, octets):
        octets = bytearray.fromhex(octets)
        assert Record._encode_struct(fmt, *values) == octets

    wrong_struct_data = [
        ("B", (1000,), "ubyte format requires 0 <= number <= 255"),
        ("+", (b'123',), "pack expected 0 items for packing (got 1)"),
    ]
    @pytest.mark.parametrize("fmt, values, errstr", wrong_struct_data)
    def test_struct_pass(self, fmt, values, errstr):
        with pytest.raises(ndef.EncodeError) as excinfo:
            Record._encode_struct(fmt, *values)
        assert str(excinfo.value) == 'ndef.record.Record ' + errstr

    def test_derived_record(self):
        class MyRecord(Record):
            _type = 'urn:nfc:wkt:x'
            def __init__(self): pass
            def _encode_payload(self): return b'\0'

        stream = BytesIO()
        octets = bytearray.fromhex('1101017800')
        assert MyRecord()._encode(stream=stream) == len(octets)
        assert stream.getvalue() == octets
        
class TestDecode:
    valid_decode_data = TestEncode.valid_encode_data + [
        (('', '', b''), '00 00 00 00 00 00'),
        (('', '', b''), '00 00 00 00 00 00 00'),
    ]
    wrong_decode_data = [
        ('07', "TNF field value must be between 0 and 6"),
        ('00', "buffer underflow at reading length fields"),
        ('0000', "buffer underflow at reading length fields"),
        ('000000', "buffer underflow at reading length fields"),
        ('00000000', "buffer underflow at reading length fields"),
        ('0000000000', "buffer underflow at reading length fields"),
        ('10010000', "TYPE_LENGTH must be 0 for TNF value 0"),
        ('110000', "TYPE_LENGTH must be > 0 for TNF value 1"),
        ('120000', "TYPE_LENGTH must be > 0 for TNF value 2"),
        ('130000', "TYPE_LENGTH must be > 0 for TNF value 3"),
        ('140000', "TYPE_LENGTH must be > 0 for TNF value 4"),
        ('15010000', "TYPE_LENGTH must be 0 for TNF value 5"),
        ('16010000', "TYPE_LENGTH must be 0 for TNF value 6"),
        ('1800000100', "ID_LENGTH must be 0 for TNF value 0"),
        ('10000100', "PAYLOAD_LENGTH must be 0 for TNF value 0"),
        ('000000000001', "PAYLOAD_LENGTH must be 0 for TNF value 0"),
        ('19010101', "buffer underflow at reading TYPE field"),
        ('1901010154', "buffer underflow at reading ID field"),
        ('190101015449', "buffer underflow at reading PAYLOAD field"),
    ]
    valid_flag_data = [
        ('000000000000', 0, 0, 0),
        ('800000000000', 1, 0, 0),
        ('400000000000', 0, 1, 0),
        ('200000000000', 0, 0, 1),
        ('c00000000000', 1, 1, 0),
        ('a00000000000', 1, 0, 1),
        ('e00000000000', 1, 1, 1),
    ]
    @pytest.mark.parametrize("args, encoded", valid_decode_data)
    def test_pass(self, args, encoded):
        stream = BytesIO(bytearray.fromhex(encoded))
        record = Record._decode(stream, 'strict', {})[0]
        assert record == Record(*args)

    @pytest.mark.parametrize("encoded, errstr", wrong_decode_data)
    def test_fail(self, encoded, errstr):
        with pytest.raises(ndef.DecodeError) as excinfo:
            stream = BytesIO(bytearray.fromhex(encoded))
            Record._decode(stream, 'strict', {})
        assert errstr in str(excinfo.value)

    @pytest.mark.parametrize("encoded, _mb, _me, _cf", valid_flag_data)
    def test_flags(self, encoded, _mb, _me, _cf):
        stream = BytesIO(bytearray.fromhex(encoded))
        record, mb, me, cf = Record._decode(stream, 'strict', {})
        assert mb == _mb
        assert me == _me
        assert cf == _cf

    def test_limit(self):
        octets = bytearray.fromhex('')
        record = Record._decode(BytesIO(octets), 'strict', {})[0]
        assert record is None
        octets = bytearray.fromhex('050000100000') + 0x100000 * b'\0'
        record = Record._decode(BytesIO(octets), 'strict', {})[0]
        assert len(record.data) == 0x100000
        errstr = "payload of more than 1048576 octets can not be decoded"
        octets = bytearray.fromhex('050000100001') + 0x100001 * b'\0'
        with pytest.raises(ndef.DecodeError) as excinfo:
            Record._decode(BytesIO(octets), 'strict', {})
        assert str(excinfo.value) == 'ndef.record.Record ' + errstr

    def test_decode_payload_is_not_implemented(self):
        errstr = "must implement the _decode_payload() method"
        with pytest.raises(NotImplementedError) as excinfo:
            Record._decode_payload(b'', 'strict')
        assert str(excinfo.value) == 'ndef.record.Record ' + errstr

    def test_decode_known_type(self):
        class MyRecord(Record):
            _type = 'urn:nfc:wkt:x'
            _decode_min_payload_length = 1
            _decode_max_payload_length = 1
            @classmethod
            def _decode_payload(cls, octets, errors): return MyRecord()

        known_types = {MyRecord._type: MyRecord}
        stream = BytesIO(bytearray.fromhex('1101017800'))
        record = Record._decode(stream, 'strict', known_types)[0]
        assert type(record) == MyRecord
        
        errstr = 'payload length can not be less than 1'
        stream = BytesIO(bytearray.fromhex('11010078'))
        with pytest.raises(ndef.DecodeError) as excinfo:
            Record._decode(stream, 'strict', known_types)
        assert str(excinfo.value) == 'test_record.MyRecord ' + errstr

        errstr = 'payload length can not be more than 1'
        stream = BytesIO(bytearray.fromhex('110102780000'))
        with pytest.raises(ndef.DecodeError) as excinfo:
            Record._decode(stream, 'strict', known_types)
        assert str(excinfo.value) == 'test_record.MyRecord ' + errstr

    valid_struct_data = [
        ("B", "01", 0, 1),
        ("BB", "0102", 0, (1, 2)),
        ("BB*", "0102313233", 0, (1, 2, b'123')),
        ("BB+", "0102313233", 0, (1, b'12')),
        ("BB+", "000102313233", 1, (1, b'12')),
    ]
    @pytest.mark.parametrize("fmt, octets, offset, values", valid_struct_data)
    def test_struct_pass(self, fmt, octets, offset, values):
        octets = bytearray.fromhex(octets)
        assert Record._decode_struct(fmt, octets, offset) == values

    wrong_struct_data = [
        ("H", "01", 0, "unpack_from requires a buffer of at least 2 bytes"),
        ("B+", "04313233", 0, "need 1 more octet to unpack format 'B+'"),
    ]
    @pytest.mark.parametrize("fmt, octets, offset, errstr", wrong_struct_data)
    def test_struct_pass(self, fmt, octets, offset, errstr):
        octets = bytearray.fromhex(octets)
        with pytest.raises(ndef.DecodeError) as excinfo:
            Record._decode_struct(fmt, octets, offset)
        assert str(excinfo.value) == 'ndef.record.Record ' + errstr

class TestValueToAscii:
    pass_values = [
        'abc', u'abc', b'abc', bytearray(b'abc')
    ]
    fail_values = [
        (int(), "accepts str or bytes, but not int"),
        ('\x80', "conversion requires ascii text, but got '\\x80'"),
    ]

    @pytest.mark.parametrize("value", pass_values)
    def test_pass(self, value):
        assert Record._value_to_ascii(value, 'value') == 'abc'

    @pytest.mark.parametrize("value, errstr", fail_values)
    def test_fail(self, value, errstr):
        with pytest.raises((TypeError, ValueError)) as excinfo:
            Record._value_to_ascii(value, 'value')
        assert str(excinfo.value) == "ndef.record.Record value " + errstr

class TestValueToLatin:
    pass_values = [
        '\xe4bc', u'\xe4bc', b'\xe4bc', bytearray(b'\xe4bc')
    ]
    fail_values = [
        (int(), "accepts str or bytes, but not int"),
        (u'\u0394', "conversion requires latin text, but got {u}'\u0394'"),
    ]

    @pytest.mark.parametrize("value", pass_values)
    def test_pass(self, value):
        assert Record._value_to_latin(value, 'value') == '\xe4bc'

    @pytest.mark.parametrize("value, errstr", fail_values)
    def test_fail(self, value, errstr):
        errstr = errstr.format(u=('', 'u')[ndef.record._PY2])
        with pytest.raises((TypeError, ValueError)) as excinfo:
            Record._value_to_latin(value, 'value')
        assert str(excinfo.value) == "ndef.record.Record value " + errstr

class TestValueToUnicode:
    pass_values = [
        'abc', u'abc', b'abc', bytearray(b'abc')
    ]
    fail_values = [
        (int(), "accepts str or bytes, but not int"),
        (b'\x80', "conversion requires ascii text, but got {b}'\\x80'"),
    ]

    @pytest.mark.parametrize("value", pass_values)
    def test_pass(self, value):
        assert Record._value_to_unicode(value, 'value') == u'abc'

    @pytest.mark.parametrize("value, errstr", fail_values)
    def test_fail(self, value, errstr):
        errstr = errstr.format(b=('b', '')[ndef.record._PY2])
        with pytest.raises((TypeError, ValueError)) as excinfo:
            Record._value_to_unicode(value, 'value')
        assert str(excinfo.value) == "ndef.record.Record value " + errstr

