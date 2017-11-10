.. -*- mode: rst; fill-column: 80 -*-

Signature Record
----------------

The NDEF Signature Record is a well-known record type defined by the
`NFC Forum`_. It contains three fields: a version field, a signature field and
a certificate field.

The version field is static. Currently this implementation only supports v2.0
of the NDEF Signature Record.

The signature field contains the signature type, the message hash type and
either the signature itself or a URI to the signature.

The certificate field contains the certificate format type, a certificate chain
store and an option URI to the next certificate in the chain.

.. class:: SignatureRecord(signature_type=None, hash_type='SHA-256', signature=b'', signature_uri='', certificate_format='X.509', certificate_store=[], certificate_uri='')

   The `SignatureRecord` class decodes or encodes an NDEF Signature Record.

   :param str signature_type: initial value for the `signature_type` attribute, default None
   :param str hash_type: initial value for the `hash_type` attribute, default 'SHA-256'
   :param bytes signature: initial value for the `signature` attribute, default b''
   :param str signature_uri: initial value for the `signature_uri` attribute, default ''
   :param str certificate_format: initial value for the `certificate_format` attribute, default 'X.509'
   :param list certificate_store: initial value for the `certificate_store` attribute, default []
   :param str certificate_uri: initial value for the `certificate_uri` attribute, default ''

   .. attribute:: type

      The Signature Record type is ``urn:nfc:wkt:Sig``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: version

      The version of the NDEF Signature Record.

   .. attribute:: signature_type

      The signature type used in the signature algorithm.

      >>> print('\n'.join([str(x[1]) for x in ndef.signature.SignatureRecord()._mapping_signature_type]))
      None
      RSASSA-PSS-1024
      RSASSA-PKCS1-v1_5-1024
      DSA-1024
      ECDSA-P192
      RSASSA-PSS-2048
      RSASSA-PKCS1-v1_5-2048
      DSA-2048
      ECDSA-P224
      ECDSA-K233
      ECDSA-B233
      ECDSA-P256

   .. attribute:: hash_type

      The hash type used in the signature algorithm.

      >>> print("\n".join([str(x[1]) for x in ndef.signature.SignatureRecord()._mapping_hash_type]))
      SHA-256

   .. attribute:: signature

      The signature (if not specified by `signature_uri`).

   .. attribute:: signature_uri

      The uniform resource identifier for the signature (if not specified by
      `signature`).

   .. attribute:: certificate_format

      The format of the certificates in the chain.

      >>> print("\n".join([str(x[1]) for x in ndef.signature.SignatureRecord()._mapping_certificate_format]))
      X.509
      M2M

   .. attribute:: certificate_store

      A list of certificates in the certificate chain.

   .. attribute:: certificate_uri

      The uniform resource identifier for the next certificate in the
      certificate chain.

   This is default usage:

   >>> signature_record = ndef.SignatureRecord(None, 'SHA-256', b'', '', 'X.509', [], '')

   This is a full example creating records, signing them and verifying them:

   >>> import ndef
   >>> import io
   >>> from cryptography.hazmat.backends import default_backend
   >>> from cryptography.hazmat.primitives import hashes
   >>> from cryptography.hazmat.primitives.asymmetric import ec
   >>> from cryptography.hazmat.primitives.asymmetric import utils
   >>> from cryptography.exceptions import InvalidSignature
   >>> from asn1crypto.algos import DSASignature

   >>> private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
   >>> public_key = private_key.public_key()

   >>> r1 = ndef.UriRecord("https://example.com")
   >>> r2 = ndef.TextRecord("TEST")

   >>> stream = io.BytesIO()
   >>> records = [r1, r2, ndef.SignatureRecord("ECDSA-P256", "SHA-256")]
   >>> encoder = ndef.message_encoder(records, stream)
   >>> for _ in range(len(records) - 1): next(encoder)

   >>> signature = private_key.sign(stream.getvalue(), ec.ECDSA(hashes.SHA256()))
   >>> records[-1].signature = DSASignature.load(signature, strict=True).to_p1363()
   >>> next(encoder)
   >>> octets = stream.getvalue()

   >>> records_verified = []
   >>> records_to_verify = []
   >>> known_types = {'urn:nfc:wkt:Sig': ndef.signature.SignatureRecord}
   >>> for record in ndef.message_decoder(octets, known_types=known_types):
   ...     if not record.type == 'urn:nfc:wkt:Sig':
   ...         records_to_verify.append(record)
   ...     else:
   ...         stream_to_verify = io.BytesIO()
   ...         encoder_to_verify = ndef.message_encoder(records_to_verify + [record], stream_to_verify)
   ...         for _ in range(len(records_to_verify)): next(encoder_to_verify)
   ...         try:
   ...             public_key.verify(DSASignature.from_p1363(record.signature).dump(), stream_to_verify.getvalue(), ec.ECDSA(hashes.SHA256()))
   ...             records_verified.extend(records_to_verify)
   ...             records_to_verify = []
   ...         except InvalidSignature:
   ...             pass

   >>> records_verified = list(ndef.message_decoder(b''.join(ndef.message_encoder(records_verified))))
