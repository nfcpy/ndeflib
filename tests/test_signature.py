# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import _test_record_base


def pytest_generate_tests(metafunc):
    _test_record_base.generate_tests(metafunc)


class TestSignatureRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.signature.SignatureRecord
    ATTRIB = ("signature_type, hash_type, signature, signature_uri,"
              "certificate_format, certificate_store, certificate_uri")
# signature_type=None, hash_type="SHA-256", signature=None, signature_uri=None,
# certificate_format="X.509", certificate_store=[], certificate_uri=None
    test_init_args_data = [
        ((),
         (None, 'SHA-256', b'', '', 'X.509', [], '')),
    ]
    test_init_kwargs_data = [
        ((None, None, None, None, None, None, None),
         ("signature_type=None, hash_type=None, signature=None, "
          "signature_uri=None, certificate_format=None, "
          "certificate_store=None, certificate_uri=None")),
    ]
    test_init_fail_data = [
        ((None, None, None, 1, None, None, None),
         ".signature_uri accepts str or bytes, but not int"),
        ((None, None, None, None, None, None, 1),
         ".certificate_uri accepts str or bytes, but not int"),
        ((None, None, 1, None, None, None, None),
         ".signature may be bytes or bytearray, but not 'int'"),
        ((None, None, (2**16)*b'1', None, None, None, None),
         ".signature cannot be more than 2^16 octets, got 65536"),
        ((None, None, b'1', '1', None, None, None),
         " cannot set both signature and signature_uri"),
        ((None, None, None, (2**16)*'1', None, None, None),
         ".signature_uri cannot be more than 2^16 octets, got 65536"),
        ((None, None, None, None, None, [1], None),
         " certificate may be bytes or bytearray, but not 'int'"),
        ((None, None, None, None, None, [(2**16)*b'1'], None),
         " certificate cannot be more than 2^16 octets, got 65536"),
        ((None, None, None, None, None, [b'1' for x in range(2**4)], None),
         " certificate store cannot hold more than 2^4 certificates, got 16"),

    ]
    test_decode_valid_data = [
        ('20000200000000',
         (None, 'SHA-256', b'', '', 'X.509', [], '')),
        (('200b02473045022100a410c28fd9437fd24f6656f121e62bcc5f65e36257f5faadf'
          '68e3e83d40d481a0220335b1dff8d6fe722fcf7018be9684d2de5670b256fdfc02a'
          'a25bdae16f624b80000000'),
         ('ECDSA-P256', 'SHA-256',
          (b'0E\x02!\x00\xa4\x10\xc2\x8f\xd9C\x7f\xd2OfV\xf1!\xe6+\xcc_e\xe3bW'
           b'\xf5\xfa\xad\xf6\x8e>\x83\xd4\rH\x1a\x02 3[\x1d\xff\x8do\xe7"\xfc'
           b'\xf7\x01\x8b\xe9hM-\xe5g\x0b%o\xdf\xc0*\xa2[\xda\xe1obK\x80'),
          '', 'X.509', [], '')),
    ]
    test_decode_error_data = [
        ('10000200000000', "decoding of version 16 is not supported"),
    ]
    test_decode_relax = None
    test_encode_error = None
    test_format_args_data = [
        ((),
         "None, 'SHA-256', b'', '', X.509, [], ''"),
        (('ECDSA-P256', 'SHA-256',
          (b'0E\x02!\x00\xa4\x10\xc2\x8f\xd9C\x7f\xd2OfV\xf1!\xe6+\xcc_e\xe3bW'
           b'\xf5\xfa\xad\xf6\x8e>\x83\xd4\rH\x1a\x02 3[\x1d\xff\x8do\xe7"\xfc'
           b'\xf7\x01\x8b\xe9hM-\xe5g\x0b%o\xdf\xc0*\xa2[\xda\xe1obK\x80'),
          '', 'X.509', [], ''),
         ('\'ECDSA-P256\', \'SHA-256\', b\'0E\\x02!\\x00\\xa4\\x10\\xc2\\x8f\\'
          'xd9C\\x7f\\xd2OfV\\xf1!\\xe6+\\xcc_e\\xe3bW\\xf5\\xfa\\xad\\xf6\\x8'
          'e>\\x83\\xd4\\rH\\x1a\\x02 3[\\x1d\\xff\\x8do\\xe7"\\xfc\\xf7\\x01'
          '\\x8b\\xe9hM-\\xe5g\\x0b%o\\xdf\\xc0*\\xa2[\\xda\\xe1obK\\x80\', '
          '\'\', X.509, [], \'\'')),
    ]
    test_format_str_data = [
        ((),
         ("NDEF Signature Record ID '' Signature RTD "
          "'Version(major=2, minor=0)'")),
        (('ECDSA-P256', 'SHA-256',
          (b'0E\x02!\x00\xa4\x10\xc2\x8f\xd9C\x7f\xd2OfV\xf1!\xe6+\xcc_e\xe3bW'
           b'\xf5\xfa\xad\xf6\x8e>\x83\xd4\rH\x1a\x02 3[\x1d\xff\x8do\xe7"\xfc'
           b'\xf7\x01\x8b\xe9hM-\xe5g\x0b%o\xdf\xc0*\xa2[\xda\xe1obK\x80'),
          '', 'X.509', [], ''),
         ('NDEF Signature Record ID \'\' Signature RTD '
          '\'Version(major=2, minor=0)\' Signature Type '
          '\'ECDSA-P256\' Hash Type \'SHA-256\'')),
    ]
