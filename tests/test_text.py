# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import pytest
import _test_record_base

def pytest_generate_tests(metafunc):
    _test_record_base.generate_tests(metafunc)

class TestTextRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.text.TextRecord
    ATTRIB = "text, language, encoding"

    test_init_args_data = [
        ((), ('', 'en', 'UTF-8')),
        ((None, None, None), ('', 'en', 'UTF-8')),
        (('Hello',), ('Hello', 'en', 'UTF-8')),
        (('Hello', 'en',), ('Hello', 'en', 'UTF-8')),
        (('Hello', 'en', 'UTF-8'), ('Hello', 'en', 'UTF-8')),
        (('Hello', 'de', 'UTF-16'), ('Hello', 'de', 'UTF-16')),
        (('Hello', 63*'a'), ('Hello', 63*'a', 'UTF-8')),
        ((u'Hallo', u'de',), ('Hallo', 'de', 'UTF-8')),
        ((b'Hallo', b'de',), ('Hallo', 'de', 'UTF-8')),
    ]
    test_init_kwargs_data = [
        (('T', 'de', 'UTF-16'), "text='T', language='de', encoding='UTF-16'"),
    ]
    test_init_fail_data = [
        ((1,), ".text accepts str or bytes, but not int"),
        (('', ''), ".language must be 1..63 characters, got 0"),
        (('', 64*'a'), ".language must be 1..63 characters, got 64"),
        (('', 'a', 'X'), ".encoding may be 'UTF-8' or 'UTF-16', but not 'X'"),
        (('', 0,), ".language accepts str or bytes, but not int"),
        (('', 'a', 0), ".encoding may be 'UTF-8' or 'UTF-16', but not '0'"),
    ]
    test_decode_valid_data = [
        ('02656e', ("", "en", "UTF-8")),
        ('026465', ("", "de", "UTF-8")),
        ('02656e48656c6c6f', ("Hello", "en", "UTF-8")),
        ('82656efffe480065006c006c006f00', ("Hello", "en", "UTF-16")),
        ('02656cce94', (u"\u0394", "el", "UTF-8")),
        ('82656cfffe9403', (u"\u0394", "el", "UTF-16")),
    ]
    test_decode_error_data = [
        ("82656e54", "can't be decoded as UTF-16"),
        ("02656efffe5400", "can't be decoded as UTF-8"),
        ("00", "language code length can not be zero"),
        ("01", "language code length exceeds payload"),
    ]
    test_decode_relax = None
    test_encode_error = None
    test_format_args_data = [
        ((), "'', 'en', 'UTF-8'"),
        (('a',), "'a', 'en', 'UTF-8'"),
        (('a', 'de'), "'a', 'de', 'UTF-8'"),
    ]    
    test_format_str_data = [
        ((),
         "NDEF Text Record ID '' Text '' Language 'en' Encoding 'UTF-8'"),
        (('T'),
         "NDEF Text Record ID '' Text 'T' Language 'en' Encoding 'UTF-8'"),
        (('T','de'),
         "NDEF Text Record ID '' Text 'T' Language 'de' Encoding 'UTF-8'"),
    ]

text_messages = [
    ('D101075402656e54455854',
     [ndef.TextRecord('TEXT', 'en', 'UTF-8')]),
    ('9101075402656e54585431 5101075402656e54585432',
     [ndef.TextRecord('TXT1', 'en', 'UTF-8'),
      ndef.TextRecord('TXT2', 'en', 'UTF-8')]),
]

@pytest.mark.parametrize("encoded, message", text_messages)
def test_message_decode(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    print(list(ndef.message_decoder(octets)))
    assert list(ndef.message_decoder(octets)) == message

@pytest.mark.parametrize("encoded, message", text_messages)
def test_message_encode(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    print(list(ndef.message_encoder(message)))
    assert b''.join(list(ndef.message_encoder(message))) == octets

