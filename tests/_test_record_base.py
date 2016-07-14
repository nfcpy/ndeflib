from __future__ import absolute_import, division

import ndef
import pytest

import sys
import re

def generate_tests(metafunc):
    if metafunc.cls and issubclass(metafunc.cls, _TestRecordBase):
        test_func = metafunc.function.__name__
        if test_func == "test_encode_valid":
            test_data = metafunc.cls.test_decode_valid_data
            test_data = [(args, payload) for payload, args in test_data]
        elif test_func == "test_compare_equal":
            test_data = metafunc.cls.test_decode_valid_data
            test_data = [(args, args) for payload, args in test_data]
        elif test_func == "test_compare_noteq":
            test_data = metafunc.cls.test_decode_valid_data
            test_data = [args for payload, args in test_data]
            test_data = zip(test_data, test_data[1:])
        elif test_func == "test_repr_is_implemented":
            test_data = metafunc.cls.test_decode_valid_data
            test_data = [(test_data[0][1],)]
        elif len(metafunc.fixturenames) > 0:
            test_data = eval("metafunc.cls.%s_data" % test_func)
        else:
            test_data = None
        if test_data:
            metafunc.parametrize(metafunc.fixturenames, test_data)

class _TestRecordBase:
    def test_init_args(self, args, attrs):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ATTRIB = list(map(str.strip, self.ATTRIB.split(',')))
        ASSERT = "assert {0}{1}.{2} == {3!r}"
        print()
        record = RECORD(*args)
        for i, attr in enumerate(ATTRIB):
            print(ASSERT.format(CLNAME, args, attr, attrs[i]))
            assert getattr(record, attr) == attrs[i]
        
    def test_init_kwargs(self, args, kwargs):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ASSERT = "assert {0}{1} == {0}({2})"
        print('\n' + ASSERT.format(CLNAME, args, kwargs))
        record = RECORD(*args)
        assert record == eval("{}({})".format(CLNAME, kwargs))

    def test_init_fail(self, args, errstr):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ERRSTR = CLNAME + errstr
        ASSERT = "assert {0}{1} ==> {2}"
        print('\n' + ASSERT.format(CLNAME, args, errstr))
        with pytest.raises((TypeError, ValueError)) as excinfo:
            RECORD(*args)
        result = str(excinfo.value)
        if sys.version_info < (3,):
            # remove b'..' literals but reinsert them for bytearray
            ERRSTR = re.sub("b'([^']*)'", r"'\1'", ERRSTR)
            ERRSTR = re.sub("(bytearray)\(('[^']*?')\)",r"\1(b\2)",ERRSTR)
            # remove u'..' literals
            result = re.sub("u'([^']*)'", r"'\1'", result)
        assert result == ERRSTR

    def test_decode_valid(self, payload, args):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        OCTETS = bytes(bytearray.fromhex(payload))
        ASSERT = "assert {0}.decode_payload(hex'{1}', 'strict') == {0}{2}"
        print('\n' + ASSERT.format(CLNAME, payload, args))
        record = RECORD(*args)
        assert RECORD._decode_payload(OCTETS, 'strict') == record

    def test_decode_error(self, payload, errstr):
        RECORD = self.RECORD;
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        OCTETS = bytes(bytearray.fromhex(payload))
        ERRSTR = CLNAME + ' ' + errstr
        ASSERT = "assert {0}.decode_payload(hex'{1}', 'strict') ==> {2}"
        print('\n' + ASSERT.format(CLNAME, payload, ERRSTR))
        with pytest.raises(ndef.DecodeError) as excinfo:
            RECORD._decode_payload(OCTETS, 'strict')
        assert str(excinfo.value) == ERRSTR

    def test_decode_relax(self, payload, args):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        OCTETS = bytes(bytearray.fromhex(payload))
        ASSERT = "assert {0}.decode_payload(hex'{1}', 'relax') == {0}{2}"
        print('\n' + ASSERT.format(CLNAME, payload, args))
        record = RECORD(*args)
        assert RECORD._decode_payload(OCTETS, 'relax') == record

    def test_encode_valid(self, args, payload):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        OCTETS = bytes(bytearray.fromhex(payload))
        ASSERT = "assert {0}({1}).encode_payload() == hex'{2}'"
        print('\n' + ASSERT.format(CLNAME, args, payload))
        record = RECORD(*args)
        assert record._encode_payload() == OCTETS

    def test_encode_error(self, args, errstr):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ERRSTR = CLNAME + ' ' + errstr
        ASSERT = "assert {0}{1} ==> {2}"
        print('\n' + ASSERT.format(CLNAME, args, errstr))
        with pytest.raises(ndef.EncodeError) as excinfo:
            record = RECORD(*args)
            record = record._encode_payload()
        assert str(excinfo.value) == ERRSTR

    def test_compare_equal(self, args_1, args_2):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ASSERT = "assert {0}{1} == {0}{2}"
        print('\n' + ASSERT.format(CLNAME, args_1, args_2))
        record_1 = RECORD(*args_1)
        record_2 = RECORD(*args_2)
        assert record_1 == record_2
        assert record_1.data == record_2.data

    def test_compare_noteq(self, args_1, args_2):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ASSERT = "assert {0}{1} != {0}{2}"
        print('\n' + ASSERT.format(CLNAME, args_1, args_2))
        record_1 = RECORD(*args_1)
        record_2 = RECORD(*args_2)
        assert record_1 != record_2
        assert record_1.data != record_2.data

    def test_format_args(self, args, formatted):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ASSERT = "assert format({0}{1}, 'args') == \"{2}\""
        print('\n' + ASSERT.format(CLNAME, args, formatted))
        record = RECORD(*args)
        result = format(record, 'args')
        if sys.version_info < (3,):
            # remove b'..' literals but reinsert them for bytearray
            formatted = re.sub("b'([^']*)'", r"'\1'", formatted)
            formatted = re.sub("(bytearray)\(('[^']*?')\)",r"\1(b\2)",formatted)
            # remove u'..' literals
            result = re.sub("u'([^']*)'", r"'\1'", result)
        assert result == formatted

    def test_format_str(self, args, formatted):
        RECORD = self.RECORD
        CLNAME = RECORD.__module__ + '.' + RECORD.__name__
        ASSERT = "assert format({0}{1}, '') == \"{2}\""
        print('\n' + ASSERT.format(CLNAME, args, formatted))
        record = RECORD(*args)
        result = format(record, '')
        if sys.version_info < (3,):
            formatted = re.sub("b'([^']*)'", r"'\1'", formatted)
            result = re.sub("u'([^']*)'", r"'\1'", result)
        assert result == formatted

