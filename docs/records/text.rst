.. -*- mode: rst; fill-column: 80 -*-

Text Record
-----------

The NDEF Text Record is a well-known record type defined by the `NFC Forum`_. It
carries a UTF-8 or UTF-16 encoded text string with an associated IANA language
code identifier.

.. class:: TextRecord(text='', language='en', encoding='UTF-8')

   A :class:`TextRecord` is initialized with the actual text content, an
   ISO/IANA language identifier, and the desired transfer encoding UTF-8 or
   UTF-16. Default values are empty text, language code 'en', and 'UTF-8'
   encoding.

   :param str text: initial value for the `text` attribute, default ''
   :param str language: initial value for the `language` attribute, default 'en'
   :param str encoding: initial value for the `encoding` attribute, default 'UTF-8'

   .. attribute:: type

      The Text Record type is ``urn:nfc:wkt:T``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: text

      The decoded or set text string value.

   .. attribute:: language

      The decoded or set IANA language code identifier.

   .. attribute:: encoding

      The transfer encoding of the text string. Either 'UTF-8' or 'UTF-16'.

   >>> import ndef
   >>> record = ndef.TextRecord("Hallo Welt", "de")
   >>> octets = b''.join(ndef.message_encoder([record]))
   >>> print(list(ndef.message_decoder(octets))[0])
   NDEF Text Record ID '' Text 'Hallo Welt' Language 'de' Encoding 'UTF-8'

