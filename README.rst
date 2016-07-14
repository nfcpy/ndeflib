===============================
Parse or generate NDEF messages
===============================

.. image:: https://readthedocs.org/projects/ndeflib/badge/?version=latest
   :target: http://ndeflib.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/nfcpy/ndeflib.svg?branch=master
   :target: https://travis-ci.org/nfcpy/ndeflib
   :alt: Build Status

.. image:: https://codecov.io/gh/nfcpy/ndeflib/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/nfcpy/ndeflib
   :alt: Code Coverage

The ``ndeflib`` is an `ISC <http://choosealicense.com/licenses/isc/>`_-licensed Python package for parsing and generating NFC Data Exchange Format (NDEF) messages:

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

The ``ndeflib`` documentation can be found on `Read the Docs <https://ndeflib.readthedocs.io/>`_, the code on `GitHub <https://github.com/nfcpy/ndeflib>`_. It is `continously tested <https://travis-ci.org/nfcpy/ndeflib>`_ for Python 2.7 and 3.5 with pretty complete `test coverage <https://codecov.io/gh/nfcpy/ndeflib>`_.
