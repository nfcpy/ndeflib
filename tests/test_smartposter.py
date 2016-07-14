# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import pytest
import _test_record_base

def pytest_generate_tests(metafunc):
    _test_record_base.generate_tests(metafunc)

class TestActionRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.smartposter.ActionRecord
    ATTRIB = "action"

    test_init_args_data = [
        ((), ('exec',)),
        ((None,), ('exec',)),
        (('exec',), ('exec',)),
        (('save',), ('save',)),
        (('edit',), ('edit',)),
        ((0,), ('exec',)),
        ((1,), ('save',)),
        ((2,), ('edit',)),
    ]
    test_init_kwargs_data = [
        (('save',), "action='save'"),
    ]
    test_init_fail_data = [
        ((3,),
         ".action may be one of ('exec', 'save', 'edit') or index, but not 3"),
    ]
    test_decode_valid_data = [
        ('00', ('exec',)),
        ('01', ('save',)),
        ('02', ('edit',)),
    ]
    test_decode_error_data = [
        ('03', "decoding of ACTION value 3 is not defined"),
        ('ff', "decoding of ACTION value 255 is not defined"),
    ]
    test_decode_relax_data = [
        ('03', ('exec',)),
        ('ff', ('exec',)),
    ]
    test_encode_error = None
    test_format_args_data = [
        ((), "'exec'"),
        (('save',), "'save'"),
    ]
    test_format_str_data = [
        ((), "NDEF Smartposter Action Record ID '' Action 'exec'"),
        (('save',), "NDEF Smartposter Action Record ID '' Action 'save'"),
    ]

class TestSizeRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.smartposter.SizeRecord
    ATTRIB = "resource_size"

    test_init_args_data = [
        ((), (0,)),
        ((1234,), (1234,)),
    ]
    test_init_kwargs_data = [
        ((1234,), "resource_size=1234"),
    ]
    test_init_fail_data = [
        (('ab',), ".resource_size expects 32-bit unsigned int, but got 'ab'"),
        ((-1,), ".resource_size expects 32-bit unsigned int, but got -1"),
    ]
    test_decode_valid_data = [
        ('00000000', (0,)),
        ('12345678', (0x12345678,)),
        ('ffffffff', (0xffffffff,)),
    ]
    test_decode_error = None
    test_decode_relax = None
    test_encode_error = None
    test_format_args_data = [
        ((), "0"),
        ((1234,), "1234"),
    ]
    test_format_str_data = [
        ((),
         "NDEF Smartposter Size Record ID '' Resource Size '0 byte'"),
        ((1234,),
         "NDEF Smartposter Size Record ID '' Resource Size '1234 byte'"),
    ]

class TestTypeRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.smartposter.TypeRecord
    ATTRIB = "resource_type"

    test_init_args_data = [
        ((), ('',)),
        (('text/html',), ('text/html',)),
    ]
    test_init_kwargs_data = [
        (('text/html',), "resource_type='text/html'"),
    ]
    test_init_fail_data = [
        ((int(),), ".resource_type accepts str or bytes, but not int"),
    ]
    test_decode_valid_data = [
        ('', ('',)),
        ('746578742f68746d6c', ('text/html',)),
    ]
    test_decode_error_data = [
        ('ff', "can't decode payload as utf-8"),
    ]
    test_decode_relax = None
    test_encode_error = None
    test_format_args_data = [
        ((), "''"),
        (('text/html',), "'text/html'"),
    ]
    test_format_str_data = [
        ((),
         "NDEF Smartposter Type Record ID '' Resource Type ''"),
        (('text/html',),
         "NDEF Smartposter Type Record ID '' Resource Type 'text/html'"),
    ]

class TestSmartposterRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.smartposter.SmartposterRecord
    ATTRIB = ("resource, title, titles, action, icon, icons," +
              "resource_size, resource_type")

    test_init_args_data = [
        ((),
         (ndef.UriRecord(''), None, {}, None, None, {}, None, None)),
        (('tel:123',),
         (ndef.UriRecord('tel:123'), None, {}, None, None, {}, None, None)),
        ((None, 'phone',),
         (None, 'phone', {'en': 'phone'}, None, None, {}, None, None)),
        ((None, None, 'exec'),
         (None, None, {}, 'exec', None, {}, None, None)),
        ((None, None, None, None, 1000),
         (None, None, {}, None, None, {}, 1000, None)),
        ((None, None, None, None, None, 'a/b'),
         (None, None, {}, None, None, {}, None, 'a/b')),
        ((None, None, None, {'image/gif': 'data'}),
         (None, None, {}, None, b'data', {'image/gif': b'data'}, None, None)),
    ]
    test_init_kwargs_data = [
        (('tel:123', 'phone', 'exec', {'image/gif': b'icon'}, 10, 'text/html'),
         ("resource='tel:123', title='phone', action='exec', " +
          "icon={'image/gif': b'icon'}, resource_size=10, " +
          "resource_type='text/html'")),
    ]
    test_init_fail_data = [
        ((None, None, None, b'123'),
         (" init requires icon bytes with png header, not b'123'")),
        ((None, None, None, 1),
         " init icon argument must be bytes or mapping, not int"),
        ((None, None, None, {'text/plain': b'123'}),
         " expects an image or video icon mimetype, not 'text/plain'"),
    ]
    test_decode_valid_data = [
        ('d101015500', ('',)),
        ('d1010a55036e666370792e6f7267', ('http://nfcpy.org',)),
        ('9101015500 5101085402656e6e66637079', ('', 'nfcpy')),
        ('9101015500 510108540264656e66637079', ('', {'de': 'nfcpy'})),
        ('9101015500 51030161637400', ('', None, 'exec')),
        ('9101015500 5101047300000001', ('', None, None, None, 1)),
        ('9101015500 51010374612f62', ('', None, None, None, None, 'a/b')),
        ('9101015500 520908 696d6167652f706e67 89504e470d0a1a0a',
         ('', None, None, b'\x89PNG\x0d\x0a\x1a\x0a')),
        ('9101015500 520901766964656f2f6d703400',
         ('', None, None, {'video/mp4': b'\0'})),
        ('9101015500 520901696d6167652f706e6701',
         ('', None, None, {'image/png': b'\1'})),
        ('9101015500 520901696d6167652f67696601',
         ('', None, None, {'image/gif': b'\1'})),
    ]
    test_decode_error_data = [
        ('', "payload must contain exactly one URI Record, got 0"),
        ('9101015500 5101015500',
         "payload must contain exactly one URI Record, got 2"),
    ]
    test_decode_relax_data = [
        ('9101015500 510301616374ff', ('', None, 'exec')),
    ]
    test_encode_error = None
    test_format_args_data = [
        (('http://nfcpy.org', 'nfcpy project', 'save',
          {'image/png': b'image data'}, 10000, 'text/html'),
         ("'http://nfcpy.org', {'en': 'nfcpy project'}, 'save', " +
          "{'image/png': bytearray(b'image data')}, 10000, 'text/html')")),
    ]
    test_format_str_data = [
        (('http://nfcpy.org',),
         "NDEF Smartposter Record ID '' Resource 'http://nfcpy.org'"),
        (('http://nfcpy.org', "nfcpy project"),
         "NDEF Smartposter Record ID '' Resource 'http://nfcpy.org' "\
         "Title 'nfcpy project'"),
        (('http://nfcpy.org', 'nfcpy project', 'exec'),
         "NDEF Smartposter Record ID '' Resource 'http://nfcpy.org' "\
         "Title 'nfcpy project' Action 'exec'"),
        (('http://nfcpy.org', 'nfcpy', 'exec', {'image/png': b''}),
         "NDEF Smartposter Record ID '' Resource 'http://nfcpy.org' "\
         "Title 'nfcpy' Icon 'image/png' Action 'exec'"),
        (('http://nfcpy.org', 'nfcpy', None, None, 999, 'text/html'),
         "NDEF Smartposter Record ID '' Resource 'http://nfcpy.org' "\
         "Title 'nfcpy' Resource Size '999 byte' Resource Type 'text/html'"),
    ]
    def test_embedded_record_lists(self):
        record = ndef.smartposter.SmartposterRecord(None)
        assert record.uri_records == []
        assert record.title_records == []
        assert record.action_records == []
        assert record.size_records == []
        assert record.type_records == []
        assert record.icon_records == []


def test_set_title():
    record = ndef.SmartposterRecord()
    assert record.titles == {}
    record.set_title("English Text",)
    record.set_title("German Text", "de")
    assert record.titles == {'en': 'English Text', 'de': 'German Text'}
    record.set_title("Deutscher Text", "de")
    assert record.titles == {'en': 'English Text', 'de': 'Deutscher Text'}

smartposter_messages = [
    ('d102055370 d101015500',
     [ndef.SmartposterRecord('')]),
    ('d1020e5370 d1010a55036e666370792e6f7267',
     [ndef.SmartposterRecord('http://nfcpy.org')]),
    ('d1021a5370 91010a55036e666370792e6f7267 5101085402656e6e66637079',
     [ndef.SmartposterRecord('http://nfcpy.org', 'nfcpy')]),
    ('d102215370 91010a55036e666370792e6f7267 1101085402656e6e66637079'
     '51030161637400',
     [ndef.SmartposterRecord('http://nfcpy.org', 'nfcpy', 'exec')]),
]

@pytest.mark.parametrize("encoded, message", smartposter_messages + [
    ('d102085370 9101015500 500000',
     [ndef.SmartposterRecord('')]),
])
def test_message_decode(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    print(list(ndef.message_decoder(octets)))
    assert list(ndef.message_decoder(octets)) == message

@pytest.mark.parametrize("encoded, message", smartposter_messages)
def test_message_encode(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    print(list(ndef.message_encoder(message)))
    assert b''.join(list(ndef.message_encoder(message))) == octets

@pytest.mark.parametrize("encoded, errstr", [
    ('d1020c5370 9101015500 51030061637400',
     "ActionRecord payload length can not be less than 1"),
    ('d1020c5370 9101015500 510301616374ff',
     "ActionRecord decoding of ACTION value 255 is not defined"),
    ('d1020c5370 9101015500 51010373000000',
     "SizeRecord payload length can not be less than 4"),
    ('d1020e5370 9101015500 510105730000000000',
     "SizeRecord payload length can not be more than 4"),
    ('d1020f5370 9101015500 51010674ff6578742f70',
     "TypeRecord can't decode payload as utf-8"),
])
def test_message_decode_fail(encoded, errstr):
    octets = bytes(bytearray.fromhex(encoded))
    with pytest.raises(ndef.DecodeError) as excinfo:
        print(list(ndef.message_decoder(octets)))
    assert str(excinfo.value) == "ndef.smartposter." + errstr

