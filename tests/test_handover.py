# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import pytest
import _test_record_base

def pytest_generate_tests(metafunc):
    _test_record_base.generate_tests(metafunc)

from ndef import message_decoder, message_encoder
from ndef.record import Record, DecodeError, EncodeError
from ndef.handover import AlternativeCarrierRecord
from ndef.handover import CollisionResolutionRecord
from ndef.handover import ErrorRecord
from ndef.handover import HandoverRequestRecord
from ndef.handover import HandoverSelectRecord
from ndef.handover import HandoverMediationRecord
from ndef.handover import HandoverInitiateRecord
from ndef.handover import HandoverCarrierRecord

class TestAlternativeCarrierRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.handover.AlternativeCarrierRecord
    ATTRIB = ("carrier_power_state, carrier_data_reference,"
              "auxiliary_data_reference")

    test_init_args_data = [
        (('inactive', ''), ('inactive', '', [])),
        (('active', ''), ('active', '', [])),
        (('activating', ''), ('activating', '', [])),
        (('unknown', ''), ('unknown', '', [])),
        ((0, 'c1'), ('inactive', 'c1', [])),
        ((1, 'c2', 'a1'), ('active', 'c2', ['a1'])),
        ((2, 'c3', 'a1', 'a2'), ('activating', 'c3', ['a1', 'a2'])),
        ((3, 'c4', 'a1', 'a2', 'a3'), ('unknown', 'c4', ['a1', 'a2', 'a3'])),
    ]
    test_init_kwargs_data = [
        (('active', 'c1'), "cps='active', cdr='c1'"),
    ]
    test_init_fail_data = [
        (('a', ''),
         (".carrier_power_state accepts index or one of ('inactive'," +
          " 'active', 'activating', 'unknown'), not 'a'")),
        ((4, ''),
         (".carrier_power_state accepts index or one of ('inactive'," +
          " 'active', 'activating', 'unknown'), not 4")),
        ((0, 1),
         ' set_carrier_data_reference() accepts str or bytes, but not int'),
        ((0, '', 1),
         ' set_auxiliary_data_reference() accepts str or bytes, but not int'),
    ]
    test_format_args_data = [
        ((0, ''), "'inactive', ''"),
        ((1, 'cdr'), "'active', 'cdr'"),
        ((2, 'cdr', 'aux'), "'activating', 'cdr', 'aux'"),
        ((3, 'cdr', 'aux1', 'aux2'), "'unknown', 'cdr', 'aux1', 'aux2'"),
    ]
    test_format_str_data = [
        ((0, ''),
         "NDEF Handover Alternative Carrier Record ID ''"\
         " Carrier Reference '' Power State 'inactive'"\
         " Auxiliary Data []"),
        ((1, 'cdr'),
         "NDEF Handover Alternative Carrier Record ID ''"\
         " Carrier Reference 'cdr' Power State 'active'"\
         " Auxiliary Data []"),
        ((2, 'cdr', 'aux'),
         "NDEF Handover Alternative Carrier Record ID ''"\
         " Carrier Reference 'cdr' Power State 'activating'"\
         " Auxiliary Data ['aux']"),
        ((3, 'cdr', 'aux1', 'aux2'),
         "NDEF Handover Alternative Carrier Record ID ''"\
         " Carrier Reference 'cdr' Power State 'unknown'"\
         " Auxiliary Data ['aux1', 'aux2']"),
    ]
    test_decode_valid_data = [
        ('000000', ('inactive', '')),
        ('010000', ('active', '')),
        ('020000', ('activating', '')),
        ('030000', ('unknown', '')),
        ('000363647200', (0, 'cdr')),
        ('01036364720100', (1, 'cdr', '')),
        ('0203636472010461647231', (2, 'cdr', 'adr1')),
        ('03016302026131026132', (3, 'c', 'a1', 'a2')),
    ]
    test_decode_relax_data = [
        ('00026331', ('inactive', 'c1')),
    ]
    test_decode_error_data = [
        ('00', 'decode is missing carrier data reference length'),
        ('0001', "need 1 more octet to unpack format 'B+'"),
        ('0000', 'decode is missing auxiliary data reference count'),
        ('000001', 'decode is missing auxiliary data reference length'),
        ('00000101', "need 1 more octet to unpack format 'B+'"),
        ('00000000', 'payload has 1 octet left after decode'),
        ('0000000000', 'payload has 2 octet left after decode'),
    ]
    test_encode_error = None

class TestCollisionResolutionRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.handover.CollisionResolutionRecord
    ATTRIB = "random_number"

    test_init_args_data = [
        ((), (0,)),
        ((100,), (100,)),
        ((b'\x00\xff',), (255,)),
    ]
    test_init_kwargs_data = [
        ((100,), "random_number=100"),
    ]
    test_init_fail_data = [
        ((1.2,), ".random_number expects an int or bytes, but not float"),
        ((65536,), ".random_number must be 0 <= x <= 65535, got 65536"),
        ((-1,), ".random_number must be 0 <= x <= 65535, got -1"),
    ]
    test_format_args_data = [
        ((100,), "100"),
    ]
    test_format_str_data = [
        ((99,),
         "NDEF Handover Collision Resolution Record ID ''"\
         " Random Number 99"),
    ]
    test_decode_valid_data = [
        ('0000', (0x0000,)),
        ('0010', (0x0010,)),
        ('8000', (0x8000,)),
        ('FFFF', (0xFFFF,)),
    ]
    test_decode_relax_data = [
        ('000000', (0x0000,)),
    ]
    test_decode_error = None
    test_encode_error = None

class TestErrorRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.handover.ErrorRecord
    ATTRIB = "error_reason, error_data"

    test_init_args_data = [
        ((1, 100), (1, 100)),
        ((2, 500), (2, 500)),
        ((3, 200), (3, 200)),
        ((0, b'ab'), (0, b'ab')),
        ((4, b'cd'), (4, b'cd')),
    ]
    test_init_kwargs_data = [
        ((1, 100), "error_reason=1, error_data=100"),
    ]
    test_init_fail = None
    test_format_args_data = [
        ((1, 100), "1, 100"),
    ]
    test_format_str_data = [
        ((1, 100), "NDEF Handover Error Record ID '' Error "\
         "'temporarily out of memory, may retry after 100 milliseconds'"),
        ((2, 500), "NDEF Handover Error Record ID '' Error "\
         "'permanently out of memory, may retry with at most 500 octets'"),
        ((3, 200), "NDEF Handover Error Record ID '' Error "\
          "'carrier specific error, may retry after 200 milliseconds'"),
        ((0, b'ab'), "NDEF Handover Error Record ID '' Error "\
         "'Reason 0 Data 6162'"),
        ((4, b'cd'), "NDEF Handover Error Record ID '' Error "\
         "'Reason 4 Data 6364'"),
    ]
    test_decode_valid_data = [
        ('0111', (1, 0x11)),
        ('0200000012', (2, 0x12)),
        ('0313', (3, 0x13)),
        ('0400', (4, b'\x00')),
    ]
    test_decode_error_data = [
        ('01', 'payload needs 1 octet error data for reason 1'),
        ('02', 'payload needs 4 octet error data for reason 2'),
        ('03', 'payload needs 1 octet error data for reason 3'),
        ('010000000000', 'payload has 4 octet left after decode'),
        ('020000000000', 'payload has 1 octet left after decode'),
        ('030000000000', 'payload has 4 octet left after decode'),
        ('00', "can't decode reserved error reason 0"),
    ]
    test_decode_relax_data = [
        ('010000000000', (1, 0)),
        ('020000000000', (2, 0)),
        ('030000000000', (3, 0)),
    ]
    test_encode_error_data = [
        ((0, b'a'), "can't encode reserved error reason 0"),
        ((1, 256), "ubyte format requires 0 <= number <= 255"),
    ]

class _TestHandoverRecordBase(_test_record_base._TestRecordBase):
    def test_unknown_records_decode(self):
        octets = bytearray.fromhex('11d20a00746578742f706c61696e')
        record = self.RECORD(0x11)
        record.unknown_records.append(ndef.Record('text/plain'))
        assert self.RECORD._decode_payload(octets, 'strict') == record

    def test_unknown_records_encode(self):
        record = self.RECORD(0x11)
        record.unknown_records.append(ndef.Record('text/plain'))
        assert record.data == bytearray.fromhex('11d20a00746578742f706c61696e')

class TestHandoverRequestRecord(_TestHandoverRecordBase):
    RECORD = ndef.handover.HandoverRequestRecord
    ATTRIB = "hexversion, version_info, collision_resolution_number,"\
             "alternative_carriers"

    test_init_args_data = [
        ((0x10,), (0x10, (1,0), None, [])),
        ((0x12, 100), (0x12, (1,2), 100, [])),
        ((0x12, 100, (1, 'cdr')),
         (0x12, (1,2), 100, [
             ndef.handover.AlternativeCarrierRecord('active', 'cdr')])),
        ((0x12, 100, (1, 'cdr1'), (1, 'cdr2')),
         (0x12, (1,2), 100, [
             ndef.handover.AlternativeCarrierRecord('active', 'cdr1'),
             ndef.handover.AlternativeCarrierRecord('active', 'cdr2')])),
    ]
    test_init_kwargs_data = [
        ((0x12, 1001), "version='1.2', crn=1001"),
    ]
    test_init_fail_data = [
        ((1.0,), " version argument expects int or str, but not float"),
        (("a",), " can't parse 'a' as a version string"),
        (("",), " can't parse '' as a version string"),
    ]
    test_format_args_data = [
        ((0x11,), "'1.1', None"),
        ((0x12, 1001), "'1.2', 1001"),
        ((0x13, 1001, (1, 'cdr')), "'1.3', 1001, ('active', 'cdr')"),
    ]
    test_format_str_data = [
        ((0x12, 1001),
         "NDEF Handover Request Record ID '' Version '1.2'"),
        ((0x13, 1001, (1, 'cdr')),
         "NDEF Handover Request Record ID '' Version '1.3'"\
         " Carrier Reference 'cdr' Power State 'active' Auxiliary Data []"),
        ((0x14, 1001, (1, 'cdr1'), (0, 'cdr2')),
         "NDEF Handover Request Record ID '' Version '1.4'"\
         " Carrier Reference 'cdr1' Power State 'active' Auxiliary Data []"\
         " Carrier Reference 'cdr2' Power State 'inactive' Auxiliary Data []"),
    ]
    test_decode_valid_data = [
        ('10', (0x10,)),
        ('11', ('1.1',)),
        ('12d1020263721234', (0x12, 4660)),
        ('11d10204616301016300', (0x11, None, ('active', 'c'))),
        ('1291020263721234510204616301016300', (0x12, 4660, ('active', 'c'))),
        ('139102026372123451020a616302016302026131026132',
         (0x13, 4660, ('activating', 'c', 'a1', 'a2'))),
    ]
    test_decode_relax_data = [
        ('1211020263721234510204616301016300', (0x12, 4660, (1, 'c'))),
        ('1211020263721234110204616301016300', (0x12, 4660, (1, 'c'))),
        ('121102026372123411020561630101630000', (0x12, 4660, (1, 'c'))),
        ('12110202637212341102066163010163000000', (0x12, 4660, (1, 'c'))),
    ]
    test_decode_error_data = [
        ('12', "can't decode version 1.2 without collision resolution record"),
    ]
    test_encode_error_data = [
        ((18,), "can't encode version 1.2 without collision resolution record"),
    ]

class TestHandoverSelectRecord(_TestHandoverRecordBase):
    RECORD = ndef.handover.HandoverSelectRecord
    ATTRIB = "hexversion, version_info, error, alternative_carriers"

    test_init_args_data = [
        ((0x10,), (0x10, (1,0), None, [])),
        ((0x12, (1, 100)),
         (0x12, (1,2), ndef.handover.ErrorRecord(1, 100), [])),
        ((0x12, (1, 100), (1, 'cdr')),
         (0x12, (1,2), ndef.handover.ErrorRecord(1, 100), [
             ndef.handover.AlternativeCarrierRecord('active', 'cdr')])),
        ((0x12, (1, 100), (1, 'cdr1'), (1, 'cdr2')),
         (0x12, (1,2), ndef.handover.ErrorRecord(1, 100), [
             ndef.handover.AlternativeCarrierRecord('active', 'cdr1'),
             ndef.handover.AlternativeCarrierRecord('active', 'cdr2')])),
    ]
    test_init_kwargs_data = [
        ((0x12, (1, 100)), "version='1.2', error=(1, 100)"),
    ]
    test_init_fail_data = [
        (("a",), " can't parse 'a' as a version string"),
        ((1.0,), " version argument expects int or str, but not float"),
        ((0x11, "a"), " can't initialize error attribute from 'a'"),
    ]
    test_format_args_data = [
        ((0x11,), "'1.1', None"),
        ((0x12, (1, 100)), "'1.2', (1, 100)"),
        ((0x13, (1, 100), (1, 'cdr')), "'1.3', (1, 100), ('active', 'cdr')"),
    ]
    test_format_str_data = [
        ((0x11,),
         "NDEF Handover Select Record ID '' Version '1.1'"),
        ((0x12, (1, 5)),
         "NDEF Handover Select Record ID '' Version '1.2'"\
         " Error 'temporarily out of memory, may retry after 5 milliseconds'"),
        ((0x13, (1, 5), (1, 'cdr')),
         "NDEF Handover Select Record ID '' Version '1.3'"\
         " Carrier Reference 'cdr' Power State 'active' Auxiliary Data []"\
         " Error 'temporarily out of memory, may retry after 5 milliseconds'"),
        ((0x13, (1, 5), (1, 'cdr1'), (0, 'cdr2')),
         "NDEF Handover Select Record ID '' Version '1.3'"\
         " Carrier Reference 'cdr1' Power State 'active' Auxiliary Data []"\
         " Carrier Reference 'cdr2' Power State 'inactive' Auxiliary Data []"\
         " Error 'temporarily out of memory, may retry after 5 milliseconds'"),
    ]
    test_decode_valid_data = [
        ('10', (0x10,)),
        ('11', ('1.1',)),
        ('12d103026572720110', (0x12, (1, 16))),
        ('12d103056572720200000100', (0x12, (2, 256))),
        ('11d10204616301016300', (0x11, None, ('active', 'c'))),
        ('129102046163010163005103026572720110', (0x12, (1, 16), (1, 'c'))),
        ('1391020a6163020163020261310261325103056572720200000100',
         (0x13, (2, 256), ('activating', 'c', 'a1', 'a2'))),
    ]
    test_decode_relax_data = [
        ('12 1103026572720100 110204616301016300', (0x12, (1, 0), (1, 'c'))),
    ]
    test_decode_error = None
    test_encode_error_data = [
        ((0x11, (1, 2)), "can't encode error record for version 1.1"),
    ]

class TestHandoverMediationRecord(_TestHandoverRecordBase):
    RECORD = ndef.handover.HandoverMediationRecord
    ATTRIB = "hexversion, version_info, alternative_carriers"

    test_init_args_data = [
        ((0x10,), (0x10, (1,0), [])),
        ((0x12,), (0x12, (1,2), [])),
        ((0x12, (1, 'cdr')), (0x12, (1,2), [
            ndef.handover.AlternativeCarrierRecord('active', 'cdr')])),
        ((0x12, (1, 'cdr1'), (1, 'cdr2')), (0x12, (1,2), [
            ndef.handover.AlternativeCarrierRecord('active', 'cdr1'),
            ndef.handover.AlternativeCarrierRecord('active', 'cdr2')])),
    ]
    test_init_kwargs_data = [
        ((0x12,), "version='1.2'"),
    ]
    test_init_fail_data = [
        (("a",), " can't parse 'a' as a version string"),
        ((1.0,), " version argument expects int or str, but not float"),
    ]
    test_format_args_data = [
        ((0x11,), "'1.1'"),
        ((0x13, (1, 'cdr')), "'1.3', ('active', 'cdr')"),
    ]
    test_format_str_data = [
        ((0x13,),
         "NDEF Handover Mediation Record ID '' Version '1.3'"),
        ((0x13, (1, 'cdr')),
         "NDEF Handover Mediation Record ID '' Version '1.3'"\
         " Carrier Reference 'cdr' Power State 'active' Auxiliary Data []"),
        ((0x13, (1, 'cdr1'), (0, 'cdr2')),
         "NDEF Handover Mediation Record ID '' Version '1.3'"\
         " Carrier Reference 'cdr1' Power State 'active' Auxiliary Data []"\
         " Carrier Reference 'cdr2' Power State 'inactive' Auxiliary Data []"),
    ]
    test_decode_valid_data = [
        ('10', (0x10,)),
        ('11', ('1.1',)),
        ('11d10204616301016300', (0x11, ('active', 'c'))),
        ('13d1020a616302016302026131026132', (0x13, (2, 'c', 'a1', 'a2'))),
    ]
    test_decode_error = None
    test_decode_relax = None
    test_encode_error = None

class TestHandoverInitiateRecord(_TestHandoverRecordBase):
    RECORD = ndef.handover.HandoverInitiateRecord
    ATTRIB = "hexversion, version_info, alternative_carriers"

    test_init_args_data = [
        ((0x10,), (0x10, (1,0), [])),
        ((0x12,), (0x12, (1,2), [])),
        ((0x12, (1, 'cdr')), (0x12, (1,2), [
            ndef.handover.AlternativeCarrierRecord('active', 'cdr')])),
        ((0x12, (1, 'cdr1'), (1, 'cdr2')), (0x12, (1,2), [
            ndef.handover.AlternativeCarrierRecord('active', 'cdr1'),
            ndef.handover.AlternativeCarrierRecord('active', 'cdr2')])),
    ]
    test_init_kwargs_data = [
        ((0x12,), "version='1.2'"),
    ]
    test_init_fail_data = [
        (("a",), " can't parse 'a' as a version string"),
        ((1.0,), " version argument expects int or str, but not float"),
    ]
    test_format_args_data = [
        ((0x11,), "'1.1'"),
        ((0x13, (1, 'cdr')), "'1.3', ('active', 'cdr')"),
    ]
    test_format_str_data = [
        ((0x13,),
         "NDEF Handover Initiate Record ID '' Version '1.3'"),
        ((0x13, (1, 'cdr')),
         "NDEF Handover Initiate Record ID '' Version '1.3'"\
         " Carrier Reference 'cdr' Power State 'active' Auxiliary Data []"),
        ((0x13, (1, 'cdr1'), (0, 'cdr2')),
         "NDEF Handover Initiate Record ID '' Version '1.3'"\
         " Carrier Reference 'cdr1' Power State 'active' Auxiliary Data []"\
         " Carrier Reference 'cdr2' Power State 'inactive' Auxiliary Data []"),
    ]
    test_decode_valid_data = [
        ('10', (0x10,)),
        ('11', ('1.1',)),
        ('11d10204616301016300', (0x11, ('active', 'c'))),
        ('13d1020a616302016302026131026132', (0x13, (2, 'c', 'a1', 'a2'))),
    ]
    test_decode_error = None
    test_decode_relax = None
    test_encode_error = None

class TestHandoverCarrierRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.handover.HandoverCarrierRecord
    ATTRIB = "carrier_type, carrier_data"

    test_init_args_data = [
        ((), ('', bytearray(b''))),
        (('ab/cd',), ('ab/cd', bytearray(b''))),
        (('ab/cd', '\0\0\0'), ('ab/cd', bytearray(3))),
        (('ab/cd', b'\0\0\0'), ('ab/cd', bytearray(3))),
        (('ab/cd', bytearray(3)), ('ab/cd', bytearray(3))),
    ]
    test_init_kwargs_data = [
        (('ab/cd',), "carrier_type='ab/cd'"),
        (('ab/cd', b'123'), "carrier_type='ab/cd', carrier_data=b'123'"),
        (('ab/cd', None, 'ref'), "carrier_type='ab/cd', reference='ref'"),
    ]
    test_init_fail_data = [
        ((int(),),
         " record type string may be str or bytes, but not int"),
        (('ab',),
         " can not convert the record type string 'ab'"),
        (('ab/cd', 1),
         " carrier data may be sequence type or None, but not int"),
        (('ab/cd', 1.0),
         " carrier data may be sequence type or None, but not float"),
    ]
    test_format_args_data = [
        (('ab/cd', None), "'ab/cd', bytearray(b'')"),
        (('ab/cd', b'123'), "'ab/cd', bytearray(b'123')"),
    ]
    test_format_str_data = [
        (('ab/cd', None),
         "NDEF Handover Carrier Record ID '' CARRIER 'ab/cd' DATA 0 byte"),
        (('ab/cd', b'1'),
         "NDEF Handover Carrier Record ID '' CARRIER 'ab/cd' DATA 1 byte '31'"),
        (('ab/cd', 20*b'1'),
         "NDEF Handover Carrier Record ID '' CARRIER 'ab/cd' DATA 20 byte "\
         "'31313131313131313131' ... 10 more"),
    ]
    test_decode_valid_data = [
        ('0000', ()),
        ('020561622f6364', ('ab/cd',)),
        ('020561622f6364000102', ('ab/cd', b'\0\1\2')),
    ]
    test_decode_error_data = [
        ('0001', "carrier type length 1 exceeds payload size"),
    ]
    test_decode_relax = None
    test_encode_error = None

def test_handover_request_record_attributes():
    record = HandoverRequestRecord()
    assert record.collision_resolution_number is None
    record.collision_resolution_number = 0x4321
    assert record.collision_resolution_number == 0x4321
    record.collision_resolution_number = 0x1234
    assert record.collision_resolution_number == 0x1234
    record.add_alternative_carrier('active', 'wifi', 'a1', 'a2')
    record.add_alternative_carrier('inactive', 'bt31', 'a3')
    record.unknown_records.append(Record('text/plain', 'txt', 'Hello'))
    octets = b''.join(message_encoder([record]))
    record = list(message_decoder(octets))[0]
    assert isinstance(record, HandoverRequestRecord)
    assert record.type == 'urn:nfc:wkt:Hr'
    assert record.name == ''
    assert record.hexversion == 0x13
    assert record.version_info == (1, 3)
    assert record.version_string == "1.3"
    assert record.collision_resolution_number == 0x1234
    assert len(record.alternative_carriers) == 2
    assert len(record.alternative_carriers[0].auxiliary_data_reference) == 2
    assert len(record.alternative_carriers[1].auxiliary_data_reference) == 1
    assert record.alternative_carriers[0].carrier_power_state == 'active'
    assert record.alternative_carriers[0].carrier_data_reference == 'wifi'
    assert record.alternative_carriers[0].auxiliary_data_reference[0] == 'a1'
    assert record.alternative_carriers[0].auxiliary_data_reference[1] == 'a2'
    assert record.alternative_carriers[1].carrier_power_state == 'inactive'
    assert record.alternative_carriers[1].carrier_data_reference == 'bt31'
    assert record.alternative_carriers[1].auxiliary_data_reference[0] == 'a3'
    assert len(record.unknown_records) == 1
    assert record.unknown_records[0].type == 'text/plain'
    assert record.unknown_records[0].name == 'txt'
    assert record.unknown_records[0].data == b'Hello'

def test_handover_select_record_attributes():
    record = HandoverSelectRecord()
    assert record.error is None
    record.set_error(2, 200)
    record.set_error(1, 100)
    record.add_alternative_carrier('active', 'wifi', 'a1', 'a2')
    record.add_alternative_carrier('inactive', 'bt31', 'a3')
    record.unknown_records.append(Record('text/plain', 'txt', 'Hello'))
    octets = b''.join(message_encoder([record]))
    record = list(message_decoder(octets))[0]
    assert isinstance(record, HandoverSelectRecord)
    assert record.type == 'urn:nfc:wkt:Hs'
    assert record.name == ''
    assert record.hexversion == 0x13
    assert record.version_info == (1, 3)
    assert record.version_string == "1.3"
    assert record.error is not None
    assert record.error.error_reason == 1
    assert record.error.error_data == 100
    assert len(record.alternative_carriers) == 2
    assert len(record.alternative_carriers[0].auxiliary_data_reference) == 2
    assert len(record.alternative_carriers[1].auxiliary_data_reference) == 1
    assert record.alternative_carriers[0].carrier_power_state == 'active'
    assert record.alternative_carriers[0].carrier_data_reference == 'wifi'
    assert record.alternative_carriers[0].auxiliary_data_reference[0] == 'a1'
    assert record.alternative_carriers[0].auxiliary_data_reference[1] == 'a2'
    assert record.alternative_carriers[1].carrier_power_state == 'inactive'
    assert record.alternative_carriers[1].carrier_data_reference == 'bt31'
    assert record.alternative_carriers[1].auxiliary_data_reference[0] == 'a3'
    assert len(record.unknown_records) == 1
    assert record.unknown_records[0].type == 'text/plain'
    assert record.unknown_records[0].name == 'txt'
    assert record.unknown_records[0].data == b'Hello'

def test_handover_mediation_record_attributes():
    record = HandoverMediationRecord()
    record.add_alternative_carrier('active', 'wifi', 'a1', 'a2')
    record.add_alternative_carrier('inactive', 'bt31', 'a3')
    record.unknown_records.append(Record('text/plain', 'txt', 'Hello'))
    octets = b''.join(message_encoder([record]))
    record = list(message_decoder(octets))[0]
    assert isinstance(record, HandoverMediationRecord)
    assert record.type == 'urn:nfc:wkt:Hm'
    assert record.name == ''
    assert record.hexversion == 0x13
    assert record.version_info == (1, 3)
    assert record.version_string == "1.3"
    assert len(record.alternative_carriers) == 2
    assert len(record.alternative_carriers[0].auxiliary_data_reference) == 2
    assert len(record.alternative_carriers[1].auxiliary_data_reference) == 1
    assert record.alternative_carriers[0].carrier_power_state == 'active'
    assert record.alternative_carriers[0].carrier_data_reference == 'wifi'
    assert record.alternative_carriers[0].auxiliary_data_reference[0] == 'a1'
    assert record.alternative_carriers[0].auxiliary_data_reference[1] == 'a2'
    assert record.alternative_carriers[1].carrier_power_state == 'inactive'
    assert record.alternative_carriers[1].carrier_data_reference == 'bt31'
    assert record.alternative_carriers[1].auxiliary_data_reference[0] == 'a3'
    assert len(record.unknown_records) == 1
    assert record.unknown_records[0].type == 'text/plain'
    assert record.unknown_records[0].name == 'txt'
    assert record.unknown_records[0].data == b'Hello'

def test_handover_initiate_record_attributes():
    record = HandoverInitiateRecord()
    record.add_alternative_carrier('active', 'wifi', 'a1', 'a2')
    record.add_alternative_carrier('inactive', 'bt31', 'a3')
    record.unknown_records.append(Record('text/plain', 'txt', 'Hello'))
    octets = b''.join(message_encoder([record]))
    record = list(message_decoder(octets))[0]
    assert isinstance(record, HandoverInitiateRecord)
    assert record.type == 'urn:nfc:wkt:Hi'
    assert record.name == ''
    assert record.hexversion == 0x13
    assert record.version_info == (1, 3)
    assert record.version_string == "1.3"
    assert len(record.alternative_carriers) == 2
    assert len(record.alternative_carriers[0].auxiliary_data_reference) == 2
    assert len(record.alternative_carriers[1].auxiliary_data_reference) == 1
    assert record.alternative_carriers[0].carrier_power_state == 'active'
    assert record.alternative_carriers[0].carrier_data_reference == 'wifi'
    assert record.alternative_carriers[0].auxiliary_data_reference[0] == 'a1'
    assert record.alternative_carriers[0].auxiliary_data_reference[1] == 'a2'
    assert record.alternative_carriers[1].carrier_power_state == 'inactive'
    assert record.alternative_carriers[1].carrier_data_reference == 'bt31'
    assert record.alternative_carriers[1].auxiliary_data_reference[0] == 'a3'
    assert len(record.unknown_records) == 1
    assert record.unknown_records[0].type == 'text/plain'
    assert record.unknown_records[0].name == 'txt'
    assert record.unknown_records[0].data == b'Hello'

handover_request_messages = [
    ('d102014872 11',
     [ndef.HandoverRequestRecord('1.1')]),
    ('91020a4872 11 d10204616301013100 5a030201612f62310001',
     [ndef.HandoverRequestRecord('1.1', None, (1, '1')),
      ndef.Record('a/b', '1', b'\x00\x01')]),
    ('d102084872 12 d1020263721234',
     [ndef.HandoverRequestRecord('1.2', 0x1234)]),
    ('9102114872 12 91020263721234 510204616301013100 5a030201612f62310001',
     [ndef.HandoverRequestRecord('1.2', 0x1234, (1, '1')),
      ndef.Record('a/b', '1', b'\x00\x01')]),
    ('9102114872 12 91020263721234 510204616301013100 590205014863310203612f62',
     [ndef.HandoverRequestRecord('1.2', 0x1234, (1, '1')),
      ndef.HandoverCarrierRecord('a/b', None, '1')]),
]

class TestHandoverRequestMessage:
    @pytest.mark.parametrize("encoded, message", handover_request_messages)
    def test_decode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_decoder(octets)))
        assert list(ndef.message_decoder(octets)) == message

    @pytest.mark.parametrize("encoded, message", handover_request_messages)
    def test_encode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_encoder(message)))
        assert b''.join(list(ndef.message_encoder(message))) == octets

handover_select_messages = [
    ('d102014873 13',
     [ndef.HandoverSelectRecord('1.3')]),
    ('d102094873 13 d1030265727201ff',
     [ndef.HandoverSelectRecord('1.3', (1, 255))]),
    ('91020a4873 13 d10204616301013100 5a030201612f62310001',
     [ndef.HandoverSelectRecord('1.3', None, (1, '1')),
      ndef.Record('a/b', '1', b'\x00\x01')]),
    ('9102124873 13 91020461630101310051030265727201ff 5a030201612f62310001',
     [ndef.HandoverSelectRecord('1.3', (1, 255), (1, '1')),
      ndef.Record('a/b', '1', b'\x00\x01')]),
]

class TestHandoverSelectMessage:
    @pytest.mark.parametrize("encoded, message", handover_select_messages)
    def test_decode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_decoder(octets)))
        assert list(ndef.message_decoder(octets)) == message

    @pytest.mark.parametrize("encoded, message", handover_select_messages)
    def test_encode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_encoder(message)))
        assert b''.join(list(ndef.message_encoder(message))) == octets

handover_mediation_messages = [
    ('d10201486d 13',
     [ndef.HandoverMediationRecord('1.3')]),
    ('91020a486d 13 d10204616301013100 5a030201612f62310001',
     [ndef.HandoverMediationRecord('1.3', (1, '1')),
      ndef.Record('a/b', '1', b'\x00\x01')]),
]

class TestHandoverMediationMessage:
    @pytest.mark.parametrize("encoded, message", handover_mediation_messages)
    def test_decode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_decoder(octets)))
        assert list(ndef.message_decoder(octets)) == message

    @pytest.mark.parametrize("encoded, message", handover_mediation_messages)
    def test_encode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_encoder(message)))
        assert b''.join(list(ndef.message_encoder(message))) == octets

handover_initiate_messages = [
    ('d102014869 13',
     [ndef.HandoverInitiateRecord('1.3')]),
    ('91020a4869 13 d10204616301013100 5a030201612f62310001',
     [ndef.HandoverInitiateRecord('1.3', (1, '1')),
      ndef.Record('a/b', '1', b'\x00\x01')]),
]

class TestHandoverInitiateMessage:
    @pytest.mark.parametrize("encoded, message", handover_initiate_messages)
    def test_decode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_decoder(octets)))
        assert list(ndef.message_decoder(octets)) == message

    @pytest.mark.parametrize("encoded, message", handover_initiate_messages)
    def test_encode(self, encoded, message):
        octets = bytes(bytearray.fromhex(encoded))
        print(list(ndef.message_encoder(message)))
        assert b''.join(list(ndef.message_encoder(message))) == octets

