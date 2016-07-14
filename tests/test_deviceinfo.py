# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import pytest
import _test_record_base

def pytest_generate_tests(metafunc):
    _test_record_base.generate_tests(metafunc)

class TestDeviceInformationRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.deviceinfo.DeviceInformationRecord
    ATTRIB = ("vendor_name, model_name, unique_name, uuid_string,"
              "version_string, undefined_data_elements")

    test_init_args_data = [
        (('Company', 'Device'),
         ('Company', 'Device', None, None, None, [])),
        (('Company', 'Device', 'Name',
          '123e4567-e89b-12d3-a456-426655440000', '10.1.5'),
         ('Company', 'Device', 'Name',
          '123e4567-e89b-12d3-a456-426655440000', '10.1.5', [])),
    ]
    test_init_kwargs_data = [
        (('Company', 'Device', 'Name',
          '123e4567-e89b-12d3-a456-426655440000', '10.1.5'),
         "vendor_name='Company', model_name='Device', unique_name='Name',"
         "uuid_string='123e4567-e89b-12d3-a456-426655440000',"
         "version_string='10.1.5'"),
    ]
    test_init_fail_data = [
        ((1, '', None, None, None),
         ".vendor_name accepts str or bytes, but not int"),
        (('', 1, None, None, None),
         ".model_name accepts str or bytes, but not int"),
        (('', '', 1, None, None),
         ".unique_name accepts str or bytes, but not int"),
        (('', '', None, 1, None),
         ".uuid_string accepts str or bytes, but not int"),
        (('', '', None, None, 1),
         ".version_string accepts str or bytes, but not int"),
        (('', '', None, None, None, ('', b'')),
         " data_type argument must be int, not 'str'"),
        (('', '', None, None, None, (255, 1)),
         " data_bytes may be bytes or bytearray, but not 'int'"),
        (('', '', None, None, None, (1, b'')),
         " data_type argument must be in range(5, 256), got 1"),
        (('', '', None, None, None, (255, 256*b'1')),
         " data_bytes can not be more than 255 octets, got 256"),
    ]
    test_decode_valid_data = [
        ('0007436f6d70616e790106446576696365',
         ("Company", 'Device')),
        ('0007436f6d70616e79 0106446576696365 02044e616d65',
         ("Company", 'Device', 'Name')),
        ('0007436f6d70616e79 0106446576696365 02044e616d65'
         '0310123e4567e89b12d3a456426655440000',
         ("Company", 'Device', 'Name', '123e4567-e89b-12d3-a456-426655440000')),
        ('0007436f6d70616e79 0106446576696365 02044e616d65 040631302e312e35',
         ("Company", 'Device', 'Name', None, '10.1.5')),
        ('0007436f6d70616e79 0106446576696365 02044e616d65 ff03313233',
         ("Company", 'Device', 'Name', None, None, (255, b'123'))),
    ]
    test_decode_error_data = [
        ('0100', "decoding requires the manufacturer and model name TLVs"),
    ]
    test_decode_relax = None
    test_encode_error_data = [
        (('', ''), "encoding requires that vendor and model name are set"),
    ]
    test_format_args_data = [
        (('Company', 'Device'),
         "'Company', 'Device', None, None, None"),
        (('Company', 'Device', 'Name', '123e4567e89b12d3a456426655440000',
          '1.1.1', (255, b'123'), (10, b'')),
         "'Company', 'Device', 'Name', '123e4567-e89b-12d3-a456-426655440000',"
         " '1.1.1', (255, b'123'), (10, b'')"),
    ]
    test_format_str_data = [
        (('Company', 'Device'),
         "NDEF Device Information Record ID '' Vendor 'Company' Model 'Device'"
        ),
        (('Company', 'Device', 'Name', '123e4567e89b12d3a456426655440000',
          '1.1.1', (255, b'123'), (10, b'')),
         "NDEF Device Information Record ID '' Vendor 'Company' Model 'Device'"
         " Name 'Name' UUID '123e4567-e89b-12d3-a456-426655440000'"
         " Version '1.1.1' DataElement(data_type=255, data_bytes=b'123')"
         " DataElement(data_type=10, data_bytes=b'')"
        ),
    ]

