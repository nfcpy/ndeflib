.. -*- mode: rst; fill-column: 80 -*-

NDEF Decoding and Encoding
==========================

NDEF (NFC Data Exchange Format), specified by the `NFC Forum`_, is a binary
message format used to encapsulate application-defined payloads exchanged
between NFC Devices and Tags. Each payload is encoded as an NDEF Record with
fields that specify the payload size, payload type, an optional payload
identifier, and flags for indicating the first and last record of an NDEF
Message or tagging record chunks. An NDEF Message is simply a sequence of one or
more NDEF Records where the first and last record are marked by the Message
Begin and End flags.

The ``ndef`` package interface for decoding and encoding of NDEF Messages
consists of the :func:`message_decoder` and :func:`message_encoder` functions
that both return generators for decoding octets into :class:`ndef.Record`
instances or encoding :class:`ndef.Record` instances into octets. :ref:`Known
record types <known-types>` are decoded into instances of their implementation
class and can be directly encoded as part of a message.

Message Decoder
---------------

.. function:: message_decoder(stream_or_bytes, errors='strict', \
              known_records=Record._known_types)

   Returns a generator function that decodes NDEF Records from a file-like,
   byte-oriented stream or a bytes object given by the *stream_or_bytes*
   argument. When the *errors* argument is set to 'strict' (the default), the
   decoder expects a valid NDEF Message with Message Begin and End flags set for
   the first and last record and decoding of known record types will fail for
   any format errors. Minor format errors are accepted when *errors* is set to
   'relax'. With *errors* set to 'ignore' the decoder silently stops when a
   non-correctable error is encountered. The *known_records* argument provides
   the mapping of record type strings to class implementations. It defaults to
   all global records implemented by `ndeflib` or additionally registered from
   user code. It's main use would probably be to force decoding into only
   generic records with `known_records={}`.

   :param stream_or_bytes: message data octets
   :type stream_or_bytes: byte stream or bytes object
   :param str errors: error handling strategy, may be 'strict', 'relax' or 'ignore'
   :param dict known_records: mapping of known record types to implementation classes
   :raises ndef.DecodeError: for data format errors (unless *errors* is set to 'ignore')

   >>> import ndef
   >>> octets = bytearray.fromhex('910303414243616263 5903030144454630646566')
   >>> decoder = ndef.message_decoder(octets)
   >>> next(decoder)
   ndef.record.Record('urn:nfc:wkt:ABC', '', bytearray(b'abc'))
   >>> next(decoder)
   ndef.record.Record('urn:nfc:wkt:DEF', '0', bytearray(b'def'))
   >>> next(decoder)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   StopIteration
   >>> message = list(ndef.message_decoder(octets))
   >>> len(message)
   2


Message Encoder
---------------

.. function:: message_encoder(message=None, stream=None)

   Returns a generator function that encodes :class:`ndef.Record` objects into
   an NDEF Message octet sequence. The *message* argument is either an iterable
   of records or None, if *message* is None the records must be sequentially
   send to the encoder (as for any generator the first send value must be None,
   specific to the message encoder is that octets are generated for the previous
   record and a final None value must be send for the last record octets). The
   *stream* argument controls the output of the generator function. If *stream*
   is None, the generator yields a bytes object for each encoded record.
   Otherwise, it must be a file-like, byte-oriented stream that receives the
   encoded octets and the generator yields the number of octets written per
   record.

   :param message: sequence of records to encode
   :type message: iterable or None
   :param stream: file-like output stream
   :type stream: byte stream or None
   :raises ndef.EncodeError: for invalid record parameter values or types 

   >>> import ndef
   >>> record1 = ndef.Record('urn:nfc:wkt:ABC', '1', b'abc')
   >>> record2 = ndef.Record('urn:nfc:wkt:DEF', '2', b'def')
   >>> encoder = ndef.message_encoder()
   >>> encoder.send(None)
   >>> encoder.send(record1)
   >>> encoder.send(record2)
   b'\x99\x03\x03\x01ABC1abc'
   >>> encoder.send(None)
   b'Y\x03\x03\x01DEF2def'
   >>> message = [record1, record2]
   >>> b''.join((ndef.message_encoder(message)))
   b'\x99\x03\x03\x01ABC1abcY\x03\x03\x01DEF2def'
   >>> list((ndef.message_encoder(message, open('/dev/null', 'wb'))))
   [11, 11]



Record Class
------------

.. class:: Record(type='', name='', data=b'')

   This class implements generic decoding and encoding of an NDEF Record and is
   the base for all specialized record type classes. The NDEF Record Payload
   Type encoded by the TNF (Type Name Format) and TYPE field is represented by a
   single *type* string argument:

   *Empty (TNF 0)*

     An *Empty* record has no TYPE, ID, and PAYLOAD fields. This is set if the
     *type* argument is absent, None, or an empty string. Encoding ignores
     whatever is set as *name* and *data*, producing just the short length
     record ``b'\x10\x00\x00'``.

   *NFC Forum Well Known Type (TNF 1)*

     An *NFC Forum Well Known Type* is a URN (:rfc:`2141`) with namespace
     identifier (NID) ``nfc`` and the namespace specific string (NSS) prefixed
     with ``wkt:``. When encoding, the type is written as a relative-URI
     (cf. :rfc:`3986`), omitting the NID and the prefix. For example, the type
     ``urn:nfc:wkt:T`` is encoded as TNF 1, TYPE ``T``.

   *Media-type as defined in RFC 2046 (TNF 2)*

     A *media-type* follows the media-type grammar defined in :rfc:`2046`.
     Records that carry a payload with an existing, registered media type should
     use this record type. Note that the record type indicates the type of the
     payload; it does not refer to a MIME message that contains an entity of the
     given type. For example, the media type 'image/jpeg' indicates that the
     payload is an image in JPEG format using JFIF encoding as defined by
     :rfc:`2046`.

   *Absolute URI as defined in RFC 3986 (TNF 3)*

     An *absolute-URI* follows the absolute-URI BNF construct defined by
     :rfc:`3986`. This type can be used for payloads that are defined by
     URIs. For example, records that carry a payload with an XML-based message
     type may use the XML namespace identifier of the root element as the record
     type, like a SOAP/1.1 message may be
     ``http://schemas.xmlsoap.org/soap/envelope/``.

   *NFC Forum External Type (TNF 4)*

     An *NFC Forum External Type* is a URN (:rfc:`2141`) with namespace
     identifier (NID) ``nfc`` and the namespace specific string (NSS) prefixed
     with ``ext:``. When encoding, the type is written as a relative-URI
     (cf. :rfc:`3986`), omitting the NID and the prefix. For example, the type
     ``urn:nfc:ext:nfcpy.org:T`` will be encoded as TNF 4, TYPE ``nfcpy.org:T``.

   *Unknown (TNF 5)*

     The *Unknown* record type indicates that the type of the payload is
     unknown, similar to the ``application/octet-stream`` media type. It is set
     with the *type* argument ``unknown`` and encoded with an empty TYPE field.

   *Unchanged (TNF 6)*

     The *Unchanged* record type is used for all except the first record in a
     chunked payload. It is set with the *type* argument ``unchanged`` and
     encoded with an empty TYPE field.

   The *type* argument sets the final value of the :attr:`type` attribute, which
   provides the value only for reading. The *name* and *data* argument set the
   initial values of the :attr:`name` and :attr:`data` attributes. They can both
   be changed later.

   :param str type: final value for the :attr:`type` attribute
   :param str name: initial value for the see :attr:`name` attribute
   :param bytes data: initial value for the :attr:`data` attribute


   .. attribute:: type

      The record type is a read-only text string set either by decoding or
      through initialization.

   .. attribute:: name

      The record name is a text string that corresponds to the NDEF Record ID
      field. The maximum capacity is 255 8-bit characters, converted in and out
      as latin-1.

   .. attribute:: data

      The record data is a bytearray with the sequence of octets that correspond
      to the NDEF Record PAYLOAD field. The attribute itself is readonly but the
      bytearray content can be changed. Note that for derived record classes
      this becomes a read-only bytes object with the content encoded from the
      record's attributes.

   .. attribute:: MAX_PAYLOAD_SIZE

      This is a class data attribute that restricts the decodable and encodable
      maximum NDEF Record PAYLOAD size from the theoretical value of up to 4GB
      to 1MB. If needed, a different value can be assigned to the record class:
      ``ndef.Record.MAX_PAYLOAD_SIZE = 100*1024``

   .. classmethod:: register_type(record_class)

      Register a derived record class as a known type for decoding. This creates
      an entry for the record_class type string to be decoded as a record_class
      instance. Beyond internal use this is needed for :ref:`adding private
      records <extending>`.
