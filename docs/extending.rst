.. -*- mode: rst; fill-column: 80 -*-

.. _extending:

Adding Private Records
======================

Private (or experimental) NDEF Record decoding and encoding can be easily made
recognized by the :func:`message_decoder` and :func:`message_encoder`. It just
requires a record class that inherits from ``ndef.record.GlobalRecord`` and
provides the desired record type value as well as the payload decode and encode
methods. The following sections document the decode/encode interface by way of
example, with increasing complexity.

Record with no Payload
----------------------

This is the most simple yet fully functional record class. It inherits from the
abstract class ``ndef.record.GlobalRecord`` (which is actually just an abstract
version of `Record` to make sure the dervied class implements the payload
decode and encode methods. The record type string is set via the ``_type`` class
attribute. The ``_encode_payload`` method must return the `bytes` for the NDEF
Record PAYLOAD field, usually encoded from other record attributes but here it's
just empty. The ``_decode_payload`` classmethod receives the NDEF Record PAYLOAD
field the `bytes` type *octets* and returns a record object populated with the
decoded PAYLOAD data, again nothing for the record with no payload. The
``_decode_min_payload_length`` and ``_decode_max_payload_length`` class
attributes (put at the end of the class definition only to align with the
explanation) inform the record decoder about the minmum required and maximum
acceptable PAYLOAD size, thus the *octets* argument will never have less or more
data. If a class does not set those values, the default min value is 0 and the
default max value is `Record.MAX_PAYLOAD_SIZE`.

.. testcode::

   import ndef
   
   class ExampleRecordWithNoPayload(ndef.record.GlobalRecord):
       """An NDEF Record with no payload."""
       
       _type = 'urn:nfc:ext:nfcpy.org:x-empty'

       def _encode_payload(self):
           # This record does not have any payload to encode.
           return b''

       @classmethod
       def _decode_payload(cls, octets, errors):
           # This record does not have any payload to decode.
           return cls()

       _decode_min_payload_length = 0
       _decode_max_payload_length = 0
   
   ndef.Record.register_type(ExampleRecordWithNoPayload)
   
   record = ExampleRecordWithNoPayload()
   octets = b''.join(ndef.message_encoder([record]))
   print("encoded: {}".format(octets))

   message = list(ndef.message_decoder(octets))
   print("decoded: {}".format(message[0]))

.. testoutput::

   encoded: b'\xd4\x11\x00nfcpy.org:x-empty'
   decoded: NDEF Example Record With No Payload ID '' PAYLOAD 0 byte


Example Temperature Record
--------------------------

This record carries an unsigned 32-bit integer timestamp that is the seconds
since 1.1.1970 (and will overflow on February 7, 2106 !) and a signed 16-bit
integer with a temperature. The payload is thus a fixed structure with exactly 6
octets for which the inherited ``_decode_struct`` and ``_encode_struct`` methods
are perfectly suited. They are quite the same as using `struct.unpack_from` and
`struct.pack` but return a single value directly and not as a (value, ) tuple.

This example also shows how the ``__format__`` method is used to provide an
arguments and a data view for the `str() <str>` and :func:`repr` functions.

.. testcode::

   import ndef
   import time
   
   class ExampleTemperatureRecord(ndef.record.GlobalRecord):
       """An NDEF Record that carries a temperature and a timestamp."""
       
       _type = 'urn:nfc:ext:nfcpy.org:x-temp'

       def __init__(self, timestamp, temperature):
           self._time = timestamp
           self._temp = temperature

       def __format__(self, format_spec):
           if format_spec == 'args':
               # Return the init args for repr() but w/o class name and brackets
               return "{r._time}, {r._temp}".format(r=self)
           if format_spec == 'data':
               # Return a nicely formatted content string for str()
               data_str = time.strftime('%d.%m.%Y', time.gmtime(self._time))
               time_str = time.strftime('%H:%M:%S', time.gmtime(self._time))
               return "{}°C on {} at {}".format(self._temp, data_str, time_str)
           return super(ExampleTemperatureRecord, self).__format__(format_spec)

       def _encode_payload(self):
           return self._encode_struct('>Lh', self._time, self._temp)

       @classmethod
       def _decode_payload(cls, octets, errors):
           timestamp, temperature = cls._decode_struct('>Lh', octets)
           return cls(timestamp, temperature)

       # Make sure that _decode_payload gets only called with 6 octets
       _decode_min_payload_length = 6
       _decode_max_payload_length = 6
   
   ndef.Record.register_type(ExampleTemperatureRecord)
   
   record = ExampleTemperatureRecord(1468410873, 25)
   octets = b''.join(ndef.message_encoder([record]))
   print("encoded: {}".format(octets))

   message = list(ndef.message_decoder(octets))
   print("decoded: {}".format(message[0]))

.. testoutput::

   encoded: b'\xd4\x10\x06nfcpy.org:x-tempW\x86+\xf9\x00\x19'
   decoded: NDEF Example Temperature Record ID '' 25°C on 13.07.2016 at 11:54:33



Type Length Value Record
------------------------

This record class demonstrates how ``_decode_struct`` and ``_encode_struct`` can
be used for typical Type-Length-Value constructs. The notion 'BB+' is a slight
extension of the `struct` module's format string syntax and means to decode or
encode a 1 byte Type field, a 1 byte Length field and Length number of octets as
Value. The ``_decode_struct`` method then returns just the Type and Value. The
``_encode_struct`` needs only the Type and Value arguments and takes the Length
from Value. Another format string syntax extension, but not not used in the
example, is a trailing '*' character. That just means that all remaining octets
are returned as `bytes`.

This example also demonstrates how decode and encode error exceptions are
generated with the ``_decode_error`` and ``_encode_error`` methods. These
methods return an instance of ``ndef.DecodeError`` and ``ndef.EncodeError`` with
the fully qualified class name followed by the expanded format string. Two
similar methods, ``_type_error`` and ``_value_error`` may be used whenever a
`TypeError` or `ValueError` shall be reported with the full classname in its
error string. They do also check if the first word in the format string matches
a data attribute name, and if, the string is joined with a '.' to the classname.

The ``_decode_payload`` method also shows the use of the errors argument. With
'strict' interpretation of errors the payload is expected to have the Type 1 TLV
encoded in first place (although not a recommended design for TLV loops). The
errors argument may also say 'relax' and then the order won't matter.

.. testcode::

   import ndef
   
   class ExampleTypeLengthValueRecord(ndef.record.GlobalRecord):
       """An NDEF Record with carries a temperature and a timestamp."""
       
       _type = 'urn:nfc:ext:nfcpy.org:x-tlvs'

       def __init__(self, *args):
           # We expect each argument to be a tuple of (Type, Value) where Type
	   # is int and Value is bytes. So *args* will be a tuple of tuples.
           self._tlvs = args

       def _encode_payload(self):
           if sum([t for t, v in self._tlvs if t == 1]) != 1:
	       raise self._encode_error("exactly one Type 1 TLV is required")
           tlv_octets = []
           for t, v in self._tlvs:
	       tlv_octets.append(self._encode_struct('>BB+', t, v))
	   return b''.join(tlv_octets)

       @classmethod
       def _decode_payload(cls, octets, errors):
           tlvs = []
           offset = 0
           while offset < len(octets):
               t, v = cls._decode_struct('>BB+', octets, offset)
	       offset = offset + 2 + len(v)
	       tlvs.append((t, v))
           if sum([t for t, v in tlvs if t == 1]) != 1:
	       raise cls._encode_error("missing the mandatory Type 1 TLV")
	   if errors == 'strict' and len(tlvs) > 0 and tlvs[0][0] != 1:
	       errstr = 'first TLV must be Type 1, not Type {}'
               raise cls._encode_error(errstr, tlvs[0][0])
           return cls(*tlvs)

       # We need at least the 2 octets Type, Length for the first TLV.
       _decode_min_payload_length = 2
   
   ndef.Record.register_type(ExampleTypeLengthValueRecord)

   record = ExampleTypeLengthValueRecord((1, b'abc'), (5, b'xyz'))
   octets = b''.join(ndef.message_encoder([record]))
   print("encoded: {}".format(octets))

   message = list(ndef.message_decoder(octets))
   print("decoded: {}".format(message[0]))

.. testoutput::

   encoded: b'\xd4\x10\nnfcpy.org:x-tlvs\x01\x03abc\x05\x03xyz'
   decoded: NDEF Example Type Length Value Record ID '' PAYLOAD 10 byte '0103616263050378797a'














