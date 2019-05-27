=======
History
=======

0.3.3 (2019-05-27)
------------------

* Support Python 3.7.

  * Python 3.7 mandates PEP 479 which made StopIteration within a
    generator raise RuntimeException.

  * The urllib.parse.quote function now follows RFC 3986 and does no
    longer convert the `~` character.

  * Importing ABCs from `collections` will no longer be possible with
    Python 3.8, must then import from `collections.abc`.

* WiFi and Bluetooth Records print attribute keys in sorted order to
  have consitent output in documentation embedded tests (doctest).

0.3.2 (2018-02-05)
------------------

* Bugfix to not encode the Certificate URI if it is None or empty,
  contributed by `Nick Knudson <https://github.com/nickaknudson>`_.

0.3.1 (2017-11-21)
------------------

* Fixes the signature record to encode lengths as 16-bits.

0.3.0 (2017-11-17)
------------------

* Support for decoding and encoding of the NFC Forum Signature Record,
  contributed by `Nick Knudson <https://github.com/nickaknudson>`_.

0.2.0 (2016-11-16)
------------------

* Wi-Fi Simple Configuration (WSC) and P2P records and attributes
  decode and encode added.

0.1.1 (2016-07-14)
------------------

* Development status set to Stable, required new release level as PyPI
  doesn't allow changing.

0.1.0 (2016-07-14)
------------------

* First release with complete documentation and pushed to PyPI.
* Fully implements decoding and encoding of generic records.
* Implements specific record decode/encode for NFC Forum Text, Uri,
  Smartposter, Device Information, Handover Request, Handover Select,
  Handover Mediation, Handover Initiate, and Handover Carrier Record.
* Tested to work with Python 2.7 and 3.5 with 100 % test coverage.
