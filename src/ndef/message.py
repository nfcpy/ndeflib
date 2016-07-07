# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import io
from .record import Record, DecodeError


def message_decoder(stream_or_bytes, errors='strict',
                    known_types=Record._known_types):
    """A message decoder yields ndef.Record instances from the stream.
    """
    if isinstance(stream_or_bytes, (io.RawIOBase, io.BufferedIOBase)):
        stream = stream_or_bytes
    elif isinstance(stream_or_bytes, (bytes, bytearray)):
        stream = io.BytesIO(stream_or_bytes)
    else:
        errstr = "a stream or bytes type argument is required, not {}"
        raise TypeError(errstr.format(type(stream_or_bytes).__name__))

    try:
        record, mb, me, cf = Record._decode(stream, errors, known_types)
    except DecodeError:
        if errors == 'ignore':
            return  # just stop decoding
        raise

    if record is not None and mb is False and errors == 'strict':
        raise DecodeError('MB flag not set in first record')

    if record is not None and known_types is Record._known_types:
        known_types = type(record)._known_types

    while record is not None:
        yield record
        if me is True:
            if cf is True and errors == 'strict':
                raise DecodeError('CF flag set in last record')
            record = None
        else:
            try:
                record, mb, me, cf = Record._decode(stream, errors,
                                                    known_types)
            except DecodeError:
                if errors == 'ignore':
                    return  # just stop decoding
                raise
            else:
                if record is None and errors == 'strict':
                    raise DecodeError('ME flag not set in last record')
                if mb is True and errors == 'strict':
                    raise DecodeError('MB flag set in middle record')


def message_encoder(message=None, stream=None):
    encoder = _message_encoder(stream)
    if message is None:
        record = None
        while True:
            record = yield (encoder.send(record))
    else:
        itermsg = iter(message)
        encoder.send(None)
        encoder.send(next(itermsg))
        for record in itermsg:
            yield encoder.send(record)
        yield encoder.send(None)


def _message_encoder(stream):
    mb_flag = True
    this_record = yield
    next_record = yield
    while this_record:
        if not isinstance(this_record, Record):
            errstr = "an ndef.Record class instance is required, not {}"
            raise TypeError(errstr.format(type(this_record).__name__))
        me_flag = next_record is None
        cf_flag = not me_flag and next_record.type == 'unchanged'
        this_result = this_record._encode(mb_flag, me_flag, cf_flag, stream)
        this_record = next_record
        next_record = (yield this_result)
        mb_flag = False
