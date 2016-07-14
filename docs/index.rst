.. -*- mode: rst; fill-column: 80 -*-

===================================
NDEF Decoder and Encoder for Python
===================================

.. _ISCL: http://choosealicense.com/licenses/isc/
.. _GitHub: https://github.com/nfcpy/ndeflib
.. _PyPI: https://pypi.python.org/pypi/ndeflib

The ``ndeflib`` is a Python package for parsing and generating NFC Data Exchange
Format (NDEF) messages. It is licensed under the `ISCL`_, hosted on `GitHub`_
and soon be available on `PyPI`_.

.. code-block:: pycon

   >>> import ndef
   >>> hexstr = '9101085402656e48656c6c6f5101085402656e576f726c64'
   >>> octets = bytearray.fromhex(hexstr)
   >>> for record in ndef.message_decoder(octets): print(record)
   NDEF Text Record ID '' Text 'Hello' Language 'en' Encoding 'UTF-8'
   NDEF Text Record ID '' Text 'World' Language 'en' Encoding 'UTF-8'
   >>> message = [ndef.TextRecord("Hello"), ndef.TextRecord("World")]
   >>> b''.join(ndef.message_encoder(message)) == octets
   True

.. toctree::
   :caption: Documentation
   :maxdepth: 2

   Decoding and Encoding <ndef>
   Known Record Types <records>
   Adding Private Records <extending>

