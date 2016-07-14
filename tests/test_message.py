# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import pytest

from ndef import Record
from io import BytesIO

test_message_set_1 = [
    ('', []),
    ('D00000', [Record()]),
    ('900000 500000', [Record(), Record()]),
    ('900000 100000 500000', [Record(), Record(), Record()]),
    ('900000 100000 500000', 3 * [Record()]),
    ('B50000 560000', [Record('unknown'), Record('unchanged')]),
]

@pytest.mark.parametrize("encoded, message", test_message_set_1)
def test_message_decoder_with_bytes_input(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    assert list(ndef.message_decoder(octets)) == message

@pytest.mark.parametrize("encoded, message", test_message_set_1)
def test_message_decoder_with_stream_input(encoded, message):
    stream = BytesIO(bytearray.fromhex(encoded))
    assert list(ndef.message_decoder(stream)) == message

@pytest.mark.parametrize("encoded, message", test_message_set_1)
def test_message_encoder_with_bytes_output(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    assert b''.join(list(ndef.message_encoder(message))) == octets

@pytest.mark.parametrize("encoded, message", test_message_set_1)
def test_message_encoder_with_stream_output(encoded, message):
    stream = BytesIO()
    octets = bytes(bytearray.fromhex(encoded))
    assert sum(ndef.message_encoder(message, stream)) == len(octets)
    assert stream.getvalue() == octets

@pytest.mark.parametrize("encoded, message", test_message_set_1)
def test_message_encoder_with_record_send(encoded, message):
    stream = BytesIO()
    octets = bytes(bytearray.fromhex(encoded))
    encoder = ndef.message_encoder(stream=stream)
    encoder.send(None)
    for record in message:
        encoder.send(record)
    encoder.send(None)
    assert stream.getvalue() == octets

test_message_set_2 = [
    ('150000 160000 560000', 'MB flag not set in first record'),
    ('950000 960000 560000', 'MB flag set in middle record'),
    ('950000 160000 160000', 'ME flag not set in last record'),
    ('B50000 160000 760000', 'CF flag set in last record'),
]

@pytest.mark.parametrize("encoded, errmsg", test_message_set_2)
def test_fail_decode_invalid_message_strict(encoded, errmsg):
    stream = BytesIO(bytearray.fromhex(encoded))
    with pytest.raises(ndef.DecodeError) as excinfo:
        list(ndef.message_decoder(stream, errors='strict'))
    assert errmsg == str(excinfo.value)

@pytest.mark.parametrize("encoded, errmsg", test_message_set_2)
def test_pass_decode_invalid_message_relax(encoded, errmsg):
    stream = BytesIO(bytearray.fromhex(encoded))
    message = [Record('unknown'), Record('unchanged'), Record('unchanged')]
    assert list(ndef.message_decoder(stream, errors='relax')) == message

test_message_set_3 = [
    ('19', 'buffer underflow'),
    ('1901', 'buffer underflow'),
    ('190101', 'buffer underflow'),
    ('19010101', 'buffer underflow'),
    ('19010101aa', 'buffer underflow'),
    ('19010101aabb', 'buffer underflow'),
    ('19000000', 'must be'),
    ('18010000', 'must be'),
    ('18000001', 'must be'),
    ('18000100', 'must be'),
]

@pytest.mark.parametrize("encoded, errmsg", test_message_set_3)
def test_fail_decode_invalid_message_relax(encoded, errmsg):
    stream = BytesIO(bytearray.fromhex(encoded))
    with pytest.raises(ndef.DecodeError) as excinfo:
        list(ndef.message_decoder(stream, errors='relax'))
    assert errmsg in str(excinfo.value)
    stream = BytesIO(bytearray.fromhex('900000' + encoded))
    with pytest.raises(ndef.DecodeError) as excinfo:
        list(ndef.message_decoder(stream, errors='relax'))
    assert errmsg in str(excinfo.value)

@pytest.mark.parametrize("encoded, errmsg", test_message_set_3)
def test_pass_decode_invalid_message_ignore(encoded, errmsg):
    stream = BytesIO(bytearray.fromhex(encoded))
    assert list(ndef.message_decoder(stream, errors='ignore')) == []
    stream = BytesIO(bytearray.fromhex('900000' + encoded))
    assert list(ndef.message_decoder(stream, errors='ignore')) == [Record()]

test_message_set_4 = [
    (1, 'a stream or bytes type argument is required, not int'),
    (1.0, 'a stream or bytes type argument is required, not float'),
]

@pytest.mark.parametrize("argument, errmsg", test_message_set_4)
def test_fail_message_decoder_invalid_types(argument, errmsg):
    with pytest.raises(TypeError) as excinfo:
        list(ndef.message_decoder(argument))
    assert errmsg == str(excinfo.value)

test_message_set_5 = [
    ([1], 'an ndef.Record class instance is required, not int'),
    ([1.0], 'an ndef.Record class instance is required, not float'),
]

@pytest.mark.parametrize("argument, errmsg", test_message_set_5)
def test_fail_message_encoder_invalid_types(argument, errmsg):
    with pytest.raises(TypeError) as excinfo:
        list(ndef.message_encoder(argument))
    assert errmsg == str(excinfo.value)

def test_message_encoder_stop_iteration():
    encoder = ndef.message_encoder()
    encoder.send(None)
    encoder.send(None)
    with pytest.raises(StopIteration):
        encoder.send(None)
