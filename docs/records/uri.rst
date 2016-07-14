.. -*- mode: rst; fill-column: 80 -*-

URI Record
----------	   

The NDEF URI Record is a well-known record type defined by the `NFC Forum`_. It
carries a, potentially abbreviated, UTF-8 encoded Internationalized Resource
Identifier (IRI) as defined by :rfc:`3987`. Abbreviation covers certain prefix
patterns that are compactly encoded as a single octet and automatically expanded
when decoding. The `UriRecord` class provides both access attributes for decoded
IRI as well as a converted URI (if a netloc part is present in the IRI).

.. class:: UriRecord(iri='')

   The `UriRecord` class decodes or encodes an NDEF URI Record. The
   `UriRecord.iri` attribute holds the expanded (if a valid abbreviation code
   was decoded) internationalized resource identifier (IRI). The `UriRecord.uri`
   attribute is a converted version of the IRI. Conversion is applied only for
   IRI's that split with a netloc component. A converted URI contains only ASCII
   characters with an IDNA encoded netloc component and percent-encoded path,
   query and fragment components.

   :param str iri: initial value for the `iri` attribute, default ''

   .. attribute:: type

      The URI Record type is ``urn:nfc:wkt:U``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: iri

      The decoded or set internationalized resource identifier, expanded if an
      abbreviation code was used in the record payload.

   .. attribute:: uri

      The uniform resource identifier translated from the `UriRecord.iri` attribute.

   >>> import ndef
   >>> record = ndef.UriRecord("http://www.hääyö.com/~user/")
   >>> record.iri
   'http://www.hääyö.com/~user/'
   >>> record.uri
   'http://www.xn--hy-viaa5g.com/%7Euser/'
   >>> record = ndef.UriRecord("http://www.example.com")
   >>> b''.join(ndef.message_encoder([record]))
   b'\xd1\x01\x0cU\x01example.com'

