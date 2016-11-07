# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import uuid
import ndef
import pytest

B = lambda s: ('' if ndef.record._PY2 else 'b') + s
U = lambda s: ('u' if ndef.record._PY2 else '') + s


class TestAttribute:
    @pytest.mark.parametrize("cls, octets, errstr", [
        (ndef.wifi.APChannel, '00',
         "data length is out of limits 2 <= 1 <= 2"),
        (ndef.wifi.APChannel, '000000',
         "data length is out of limits 2 <= 3 <= 2"),
    ])
    def test_decode_error(self, cls, octets, errstr):
        errstr = cls.__module__ + '.' + cls.__name__ + ' ' + errstr
        with pytest.raises(ndef.DecodeError) as excinfo:
            cls.decode(bytearray.fromhex(octets))
        assert str(excinfo.value) == errstr
        
    @pytest.mark.parametrize("cls, values, errstr", [
        (ndef.wifi.ModelName, (33*'a',),
         "data length is out of limits 0 <= 33 <= 32"),
    ])
    def test_encode_error(self, cls, values, errstr):
        errstr = cls.__module__ + '.' + cls.__name__ + ' ' + errstr
        with pytest.raises(ndef.EncodeError) as excinfo:
            cls(*values).encode()
        assert str(excinfo.value) == errstr
        

class TestAttribute_APChannel:
    @pytest.mark.parametrize("args, value", [
        ([1], 1), (['1'], 1), ([100], 100)
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.APChannel(*args)
        assert attr.value == value
        assert ndef.wifi.APChannel(attr).value == value

    def test_decode(self):
        assert ndef.wifi.APChannel.decode(b'\x00\x01').value == 1

    def test_encode(self):
        assert ndef.wifi.APChannel(1).encode() == b'\x00\x01'

    def test_format(self):
        attr = ndef.wifi.APChannel(6)
        assert "{:args}".format(attr) == "6"
        assert "{:data}".format(attr) == "6"
        assert "{}".format(attr) == "AP Channel 6"


class TestAttribute_AuthenticationType:
    @pytest.mark.parametrize("args, value", [
        ((1,), (1, 'Open',)),
        (('Open',), (1, 'Open',)),
        ((0x0022,), (34, 'WPA-Personal', 'WPA2-Personal')),
        (('WPA-Personal', 'WPA2-Personal'),
         (34, 'WPA-Personal', 'WPA2-Personal')),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.AuthenticationType(*args)
        assert attr.value == value
        assert ndef.wifi.AuthenticationType(attr).value == value

    @pytest.mark.parametrize("octets, value", [
        ('0001', (0x0001, 'Open',)),
        ('0002', (0x0002, 'WPA-Personal',)),
        ('0004', (0x0004, 'Shared',)),
        ('0008', (0x0008, 'WPA-Enterprise',)),
        ('0010', (0x0010, 'WPA2-Enterprise',)),
        ('0020', (0x0020, 'WPA2-Personal',)),
        ('0022', (0x0022, 'WPA-Personal', 'WPA2-Personal')),
    ])
    def test_decode(self, octets, value):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.AuthenticationType.decode(octets).value == value

    @pytest.mark.parametrize("octets, args", [
        ('0001', ('Open',)),
        ('0002', ('WPA-Personal',)),
        ('0004', ('Shared',)),
        ('0008', ('WPA-Enterprise',)),
        ('0010', ('WPA2-Enterprise',)),
        ('0020', ('WPA2-Personal',)),
        ('0022', ('WPA-Personal', 'WPA2-Personal')),
    ])
    def test_encode(self, octets, args):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.AuthenticationType(*args).encode() == octets

    def test_format(self):
        attr = ndef.wifi.AuthenticationType(0x0002)
        assert "{:args}".format(attr) == "2"
        assert "{:data}".format(attr) == "0x0002 ['WPA-Personal']"
        assert "{}".format(attr) == \
            "Authentication Type 0x0002 ['WPA-Personal']"
        attr = ndef.wifi.AuthenticationType(0x0022)
        assert "{:args}".format(attr) == "34"
        assert "{:data}".format(attr) == \
            "0x0022 ['WPA-Personal', 'WPA2-Personal']"
        assert "{}".format(attr) == \
            "Authentication Type 0x0022 ['WPA-Personal', 'WPA2-Personal']"

    def test_contains(self):
        attr = ndef.wifi.AuthenticationType(0x0022)
        assert 'WPA-Personal' in attr
        assert 'WPA2-Personal' in attr
        assert 'Open' not in attr


class TestAttribute_ConfigMethods:
    @pytest.mark.parametrize("args, value", [
        ((1,), (1, 'USBA')),
        (('USBA',), (1, 'USBA')),
        ((3,), (3, 'USBA', 'Ethernet')),
        (('USBA', 'Ethernet'), (3, 'USBA', 'Ethernet')),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.ConfigMethods(*args)
        assert attr.value == value
        assert ndef.wifi.ConfigMethods(attr).value == value

    @pytest.mark.parametrize("octets, value", [
        ('0001', (0x0001, 'USBA')),
        ('0002', (0x0002, 'Ethernet')),
        ('0004', (0x0004, 'Label')),
        ('0008', (0x0008, 'Display')),
        ('0010', (0x0010, 'External NFC Token')),
        ('0020', (0x0020, 'Integrated NFC Token')),
        ('0040', (0x0040, 'NFC Interface')),
        ('0080', (0x0080, 'Push Button')),
        ('0100', (0x0100, 'Keypad')),
        ('0280', (0x0280, 'Push Button', 'Virtual Push Button')),
        ('0480', (0x0480, 'Push Button', 'Physical Push Button')),
        ('2008', (0x2008, 'Display', 'Virtual Display PIN')),
        ('4008', (0x4008, 'Display', 'Physical Display PIN')),
    ])
    def test_decode(self, octets, value):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.ConfigMethods.decode(octets).value == value

    @pytest.mark.parametrize("octets, args", [
        ('0001', ('USBA',)),
        ('0002', ('Ethernet',)),
        ('0004', ('Label',)),
        ('0008', ('Display',)),
        ('0010', ('External NFC Token',)),
        ('0020', ('Integrated NFC Token',)),
        ('0040', ('NFC Interface',)),
        ('0080', ('Push Button',)),
        ('0100', ('Keypad',)),
        ('0280', ('Push Button', 'Virtual Push Button',)),
        ('0480', ('Push Button', 'Physical Push Button',)),
        ('2008', ('Display', 'Virtual Display PIN',)),
        ('4008', ('Display', 'Physical Display PIN',)),
    ])
    def test_encode(self, octets, args):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.ConfigMethods(*args).encode() == octets

    def test_format(self):
        attr = ndef.wifi.ConfigMethods(0x0002)
        assert "{:args}".format(attr) == "2"
        assert "{:data}".format(attr) == "0x0002 ['Ethernet']"
        assert "{}".format(attr) == "Configuration Methods 0x0002 ['Ethernet']"
        attr = ndef.wifi.ConfigMethods(0x0006)
        assert "{:args}".format(attr) == "6"
        assert "{:data}".format(attr) == "0x0006 ['Ethernet', 'Label']"
        assert "{}".format(attr) == \
            "Configuration Methods 0x0006 ['Ethernet', 'Label']"

    def test_contains(self):
        attr = ndef.wifi.ConfigMethods(0x06)
        assert 'Ethernet' in attr
        assert 'Label' in attr
        assert 'Push Button' not in attr


class TestAttribute_DeviceName:
    @pytest.mark.parametrize("args, value", [
        (['ABC'], 'ABC'), ([b'ABC'], 'ABC'), ([u'ABC'], 'ABC'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.DeviceName(*args)
        assert attr.value == value
        assert ndef.wifi.DeviceName(attr).value == value

    def test_decode(self):
        assert ndef.wifi.DeviceName.decode(b'\xc3\x84BC').value == 'ÄBC'

    def test_encode(self):
        assert ndef.wifi.DeviceName(u'ÄBC').encode() == b'\xc3\x84BC'

    def test_format(self):
        attr = ndef.wifi.DeviceName('ABC')
        assert "{:args}".format(attr) == B("'ABC'")
        assert "{:data}".format(attr) == "ABC"
        assert "{}".format(attr) == "Device Name ABC"


class TestAttribute_EncryptionType:
    @pytest.mark.parametrize("args, value", [
        ((1,), (0x0001, 'None')),
        (('None',), (0x0001, 'None')),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.EncryptionType(*args)
        assert attr.value == value
        assert ndef.wifi.EncryptionType(attr).value == value

    @pytest.mark.parametrize("octets, value", [
        ('0000', (0x0000,)),
        ('0001', (0x0001, 'None')),
        ('0002', (0x0002, 'WEP')),
        ('0004', (0x0004, 'TKIP')),
        ('0008', (0x0008, 'AES')),
    ])
    def test_decode(self, octets, value):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.EncryptionType.decode(octets).value == value

    @pytest.mark.parametrize("octets, args", [
        ('0000', (0x0000,)),
        ('0001', ('None',)),
        ('0002', ('WEP',)),
        ('0004', ('TKIP',)),
        ('0008', ('AES',)),
        ('000C', ('TKIP', 'AES',)),
    ])
    def test_encode(self, octets, args):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.EncryptionType(*args).encode() == octets

    def test_format(self):
        attr = ndef.wifi.EncryptionType(0x0008)
        assert "{:args}".format(attr) == "8"
        assert "{:data}".format(attr) == "0x0008 ['AES']"
        assert "{}".format(attr) == "Encryption Type 0x0008 ['AES']"
        attr = ndef.wifi.EncryptionType(0x000C)
        assert "{:args}".format(attr) == "12"
        assert "{:data}".format(attr) == "0x000C ['TKIP', 'AES']"
        assert "{}".format(attr) == "Encryption Type 0x000C ['TKIP', 'AES']"

    def test_contains(self):
        attr = ndef.wifi.EncryptionType(0x000C)
        assert 'TKIP' in attr
        assert 'AES' in attr
        assert 'None' not in attr


class TestAttribute_KeyProvidedAutomatically:
    @pytest.mark.parametrize("args, value", [
        ([True], True), ([1], True),
        ([False], False), ([0], False),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.KeyProvidedAutomatically(*args)
        assert attr.value == value
        assert ndef.wifi.KeyProvidedAutomatically(attr).value == value

    def test_decode(self):
        assert ndef.wifi.KeyProvidedAutomatically.decode(b'\x00').value is False
        assert ndef.wifi.KeyProvidedAutomatically.decode(b'\x01').value is True
        assert ndef.wifi.KeyProvidedAutomatically.decode(b'\xFF').value is True

    def test_encode(self):
        assert ndef.wifi.KeyProvidedAutomatically(False).encode() == b'\x00'
        assert ndef.wifi.KeyProvidedAutomatically(True).encode() == b'\x01'

    def test_format(self):
        attr = ndef.wifi.KeyProvidedAutomatically(0)
        assert "{:args}".format(attr) == "False"
        assert "{:data}".format(attr) == "False"
        assert "{}".format(attr) == "Key Provided Automatically False"
        attr = ndef.wifi.KeyProvidedAutomatically(1)
        assert "{:args}".format(attr) == "True"
        assert "{:data}".format(attr) == "True"
        assert "{}".format(attr) == "Key Provided Automatically True"


class TestAttribute_MacAddress:
    @pytest.mark.parametrize("args, value", [
        ([b'\1\2\3\4\5\6'], b'\1\2\3\4\5\6'),
        ([list(range(6))], b'\0\1\2\3\4\5'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.MacAddress(*args)
        assert attr.value == value
        assert ndef.wifi.MacAddress(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.MacAddress.decode(b'\1\2\3\4\5\6')
        assert attr.value == b'\1\2\3\4\5\6'

    def test_encode(self):
        attr = ndef.wifi.MacAddress(b'\1\2\3\4\5\6')
        assert attr.encode() == b'\1\2\3\4\5\6'

    def test_format(self):
        attr = ndef.wifi.MacAddress(b'\1\2\3\4\5\6')
        assert "{:args}".format(attr) == B("'\\x01\\x02\\x03\\x04\\x05\\x06'")
        assert "{:data}".format(attr) == "01:02:03:04:05:06"
        assert "{}".format(attr) == "MAC Address 01:02:03:04:05:06"


class TestAttribute_Manufacturer:
    @pytest.mark.parametrize("args, value", [
        (['ABC'], 'ABC'), ([b'ABC'], 'ABC'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.Manufacturer(*args)
        assert attr.value == value
        assert ndef.wifi.Manufacturer(attr).value == value

    def test_decode(self):
        assert ndef.wifi.Manufacturer.decode(b'ABC').value == 'ABC'

    def test_encode(self):
        assert ndef.wifi.Manufacturer('ABC').encode() == b'ABC'

    def test_format(self):
        attr = ndef.wifi.Manufacturer('ABC')
        assert "{:args}".format(attr) == B("'ABC'")
        assert "{:data}".format(attr) == "ABC"
        assert "{}".format(attr) == "Manufacturer ABC"


class TestAttribute_ModelName:
    @pytest.mark.parametrize("args, value", [
        (['Model'], 'Model'), ([b'Model'], 'Model'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.ModelName(*args)
        assert attr.value == value
        assert ndef.wifi.ModelName(attr).value == value

    def test_decode(self):
        assert ndef.wifi.ModelName.decode(b'Model').value == 'Model'

    def test_encode(self):
        assert ndef.wifi.ModelName('Model').encode() == b'Model'

    def test_format(self):
        attr = ndef.wifi.ModelName('XYZ')
        assert "{:args}".format(attr) == B("'XYZ'")
        assert "{:data}".format(attr) == "XYZ"
        assert "{}".format(attr) == "Model Name XYZ"


class TestAttribute_ModelNumber:
    @pytest.mark.parametrize("args, value", [
        (['007'], '007'), ([b'007'], '007'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.ModelNumber(*args)
        assert attr.value == value
        assert ndef.wifi.ModelNumber(attr).value == value

    def test_decode(self):
        assert ndef.wifi.ModelNumber.decode(b'007').value == '007'

    def test_encode(self):
        assert ndef.wifi.ModelNumber('007').encode() == b'007'

    def test_format(self):
        attr = ndef.wifi.ModelNumber('007')
        assert "{:args}".format(attr) == B("'007'")
        assert "{:data}".format(attr) == "007"
        assert "{}".format(attr) == "Model Number 007"


class TestAttribute_NetworkIndex:
    @pytest.mark.parametrize("args, value", [
        ([1], 1), (['1'], 1),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.NetworkIndex(*args)
        assert attr.value == value
        assert ndef.wifi.NetworkIndex(attr).value == value

    def test_decode(self):
        assert ndef.wifi.NetworkIndex.decode(b'\1').value == 1

    def test_encode(self):
        assert ndef.wifi.NetworkIndex(1).encode() == b'\1'

    def test_format(self):
        attr = ndef.wifi.NetworkIndex(1)
        assert "{:args}".format(attr) == "1"
        assert "{:data}".format(attr) == "1"
        assert "{}".format(attr) == "Network Index 1"


class TestAttribute_NetworkKey:
    @pytest.mark.parametrize("args, value", [
        ([b'\1\2\3\4\5\6'], b'\1\2\3\4\5\6'),
        ([list(range(6))], b'\0\1\2\3\4\5'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.NetworkKey(*args)
        assert attr.value == value
        assert ndef.wifi.NetworkKey(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.NetworkKey.decode(b'\1\2\3\4\5\6')
        assert attr.value == b'\1\2\3\4\5\6'

    def test_encode(self):
        attr = ndef.wifi.NetworkKey(b'\1\2\3\4\5\6')
        assert attr.encode() == b'\1\2\3\4\5\6'

    def test_format(self):
        attr = ndef.wifi.NetworkKey(b'\1\2\3\4\5\6')
        assert "{:args}".format(attr) == B("'\\x01\\x02\\x03\\x04\\x05\\x06'")
        assert "{:data}".format(attr) == "01:02:03:04:05:06"
        assert "{}".format(attr) == "Network Key 01:02:03:04:05:06"


class TestAttribute_NetworkKeyShareable:
    @pytest.mark.parametrize("args, value", [
        ([True], True), ([1], True),
        ([False], False), ([0], False),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.NetworkKeyShareable(*args)
        assert attr.value == value
        assert ndef.wifi.NetworkKeyShareable(attr).value == value

    def test_decode(self):
        assert ndef.wifi.NetworkKeyShareable.decode(b'\x00').value is False
        assert ndef.wifi.NetworkKeyShareable.decode(b'\x01').value is True
        assert ndef.wifi.NetworkKeyShareable.decode(b'\xFF').value is True

    def test_encode(self):
        assert ndef.wifi.NetworkKeyShareable(False).encode() == b'\x00'
        assert ndef.wifi.NetworkKeyShareable(True).encode() == b'\x01'

    def test_format(self):
        attr = ndef.wifi.NetworkKeyShareable(0)
        assert "{:args}".format(attr) == "False"
        assert "{:data}".format(attr) == "False"
        assert "{}".format(attr) == "Network Key Shareable False"
        attr = ndef.wifi.NetworkKeyShareable(1)
        assert "{:args}".format(attr) == "True"
        assert "{:data}".format(attr) == "True"
        assert "{}".format(attr) == "Network Key Shareable True"


class TestAttribute_OutOfBandPassword:
    @pytest.mark.parametrize("args, value", [
        ([bytearray(range(20)), 7, b''],
         (bytearray(range(20)), 7, b'')),
        ([bytearray(range(20)), 16, bytearray(range(16))],
         (bytearray(range(20)), 16, bytearray(range(16)))),
        ([bytearray(range(20)), 32, bytearray(range(32))],
         (bytearray(range(20)), 32, bytearray(range(32)))),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.OutOfBandPassword(*args)
        assert attr.public_key_hash == value[0]
        assert attr.password_id == value[1]
        assert attr.device_password == value[2]
        attr = ndef.wifi.OutOfBandPassword(attr)
        assert attr.public_key_hash == value[0]
        assert attr.password_id == value[1]
        assert attr.device_password == value[2]

    def test_decode(self):
        data = bytearray(range(20)) + b'\x00\x07'
        attr = ndef.wifi.OutOfBandPassword.decode(data)
        assert attr.value == (bytearray(range(20)), 7, b'')
        data = bytearray(range(20)) + b'\x00\x10' + bytearray(range(16))
        attr = ndef.wifi.OutOfBandPassword.decode(data)
        assert attr.value == (bytearray(range(20)), 16, bytearray(range(16)))
        data = bytearray(range(20)) + b'\x00\x10' + bytearray(range(32))
        attr = ndef.wifi.OutOfBandPassword.decode(data)
        assert attr.value == (bytearray(range(20)), 16, bytearray(range(32)))

    def test_encode(self):
        pkhash = bytearray(range(20))
        attr = ndef.wifi.OutOfBandPassword(pkhash, 7, b'')
        assert attr.encode() == pkhash + b'\x00\x07'
        attr = ndef.wifi.OutOfBandPassword(pkhash, 16, bytearray(range(16)))
        assert attr.encode() == pkhash + b'\x00\x10' + bytearray(range(16))
        attr = ndef.wifi.OutOfBandPassword(pkhash, 16, bytearray(range(32)))
        assert attr.encode() == pkhash + b'\x00\x10' + bytearray(range(32))

    def test_format(self):
        pkhash = bytearray(range(20))
        attr = ndef.wifi.OutOfBandPassword(pkhash, 7, b'')
        assert "{:args}".format(attr) == \
            B("'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b"\
              "\\x0c\\r\\x0e\\x0f\\x10\\x11\\x12\\x13'") + ", 7, " + B("''")
        assert "{:data}".format(attr) == \
            "HASH 000102030405060708090a0b0c0d0e0f10111213 ID 7 PWD "
        assert "{}".format(attr) == "Out Of Band Device Password "\
            "HASH 000102030405060708090a0b0c0d0e0f10111213 ID 7 PWD "
        attr = ndef.wifi.OutOfBandPassword(pkhash, 16, bytearray(range(16)))
        assert "{:data}".format(attr) == \
            "HASH 000102030405060708090a0b0c0d0e0f10111213 ID 16 "\
            "PWD 000102030405060708090a0b0c0d0e0f"


class TestAttribute_PrimaryDeviceType:
    @pytest.mark.parametrize("args, value", [
        ((0x0000000000000000,), "0000::000000000000"),
        ((0x0001000000000001,), "Computer::000000000001"),
        ((0x00010050F2040001,), "Computer::PC"),
        (("Computer::PC",), "Computer::PC"),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.PrimaryDeviceType(*args)
        assert attr.value == value
        assert ndef.wifi.PrimaryDeviceType(attr).value == value

    def test_decode(self):
        octets = bytearray.fromhex('00010050F2040001')
        attr = ndef.wifi.PrimaryDeviceType.decode(octets)
        assert attr.value == "Computer::PC"

    def test_encode(self):
        attr = ndef.wifi.PrimaryDeviceType("Computer::PC")
        assert attr.encode() == bytearray.fromhex('00010050F2040001')

    def test_format(self):
        attr = ndef.wifi.PrimaryDeviceType(0x00010050F2040001)
        assert "{:args}".format(attr) == "0x00010050F2040001"
        assert "{:data}".format(attr) == "Computer::PC"
        assert "{}".format(attr) == "Primary Device Type Computer::PC"
        attr = ndef.wifi.PrimaryDeviceType(0x0001FFFFFFFF0001)
        assert "{:args}".format(attr) == "0x0001FFFFFFFF0001"
        assert "{:data}".format(attr) == "Computer::FFFFFFFF0001"
        assert "{}".format(attr) == "Primary Device Type Computer::FFFFFFFF0001"
        attr = ndef.wifi.PrimaryDeviceType(0x0101FFFFFFFF0001)
        assert "{:args}".format(attr) == "0x0101FFFFFFFF0001"
        assert "{:data}".format(attr) == "0101::FFFFFFFF0001"
        assert "{}".format(attr) == "Primary Device Type 0101::FFFFFFFF0001"

    def test_undefined_name(self):
        with pytest.raises((ValueError)) as excinfo:
            ndef.wifi.PrimaryDeviceType("Category::Subcategory")
        assert str(excinfo.value) == \
            "'Category::Subcategory' does not have a known mapping"


class TestAttribute_RFBands:
    @pytest.mark.parametrize("args, value", [
        ((0x00,), (0x00,)),
        ((0x01,), (0x01, '2.4GHz')),
        ((0x02,), (0x02, '5.0GHz')),
        ((0x04,), (0x04, '60GHz')),
        ((0x03,), (0x03, '2.4GHz', '5.0GHz')),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.RFBands(*args)
        assert attr.value == value
        assert ndef.wifi.RFBands(attr).value == value

    @pytest.mark.parametrize("octets, value", [
        ('00', (0x00,)),
        ('01', (0x01, '2.4GHz')),
        ('02', (0x02, '5.0GHz')),
        ('04', (0x04, '60GHz')),
        ('03', (0x03, '2.4GHz', '5.0GHz')),
    ])
    def test_decode(self, octets, value):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.RFBands.decode(octets).value == value

    @pytest.mark.parametrize("octets, args", [
        ('00', (0x00,)),
        ('01', ('2.4GHz',)),
        ('02', ('5.0GHz',)),
        ('04', ('60GHz',)),
        ('03', ('2.4GHz', '5.0GHz')),
    ])
    def test_encode(self, octets, args):
        octets = bytearray.fromhex(octets)
        assert ndef.wifi.RFBands(*args).encode() == octets

    def test_format(self):
        attr = ndef.wifi.RFBands(0x01)
        assert "{:args}".format(attr) == "1"
        assert "{:data}".format(attr) == "0x01 ['2.4GHz']"
        assert "{}".format(attr) == "RF Bands 0x01 ['2.4GHz']"
        attr = ndef.wifi.RFBands(0x03)
        assert "{:args}".format(attr) == "3"
        assert "{:data}".format(attr) == "0x03 ['2.4GHz', '5.0GHz']"
        assert "{}".format(attr) == "RF Bands 0x03 ['2.4GHz', '5.0GHz']"

    def test_contains(self):
        attr = ndef.wifi.RFBands(0x03)
        assert '2.4GHz' in attr
        assert '5.0GHz' in attr
        assert '60GHz' not in attr


class TestAttribute_SecondaryDeviceTypeList:
    @pytest.mark.parametrize("args, value", [
        ([0x00010050F2040001, 0x00050050F2040001],
         ("Computer::PC", "Storage::NAS")),
        (["Storage::NAS", "Computer::PC"],
         ("Storage::NAS", "Computer::PC")),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.SecondaryDeviceTypeList(*args)
        assert attr.value == value
        assert ndef.wifi.SecondaryDeviceTypeList(attr).value == value

    def test_decode(self):
        octets = bytearray.fromhex('00010050F2040001 00050050F2040001')
        attr = ndef.wifi.SecondaryDeviceTypeList.decode(octets)
        assert attr.value == ("Computer::PC", "Storage::NAS")

    def test_encode(self):
        octets = bytearray.fromhex('00010050F2040001 00050050F2040001')
        attr = ndef.wifi.SecondaryDeviceTypeList("Computer::PC", "Storage::NAS")
        assert attr.encode() == octets

    def test_format(self):
        args = (0x00010050F2040001, 0x0005FFFFFFFF0001, 0x0101FFFFFFFF0001)
        attr = ndef.wifi.SecondaryDeviceTypeList(*args)
        assert "{:args}".format(attr) == \
            "0x00010050F2040001, 0x0005FFFFFFFF0001, 0x0101FFFFFFFF0001"
        assert "{:data}".format(attr) == \
            "Computer::PC Storage::FFFFFFFF0001 0101::FFFFFFFF0001"
        assert "{}".format(attr) == \
            "Secondary Device Type List " \
            "Computer::PC Storage::FFFFFFFF0001 0101::FFFFFFFF0001"

    def test_undefined_name(self):
        with pytest.raises((ValueError)) as excinfo:
            ndef.wifi.SecondaryDeviceTypeList("Category::Subcategory")
        assert str(excinfo.value) == \
            "'Category::Subcategory' does not have a known mapping"


class TestAttribute_SerialNumber:
    @pytest.mark.parametrize("args, value", [
        (['1234'], '1234'), ([b'1234'], '1234'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.SerialNumber(*args)
        assert attr.value == value
        assert ndef.wifi.SerialNumber(attr).value == value

    def test_decode(self):
        assert ndef.wifi.SerialNumber.decode(b'1234').value == '1234'

    def test_encode(self):
        assert ndef.wifi.SerialNumber('1234').encode() == b'1234'

    def test_format(self):
        attr = ndef.wifi.SerialNumber('1234')
        assert "{:args}".format(attr) == B("'1234'")
        assert "{:data}".format(attr) == "1234"
        assert "{}".format(attr) == "Serial Number 1234"


class TestAttribute_SSID:
    @pytest.mark.parametrize("args, value", [
        ([b'\1\2\3\4\5\6'], b'\1\2\3\4\5\6'),
        ([list(range(6))], b'\0\1\2\3\4\5'),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.SSID(*args)
        assert attr.value == value
        assert ndef.wifi.SSID(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.SSID.decode(b'\1\2\3\4\5\6')
        assert attr.value == b'\1\2\3\4\5\6'

    def test_encode(self):
        attr = ndef.wifi.SSID(b'\1\2\3\4\5\6')
        assert attr.encode() == b'\1\2\3\4\5\6'

    def test_format(self):
        attr = ndef.wifi.SSID(b'\1\2\3\4\5\6')
        assert "{:args}".format(attr) == B("'\\x01\\x02\\x03\\x04\\x05\\x06'")
        assert "{:data}".format(attr) == "01:02:03:04:05:06"
        assert "{}".format(attr) == "SSID 01:02:03:04:05:06"


class TestAttribute_UUIDEnrollee:
    @pytest.mark.parametrize("args, value", [
        ([bytearray(range(16))],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
        ([bytes(bytearray(range(16)))],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
        ([uuid.UUID(bytes=bytes(bytearray(range(16))))],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
        (["00010203-0405-0607-0809-0a0b0c0d0e0f"],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.UUIDEnrollee(*args)
        assert attr.value == value
        assert ndef.wifi.UUIDEnrollee(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.UUIDEnrollee.decode(bytearray(range(16)))
        assert attr.value == "00010203-0405-0607-0809-0a0b0c0d0e0f"

    def test_encode(self):
        attr = ndef.wifi.UUIDEnrollee(bytearray(range(16)))
        assert attr.encode() == bytearray(range(16))

    def test_format(self):
        attr = ndef.wifi.UUIDEnrollee(bytearray(range(16)))
        assert "{:args}".format(attr) == \
            "'00010203-0405-0607-0809-0a0b0c0d0e0f'"
        assert "{:data}".format(attr) == \
            "00010203-0405-0607-0809-0a0b0c0d0e0f"
        assert "{}".format(attr) == \
            "UUID-E 00010203-0405-0607-0809-0a0b0c0d0e0f"


class TestAttribute_UUIDRegistrar:
    @pytest.mark.parametrize("args, value", [
        ([bytearray(range(16))],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
        ([bytes(bytearray(range(16)))],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
        ([uuid.UUID(bytes=bytes(bytearray(range(16))))],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
        (["00010203-0405-0607-0809-0a0b0c0d0e0f"],
         "00010203-0405-0607-0809-0a0b0c0d0e0f"),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.UUIDRegistrar(*args)
        assert attr.value == value
        assert ndef.wifi.UUIDRegistrar(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.UUIDRegistrar.decode(bytearray(range(16)))
        assert attr.value == "00010203-0405-0607-0809-0a0b0c0d0e0f"

    def test_encode(self):
        attr = ndef.wifi.UUIDRegistrar("00010203-0405-0607-0809-0a0b0c0d0e0f")
        assert attr.encode() == bytes(bytearray(range(16)))

    def test_format(self):
        attr = ndef.wifi.UUIDRegistrar(bytearray(range(16)))
        assert "{:args}".format(attr) == \
            "'00010203-0405-0607-0809-0a0b0c0d0e0f'"
        assert "{:data}".format(attr) == \
            "00010203-0405-0607-0809-0a0b0c0d0e0f"
        assert "{}".format(attr) == \
            "UUID-R 00010203-0405-0607-0809-0a0b0c0d0e0f"


class TestAttribute_VendorExtension:
    @pytest.mark.parametrize("args, value", [
        ([b'\x00\x37\x2A', b'123'], (b'\x00\x37\x2A', b'123')),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.VendorExtension(*args)
        assert attr.value == value
        assert ndef.wifi.VendorExtension(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.VendorExtension.decode(b'\x00\x37\x2A\x31\x32\x33')
        assert attr.value == (b'\x00\x37\x2A', b'123')

    def test_encode(self):
        attr = ndef.wifi.VendorExtension(b'\x00\x37\x2A', b'123')
        assert attr.encode() == b'\x00\x37\x2A\x31\x32\x33'

    def test_format(self):
        attr = ndef.wifi.VendorExtension(b'\x00\x37\x2A', b'123')
        assert "{:args}".format(attr) == B("'\\x007*'") + ", " + B("'123'")
        assert "{:data}".format(attr) == "ID 00372a DATA 313233"
        assert "{}".format(attr) == "Vendor Extension ID 00372a DATA 313233"


class TestAttribute_Version1:
    @pytest.mark.parametrize("args, value", [
        ([0x10], ndef.wifi.VersionTuple(1, 0)),
        ([1, 0], ndef.wifi.VersionTuple(1, 0)),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.Version1(*args)
        assert attr.value == value
        assert ndef.wifi.Version1(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.Version1.decode(b'\x10')
        assert attr.value == ndef.wifi.VersionTuple(1, 0)

    def test_encode(self):
        attr = ndef.wifi.Version1(0x10)
        assert attr.encode() == b'\x10'

    def test_format(self):
        attr = ndef.wifi.Version1(0x10)
        assert "{:args}".format(attr) == "1, 0"
        assert "{:data}".format(attr) == "1.0"
        assert "{}".format(attr) == "Version1 1.0"


class TestAttribute_Version2:
    @pytest.mark.parametrize("args, value", [
        ([0x20], ndef.wifi.VersionTuple(2, 0)),
        ([2, 0], ndef.wifi.VersionTuple(2, 0)),
    ])
    def test_init(self, args, value):
        attr = ndef.wifi.Version2(*args)
        assert attr.value == value
        assert ndef.wifi.Version2(attr).value == value

    def test_decode(self):
        attr = ndef.wifi.Version2.decode(b'\x20')
        assert attr.value == ndef.wifi.VersionTuple(2, 0)

    def test_encode(self):
        attr = ndef.wifi.Version2(0x20)
        assert attr.encode() == b'\x20'

    def test_format(self):
        attr = ndef.wifi.Version2(0x20)
        assert "{:args}".format(attr) == "2, 0"
        assert "{:data}".format(attr) == "2.0"
        assert "{}".format(attr) == "Version2 2.0"


class TestWifiAllianceVendorExtension:
    @pytest.mark.parametrize("args, attrs", [
        ([(0x00, b'\x20')], {'version-2': [b'\x20']}),
        ([('version-2', b'\x20')], {'version-2': [b'\x20']}),
        ([(0x02, b'\x01')], {'shareable': [b'\x01']}),
        ([('network-key-shareable', b'\x01')], {'shareable': [b'\x01']}),
    ])
    def test_init(self, args, attrs):
        attr = ndef.wifi.WifiAllianceVendorExtension(*args)
        assert attr.get(0x00) == attrs.get('version-2')
        assert attr.get(0x02) == attrs.get('shareable')

    def test_decode(self):
        data = bytearray.fromhex('00372A 000120 020101')
        attr = ndef.wifi.WifiAllianceVendorExtension.decode(data)
        assert attr.get(0x00) == [b'\x20']
        assert attr.get(0x02) == [b'\x01']

    def test_encode(self):
        args = [(0x00, b'\x20'), (0x02, b'\x01')]
        attr = ndef.wifi.WifiAllianceVendorExtension(*args)
        assert attr.encode() == bytearray.fromhex('00372A 000120 020101')

    def test_format(self):
        args = [(0x00, b'\x20'), (0x02, b'\x01')]
        attr = ndef.wifi.WifiAllianceVendorExtension(*args)
        if ndef.record._PY2:
            assert "{:args}".format(attr) == "(0x00, ' '), (0x02, '\\x01')"
        else:
            assert "{:args}".format(attr) == "(0x00, b' '), (0x02, b'\\x01')"
        assert "{:data}".format(attr) == "Attributes 0x00 0x02"
        assert "{}".format(attr) == "WFA Vendor Extension Attributes 0x00 0x02"


class TestAttribute_Credential:
    @pytest.mark.parametrize("args, attrs", [
        ([(0x1003, b'\x00\x01')], {'auth': [b'\x00\x01']}),
        ([(0x100F, b'\x00\x01')], {'encr': [b'\x00\x01']}),
        ([(0x1061, b'\x01')], {'auto': [b'\x01']}),
        ([(0x1020, b'\1\2\3\4\5\6')], {'addr': [b'\1\2\3\4\5\6']}),
        ([(0x1027, b'secret')], {'pass': [b'secret']}),
        ([(0x1045, b'my-ssid')], {'ssid': [b'my-ssid']}),
        ([(0x1049, b'\x00\x37\x2A123')], {'vext': [b'\x00\x37\x2A123']}),
        ([('authentication-type', b'\x00\x01')], {'auth': [b'\x00\x01']}),
        ([('encryption-type', b'\x00\x01')], {'encr': [b'\x00\x01']}),
        ([('key-provided-automatically', b'\x01')], {'auto': [b'\x01']}),
        ([('mac-address', b'\1\2\3\4\5\6')], {'addr': [b'\1\2\3\4\5\6']}),
        ([('network-key', b'secret')], {'pass': [b'secret']}),
        ([('ssid', b'my-ssid')], {'ssid': [b'my-ssid']}),
        ([('vendor-extension', b'\0\x37\x2A12')], {'vext': [b'\0\x37\x2A12']}),
    ])
    def test_init(self, args, attrs):
        attr = ndef.wifi.Credential(*args)
        assert attr.get(0x1003) == attrs.get('auth')
        assert attr.get(0x100F) == attrs.get('encr')
        assert attr.get(0x1061) == attrs.get('auto')
        assert attr.get(0x1020) == attrs.get('addr')
        assert attr.get(0x1027) == attrs.get('pass')
        assert attr.get(0x1045) == attrs.get('ssid')
        assert attr.get(0x1049) == attrs.get('vext')
        assert attr.get(0x1003) == attr.get('authentication-type')
        assert attr.get(0x100F) == attr.get('encryption-type')
        assert attr.get(0x1061) == attr.get('key-provided-automatically')
        assert attr.get(0x1020) == attr.get('mac-address')
        assert attr.get(0x1027) == attr.get('network-key')
        assert attr.get(0x1045) == attr.get('ssid')
        assert attr.get(0x1049) == attr.get('vendor-extension')

    def test_decode(self):
        data = bytearray.fromhex('100F00020001')  # encryption-type
        data+= bytearray.fromhex('100300020001')  # authentication-type
        data+= bytearray.fromhex('1061000101')  # key-provided-automatically
        data+= bytearray.fromhex('104500076d792d73736964')  # ssid
        data+= bytearray.fromhex('10270006736563726574')  # network-key
        data+= bytearray.fromhex('10200006010203040506')  # mac-address
        data+= bytearray.fromhex('1049000600372A313233')  # vendor-extension
        attr = ndef.wifi.Credential.decode(data)
        assert attr.get(0x1003) == [b'\x00\x01']
        assert attr.get(0x100F) == [b'\x00\x01']
        assert attr.get(0x1061) == [b'\x01']
        assert attr.get(0x1020) == [b'\1\2\3\4\5\6']
        assert attr.get(0x1027) == [b'secret']
        assert attr.get(0x1045) == [b'my-ssid']
        assert attr.get(0x1049) == [b'\x00\x37\x2A123']
        assert attr.get_attribute('authentication-type') \
            == ndef.wifi.AuthenticationType('Open')
        assert attr.get_attribute('encryption-type') \
            == ndef.wifi.EncryptionType('None')
        assert attr.get_attribute('key-provided-automatically') \
            == ndef.wifi.KeyProvidedAutomatically(True)
        assert attr.get_attribute('mac-address') \
            == ndef.wifi.MacAddress(b'\1\2\3\4\5\6')
        assert attr.get_attribute('network-key') \
            == ndef.wifi.NetworkKey(b'secret')
        assert attr.get_attribute('ssid') \
            == ndef.wifi.SSID(b'my-ssid')
        assert attr.get_attribute('vendor-extension') \
            == ndef.wifi.VendorExtension(b'\x00\x37\x2A', b'123')

    def test_encode(self):
        attr = ndef.wifi.Credential()
        attr[0x100F] = [b'\x00\x01']  # encryption-type
        attr[0x1003] = [b'\x00\x01']  # authentication-type
        attr[0x1061] = [b'\x01']  # key-provided-automatically
        attr[0x1045] = [b'my-ssid']  # ssid
        attr[0x1027] = [b'secret']  # network-key
        attr[0x1020] = [b'\1\2\3\4\5\6']  # mac-address
        attr[0x1049] = [b'\x00\x37\x2A123']  # vendor-extension      
        data = bytearray.fromhex('100300020001')  # authentication-type
        data+= bytearray.fromhex('100F00020001')  # encryption-type
        data+= bytearray.fromhex('10200006010203040506')  # mac-address
        data+= bytearray.fromhex('10270006736563726574')  # network-key
        data+= bytearray.fromhex('104500076d792d73736964')  # ssid
        data+= bytearray.fromhex('1049000600372A313233')  # vendor-extension
        data+= bytearray.fromhex('1061000101')  # key-provided-automatically
        assert attr.encode() == bytes(data)  # encoding is sorted by keys
        attr = ndef.wifi.Credential()
        attr.set_attribute('authentication-type', 'Open')
        attr.set_attribute('encryption-type', 'None')
        attr.set_attribute('key-provided-automatically', True)
        attr.set_attribute('mac-address', b'\1\2\3\4\5\6')
        attr.set_attribute('network-key', b'secret')
        attr.set_attribute('ssid', b'my-ssid')
        attr.set_attribute('vendor-extension', b'\x00\x37\x2A', b'123')
        assert attr.encode() == bytes(data)  # encoding is sorted by keys

    def test_format(self):
        attr = ndef.wifi.Credential((0x1045, b'ssid'), (0x1027, b'pwd'))
        if ndef.record._PY2:
            assert "{:args}".format(attr) == \
                "(0x1045, 'ssid'), (0x1027, 'pwd')"
        else:
            assert "{:args}".format(attr) == \
                "(0x1045, b'ssid'), (0x1027, b'pwd')"
        assert "{:data}".format(attr) == "Attributes 0x1045 0x1027"
        assert "{}".format(attr) == "Credential Attributes 0x1045 0x1027"

#
# P2P Attributes
#

class TestAttribute_PeerToPeerCapability:
    @pytest.mark.parametrize("args, device_capability, group_capability", [
        ((0x00, 0x00), (0x00,), (0x00,)),
        ((0x01, 0x00), (0x01, 'Service Discovery'), (0x00,)),
        ((0x02, 0x00), (0x02, 'P2P Client Discoverability'), (0x00,)),
        ((0x04, 0x00), (0x04, 'Concurrent Operation'), (0x00,)),
        ((0x08, 0x00), (0x08, 'P2P Infastructure Managed'), (0x00,)),
        ((0x10, 0x00), (0x10, 'P2P Device Limit'), (0x00,)),
        ((0x20, 0x00), (0x20, 'P2P Invitation Procedure'), (0x00,)),
        ((0x40, 0x00), (0x40, 'Reserved Bit 6'), (0x00,)),
        ((0x80, 0x00), (0x80, 'Reserved Bit 7'), (0x00,)),
        ((0x00, 0x01), (0x00,), (0x01, 'P2P Group Owner'),),
        ((0x00, 0x02), (0x00,), (0x02, 'Persistent P2P Group'),),
        ((0x00, 0x04), (0x00,), (0x04, 'P2P Group Limit'),),
        ((0x00, 0x08), (0x00,), (0x08, 'Intra-BSS Distribution'),),
        ((0x00, 0x10), (0x00,), (0x10, 'Cross Connection'),),
        ((0x00, 0x20), (0x00,), (0x20, 'Persistent Reconnect'),),
        ((0x00, 0x40), (0x00,), (0x40, 'Group Formation'),),
        ((0x00, 0x80), (0x00,), (0x80, 'IP Address Allocation'),),
        ((0x11, 0x22),
         (0x11, 'Service Discovery', 'P2P Device Limit'),
         (0x22, 'Persistent P2P Group', 'Persistent Reconnect')),
    ])
    def test_init(self, args, device_capability, group_capability):
        attr = ndef.wifi.PeerToPeerCapability(*args)
        assert attr.device_capability == device_capability
        assert attr.group_capability == group_capability

    def test_decode(self):
        attr = ndef.wifi.PeerToPeerCapability.decode(b'\x01\x02')
        assert attr.device_capability == (0x01, 'Service Discovery')
        assert attr.group_capability == (0x02, 'Persistent P2P Group')

    @pytest.mark.parametrize("octets, args", [
        ('0100', (('Service Discovery',), 0x00)),
        ('0200', (('P2P Client Discoverability',), 0x00)),
        ('0400', (('Concurrent Operation',), 0x00)),
        ('0800', (('P2P Infastructure Managed',), 0x00)),
        ('1000', (('P2P Device Limit',), 0x00)),
        ('2000', (('P2P Invitation Procedure',), 0x00)),
        ('4000', (('Reserved Bit 6',), 0x00)),
        ('8000', (('Reserved Bit 7',), 0x00)),
        ('0001', (0x00, ('P2P Group Owner',))),
        ('0002', (0x00, ('Persistent P2P Group',))),
        ('0004', (0x00, ('P2P Group Limit',))),
        ('0008', (0x00, ('Intra-BSS Distribution',))),
        ('0010', (0x00, ('Cross Connection',))),
        ('0020', (0x00, ('Persistent Reconnect',))),
        ('0040', (0x00, ('Group Formation',))),
        ('0080', (0x00, ('IP Address Allocation',))),
        ('1122', (
            ('P2P Device Limit', 'Service Discovery'),
            ('Persistent Reconnect', 'Persistent P2P Group'))),
    ])
    def test_encode(self, octets, args):
        attr = ndef.wifi.PeerToPeerCapability(*args)
        assert attr.encode() == bytearray.fromhex(octets)

    def test_format(self):
        attr = ndef.wifi.PeerToPeerCapability(0x41, 0x21)
        assert repr(attr) == "ndef.wifi.PeerToPeerCapability(65, 33)"
        assert str(attr) == "P2P Capability "\
            "Device ['Service Discovery', 'Reserved Bit 6'] "\
            "Group ['P2P Group Owner', 'Persistent Reconnect']"


class TestAttribute_ChannelList:
    @pytest.mark.parametrize("octets, country_string, channel_entry_list", [
        ('646504 5100', b'de\x04', [(81, ())]),
        ('646504 510106', b'de\x04', [(81, (6,))]),
        ('646504 51020601', b'de\x04', [(81, (6, 1))]),
        ('646504 5100 5200', b'de\x04', [(81, ()), (82, ())]),
        ('646504 510106 520101', b'de\x04', [(81, (6,)), (82, (1,))]),
        ('646504 51020601 52020106', b'de\x04', [(81, (6, 1)), (82, (1, 6))]),
    ])
    def test_decode(self, octets, country_string, channel_entry_list):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.ChannelList.decode(data)
        assert attr.country_string == country_string
        assert len(attr) == len(channel_entry_list)
        for index, channel_entry in enumerate(channel_entry_list):
            assert attr[index].operating_class == channel_entry[0]
            assert attr[index].channel_numbers == channel_entry[1]
    
    @pytest.mark.parametrize("octets, country_string, channel_entry_list", [
        ('646504 5100', b'de\x04', [(81, ())]),
        ('646504 510106', b'de\x04', [(81, (6,))]),
        ('646504 51020601', b'de\x04', [(81, (6, 1))]),
        ('646504 5100 5200', b'de\x04', [(81, ()), (82, ())]),
        ('646504 510106 520101', b'de\x04', [(81, (6,)), (82, (1,))]),
        ('646504 51020601 52020106', b'de\x04', [(81, (6, 1)), (82, (1, 6))]),
    ])
    def test_encode(self, octets, country_string, channel_entry_list):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.ChannelList(country_string, *channel_entry_list)
        assert attr.encode() == data

    @pytest.mark.parametrize("country_string, channel_entry_list, s", [
        (b'de\x04', [(81, ())], "Class 81 Channels []"),
        (b'de\x04', [(81, (6,))], "Class 81 Channels [6]"),
        (b'de\x04', [(81, (6, 1))], "Class 81 Channels [6, 1]"),
        (b'de\x04', [(81, (6, 1)), (82, (1, 6))],
         "Class 81 Channels [6, 1], Class 82 Channels [1, 6]"),
    ])
    def test_format(self, country_string, channel_entry_list, s):
        attr = ndef.wifi.ChannelList(country_string, *channel_entry_list)
        assert "{}".format(attr) == "Channel List Country DE Table E-4 " + s
        assert str(attr) == "Channel List Country DE Table E-4 " + s


class TestAttribute_PeerToPeerDeviceInfo:
    @pytest.mark.parametrize("args", [
        (b'\1\2\3\4\5\6', ('Label', 'NFC Interface'), 'Computer::Tablet',
         ('Telephone::DualModeSmartphone', 'Audio::Speaker'), 'abc'),
        (b'\1\2\3\4\5\6', 68, 281822634442761, 
         (2815097424838661, 3096572401549314), 'abc'),
    ])
    def test_init(self, args):
        attr = ndef.wifi.PeerToPeerDeviceInfo(*args)
        assert attr.device_address == b'\1\2\3\4\5\6'
        assert attr.config_methods == (0x0044, 'Label', 'NFC Interface')
        assert attr.primary_device_type == 'Computer::Tablet'
        assert attr.secondary_device_type_list == (
            'Telephone::DualModeSmartphone', 'Audio::Speaker')
        assert attr.device_name == 'abc'
    
    def test_decode(self):
        data = bytearray.fromhex('010203040506')      # device address
        data+= bytearray.fromhex('00C0')              # config methods
        data+= bytearray.fromhex('00010050F2040007')  # primary device type
        data+= bytearray.fromhex('02')                # secondary device type N
        data+= bytearray.fromhex('000A0050F2040005')  # secondary device type
        data+= bytearray.fromhex('000B0050F2040003')  # secondary device type
        data+= bytearray.fromhex('10110003616263')    # device name 'abc'
        attr = ndef.wifi.PeerToPeerDeviceInfo.decode(data)
        assert attr.device_address == b'\1\2\3\4\5\6'
        assert attr.config_methods == (0x00C0, 'NFC Interface', 'Push Button')
        assert attr.primary_device_type == 'Computer::MobileInternetDevice'
        assert attr.secondary_device_type_list == (
            'Telephone::DualModeSmartphone', 'Audio::PortableMusicPlayer')
        assert attr.device_name == 'abc'

    def test_encode(self):
        data = bytearray.fromhex('010203040506')      # device address
        data+= bytearray.fromhex('0044')              # config methods
        data+= bytearray.fromhex('00010050F2040009')  # primary device type
        data+= bytearray.fromhex('02')                # secondary device type N
        data+= bytearray.fromhex('000A0050F2040005')  # secondary device type
        data+= bytearray.fromhex('000B0050F2040002')  # secondary device type
        data+= bytearray.fromhex('10110003616263')    # device name 'abc'
        attr = ndef.wifi.PeerToPeerDeviceInfo(
            b'\1\2\3\4\5\6', ('Label', 'NFC Interface'), 'Computer::Tablet',
            ('Telephone::DualModeSmartphone', 'Audio::Speaker'), 'abc')
        assert attr.encode() == data

    def test_format(self):
        attr = ndef.wifi.PeerToPeerDeviceInfo(
            b'\1\2\3\4\5\6', ('Label', 'NFC Interface'), 'Computer::Tablet',
            ('Telephone::DualModeSmartphone', 'Audio::Speaker'), 'abc')
        assert "{!r}".format(attr) == "ndef.wifi.PeerToPeerDeviceInfo(" + \
            B("'\\x01\\x02\\x03\\x04\\x05\\x06'") + ", 68, 281822634442761, "\
            "(2815097424838661, 3096572401549314), 'abc')"
        assert "{}".format(attr) == "P2P Device Info 01:02:03:04:05:06 "\
            "0x0044 ['Label', 'NFC Interface'] Computer::Tablet "\
            "Telephone::DualModeSmartphone Audio::Speaker 'abc'"


class TestAttribute_PeerToPeerGroupInfo:
    @pytest.mark.parametrize("octets, values", [
        ('010203040506 060504030201 01 0040 00010050F2040009 00 10110003616263',
         ((b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', (1, 'Service Discovery'),
           (64, 'NFC Interface'), "Computer::Tablet", (), 'abc'),)
        ),
        ('010203040506 060504030201 01 0040 00010050F2040009 00 10110003616263'
         '010203040506 060504030201 01 0040 00010050F2040009 00 10110003646566',
         ((b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', (1, 'Service Discovery'),
           (64, 'NFC Interface'), "Computer::Tablet", (), 'abc'),
         (b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', (1, 'Service Discovery'),
           (64, 'NFC Interface'), "Computer::Tablet", (), 'def'))
        ),
        ('010203040506 060504030201 01 0040 00010050F2040009 '
         '02 00090050F2040005 00070050F2040004 10110003616263',
         ((b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', (1, 'Service Discovery'),
           (64, 'NFC Interface'), "Computer::Tablet",
           ("Gaming::Portable", "Display::Monitor"), 'abc'),)
        ),
    ])
    def test_decode(self, octets, values):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.PeerToPeerGroupInfo.decode(data)
        assert len(attr) == len(values)
        for index, value in enumerate(values):
            print(attr._value)
            assert attr[index].device_address == value[0]
            assert attr[index].interface_address == value[1]
            assert attr[index].device_capability == value[2]
            assert attr[index].config_methods == value[3]
            assert attr[index].primary_device_type == value[4]
            assert attr[index].secondary_device_type_list == value[5]
            assert attr[index].device_name == value[6]

    @pytest.mark.parametrize("octets, args", [
        ('010203040506 060504030201 01 0040 00010050F2040009 00 10110003616263',
         ((b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', ('Service Discovery',),
           ('NFC Interface',), "Computer::Tablet", (), 'abc'),)
        ),
        ('010203040506 060504030201 01 0040 00010050F2040009 00 10110003616263'
         '010203040506 060504030201 01 0040 00010050F2040009 00 10110003646566',
         ((b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', ('Service Discovery',),
           ('NFC Interface',), "Computer::Tablet", (), 'abc'),
         (b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', ('Service Discovery',),
           ('NFC Interface',), "Computer::Tablet", (), 'def'))
        ),
        ('010203040506 060504030201 01 0040 00010050F2040009 '
         '02 00090050F2040005 00070050F2040004 10110003616263',
         ((b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', ('Service Discovery',),
           ('NFC Interface',), "Computer::Tablet",
           ("Gaming::Portable", "Display::Monitor"), 'abc'),)
        ),
    ])
    def test_encode(self, octets, args):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.PeerToPeerGroupInfo(*args)
        assert attr.encode() == data

    def test_format(self):
        attr = ndef.wifi.PeerToPeerGroupInfo(
            (b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', ('Service Discovery',),
             ('NFC Interface',), "Computer::Tablet",
             ("Gaming::Portable", "Display::Monitor"), 'abc'))
        assert "{}".format(attr) == "P2P Group Info "\
            "(Device 1: 01:02:03:04:05:06 06:05:04:03:02:01 "\
            "Capability ['Service Discovery'] "\
            "Config 0x0040 ['NFC Interface'] "\
            "Type 'Computer::Tablet Gaming::Portable Display::Monitor' "\
            "Name 'abc')"
        attr = ndef.wifi.PeerToPeerGroupInfo(
            (b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', ('Service Discovery',),
             ('NFC Interface',), "Computer::Tablet",
             ("Gaming::Portable", "Display::Monitor"), 'abc'),
            (b'\1\2\3\4\5\6', b'\6\5\4\3\2\1', ('Service Discovery',),
             ('NFC Interface',), "Computer::Tablet",
             ("Gaming::Portable", "Display::Monitor"), 'abc'))
        assert "{}".format(attr) == "P2P Group Info "\
            "(Device 1: 01:02:03:04:05:06 06:05:04:03:02:01 "\
            "Capability ['Service Discovery'] "\
            "Config 0x0040 ['NFC Interface'] "\
            "Type 'Computer::Tablet Gaming::Portable Display::Monitor' "\
            "Name 'abc'), "\
            "(Device 2: 01:02:03:04:05:06 06:05:04:03:02:01 "\
            "Capability ['Service Discovery'] "\
            "Config 0x0040 ['NFC Interface'] "\
            "Type 'Computer::Tablet Gaming::Portable Display::Monitor' "\
            "Name 'abc')"


class TestAttribute_PeerToPeerGroupID:
    @pytest.mark.parametrize("args, device_address, ssid", [
        ((b'\1\2\3\4\5\6', b'my-ssid'), b'\1\2\3\4\5\6', b'my-ssid'),
    ])
    def test_init(self, args, device_address, ssid):
        attr = ndef.wifi.PeerToPeerGroupID(*args)
        assert attr.device_address == device_address
        assert attr.ssid == ssid

    @pytest.mark.parametrize("octets, device_address, ssid", [
        ('010203040506', b'\1\2\3\4\5\6', b''),
        ('010203040506616263', b'\1\2\3\4\5\6', b'abc'),
    ])
    def test_decode(self, octets, device_address, ssid):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.PeerToPeerGroupID.decode(data)
        assert attr.device_address == device_address
        assert attr.ssid == ssid

    @pytest.mark.parametrize("octets, device_address, ssid", [
        ('010203040506', b'\1\2\3\4\5\6', b''),
        ('010203040506616263', b'\1\2\3\4\5\6', b'abc'),
    ])
    def test_encode(self, octets, device_address, ssid):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.PeerToPeerGroupID(device_address, ssid)
        assert attr.encode() == data

    def test_format(self):
        attr = ndef.wifi.PeerToPeerGroupID(b'\1\2\3\4\5\6', b'my-ssid')
        assert "{:args}".format(attr) == \
            B("'\\x01\\x02\\x03\\x04\\x05\\x06', ") + B("'my-ssid'")
        assert "{}".format(attr) == "P2P Group ID {} {}".format(
            '01:02:03:04:05:06', ndef.wifi.SSID(b'my-ssid'))


class TestAttribute_NegotiationChannel:
    @pytest.mark.parametrize("args, values", [
        ((b'de\x04', 81, 6, 0),
         (b'de\x04', 81, 6, (0, 'Not Member'))),
        ((b'de\x04', 81, 6, 'Group Client'),
         (b'de\x04', 81, 6, (1, 'Group Client'))),
    ])
    def test_init(self, args, values):
        attr = ndef.wifi.NegotiationChannel(*args)
        assert attr.country_string == values[0]
        assert attr.operating_class == values[1]
        assert attr.channel_number == values[2]
        assert attr.role_indication == values[3]

    @pytest.mark.parametrize("octets, values", [
        ('646504510600', (b'de\x04', 81, 6, (0, 'Not Member'))),
        ('646504510601', (b'de\x04', 81, 6, (1, 'Group Client'))),
        ('646504510602', (b'de\x04', 81, 6, (2, 'Group Owner'))),
        ('646504510603', (b'de\x04', 81, 6, (3,))),
    ])
    def test_decode(self, octets, values):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.NegotiationChannel.decode(data)
        assert attr.country_string == values[0]
        assert attr.operating_class == values[1]
        assert attr.channel_number == values[2]
        assert attr.role_indication == values[3]

    @pytest.mark.parametrize("octets, args", [
        ('646504510600', (b'de\x04', 81, 6, 'Not Member')),
        ('646504510601', (b'de\x04', 81, 6, 'Group Client')),
        ('646504510602', (b'de\x04', 81, 6, 'Group Owner')),
        ('646504510603', (b'de\x04', 81, 6, 3)),
    ])
    def test_encode(self, octets, args):
        data = bytearray.fromhex(octets)
        attr = ndef.wifi.NegotiationChannel(*args)
        assert attr.encode() == data

    def test_format(self):
        attr = ndef.wifi.NegotiationChannel(b'de\x04', 81, 6, 0)
        assert "{:args}".format(attr) == B("'de\\x04'") + ", 81, 6, 0"
        assert "{}".format(attr) == "Negotiation Channel Country DE "\
            "Table E-4 Class 81 Channel 6 Role 'Not Member'"
        attr = ndef.wifi.NegotiationChannel(b'de\x04', 81, 6, 3)
        assert "{:args}".format(attr) == B("'de\\x04'") + ", 81, 6, 3"
        assert "{}".format(attr) == "Negotiation Channel Country DE "\
            "Table E-4 Class 81 Channel 6 Role 3"


class TestWifiSimpleConfigRecord:
    @pytest.mark.parametrize("octets, errstr", [
        ('0001000110', "reserved attribute type 0x0001 at offset 0"),
        ('10000001000001000110', "reserved attribute type 0x0001 at offset 5"),
    ])
    def test_decode_fail(self, octets, errstr):
        RECORD = ndef.wifi.WifiSimpleConfigRecord
        octets = bytes(bytearray.fromhex(octets))
        errstr = "ndef.wifi.WifiSimpleConfigRecord " + errstr
        with pytest.raises(ndef.DecodeError) as excinfo:
            RECORD._decode_payload(octets, 'strict')
        assert str(excinfo.value) == errstr
        with pytest.raises(ndef.DecodeError) as excinfo:
            RECORD._decode_payload(octets, 'relax')
        assert str(excinfo.value) == errstr

    def test_contains(self):
        record = ndef.wifi.WifiSimpleConfigRecord()
        assert 'mac-address' not in record
        record.add_attribute('mac-address', b'\1\2\3\4\5\6')
        assert 'mac-address' in record
        record.add_attribute('mac-address', b'\6\5\4\3\2\1')
        assert 'mac-address' in record

    def test_keys_values_items(self):
        record = ndef.wifi.WifiSimpleConfigRecord()
        record.add_attribute('mac-address', b'\1\2\3\4\5\6')
        record.add_attribute('ap-channel', 6)
        assert list(record.keys()) == [0x1020, 0x1001]
        assert list(record.values()) == [[b'\1\2\3\4\5\6'], [b'\0\6']]
        assert list(record.items()) == \
            [(0x1020, [b'\1\2\3\4\5\6']), (0x1001, [b'\0\6'])]

    def test_invalid_key(self):
        errstr = "unknown attribute name 'wrong-name'"
        record = ndef.wifi.WifiSimpleConfigRecord()
        with pytest.raises(ValueError) as excinfo:
            record.get('wrong-name')
        assert str(excinfo.value) == errstr

    def test_attribute_names(self):
        attribute_names = (
            'ap-channel',
            'credential',
            'device-name',
            'mac-address',
            'manufacturer',
            'model-name',
            'model-number',
            'oob-password',
            'primary-device-type',
            'rf-bands',
            'secondary-device-type-list',
            'serial-number',
            'uuid-enrollee',
            'uuid-registrar',
            'vendor-extension',
            'version-1',
        )
        record = ndef.wifi.WifiSimpleConfigRecord()
        assert sorted(record.attribute_names) == sorted(attribute_names)

    def test_get_attribute(self):
        octets = '10200006010203040506 10200006060504030201'
        record = ndef.wifi.WifiSimpleConfigRecord()
        assert record.get_attribute('mac-address') is None
        record.add_attribute('mac-address', b'\1\2\3\4\5\6')
        assert record.get_attribute('mac-address').value == b'\1\2\3\4\5\6'
        assert record.get_attribute('mac-address', 1) is None
        record.add_attribute('mac-address', b'\6\5\4\3\2\1')
        assert record.get_attribute('mac-address', 1).value == b'\6\5\4\3\2\1'
        assert record.get_attribute('mac-address', 2) is None
        assert record._encode_payload() == bytearray.fromhex(octets)

    def test_add_attribute(self):
        octets = '10200006010203040506 10200006060504030201'
        record = ndef.wifi.WifiSimpleConfigRecord()
        record.add_attribute('mac-address', b'\1\2\3\4\5\6')
        record.add_attribute('mac-address', b'\6\5\4\3\2\1')
        assert len(record['mac-address']) == 2
        assert record._encode_payload() == bytearray.fromhex(octets)

    def test_add_attribute(self):
        octets = '10200006010203040506 10200006060504030201'
        record = ndef.wifi.WifiSimpleConfigRecord((0x1020, b'\1\2\3\4\5\6'))
        record.add_attribute('mac-address', b'\6\5\4\3\2\1')
        assert len(record['mac-address']) == 2
        assert record._encode_payload() == bytearray.fromhex(octets)
        record.set_attribute('mac-address', b'\1\2\3\4\5\6')
        assert len(record['mac-address']) == 1
        assert record._encode_payload() == bytearray.fromhex(octets.split()[0])

    def test_wfa_vendor_extension(self):
        record = ndef.wifi.WifiSimpleConfigRecord()
        assert record.get_attribute('wfa-vendor-extension') is None
        record.add_attribute('vendor-extension', b'\1\2\3', b'\4\5\6')
        assert record.get_attribute('vendor-extension') is not None
        assert record.get_attribute('wfa-vendor-extension') is None
        record.add_attribute('wfa-vendor-extension', (0, b'\x20'))
        assert record.get_attribute('wfa-vendor-extension') is not None
        wfaext = record.get_attribute('wfa-vendor-extension')
        assert wfaext.get_attribute('version-2').value == (2, 0)

    def test_repr(self):
        clsstr = "ndef.wifi.WifiSimpleConfigRecord"
        record = ndef.wifi.WifiSimpleConfigRecord()
        assert repr(record) == clsstr + "()"
        record[1] = [b'ab']
        assert repr(record) == clsstr + "((0x01, " + B("'ab'") + "))"

    def test_str(self):
        common = "NDEF Wifi Simple Config Record ID '' Attributes "
        record = ndef.wifi.WifiSimpleConfigRecord()
        assert str(record) == common + ""
        record[1] = [b'ab']
        assert str(record) == common + "0x01"
        record[0x1001] = [b'cd']
        assert str(record) == common + "0x01 0x1001"


class TestWifiPasswordFormat:
    @pytest.mark.parametrize("octets, pkhash, pwd_id, passwd", [
        ('104a 0001 10 102c 0026 0a38808c8675902968a80b7c7863e0b1d4d8911d 071b'
         '6d792d776c616e2d70617373776f7264 1049 0006 00372a000120',
         "0a38808c8675902968a80b7c7863e0b1d4d8911d",
         0x071b, b"my-wlan-password"),
        ('104a 0001 10 102c 0036 0a38808c8675902968a80b7c7863e0b1d4d8911d 0710'
         '6d792d776c616e2d70617373776f72646d792d776c616e2d70617373776f7264'
         '1049 0006 00372a000120',
         "0a38808c8675902968a80b7c7863e0b1d4d8911d",
         0x0710, b"my-wlan-password" + b"my-wlan-password"),
        ('0039 104a 0001 10 102c 0026 0a38808c8675902968a80b7c7863e0b1d4d8911d'
         '071b 6d792d776c616e2d70617373776f7264 1049 0006 00372a000120',
         "0a38808c8675902968a80b7c7863e0b1d4d8911d",
         0x071b, b"my-wlan-password"),
    ])
    def test_decode(self, octets, pkhash, pwd_id, passwd):
        RECORD = ndef.wifi.WifiSimpleConfigRecord
        octets = bytes(bytearray.fromhex(octets))
        record = RECORD._decode_payload(octets, 'strict')
        vers_1 = record.get_attribute('version-1')
        assert vers_1 and vers_1.value == (1, 0)
        wfaext = record.get_attribute('wfa-vendor-extension')
        assert wfaext and wfaext.get_attribute('version-2').value == (2, 0)
        oobpwd = record.get_attribute('oob-password')
        assert oobpwd.public_key_hash == bytes(bytearray.fromhex(pkhash))
        assert oobpwd.password_id == pwd_id
        assert oobpwd.device_password == passwd

    @pytest.mark.parametrize("octets, pkhash, pwd_id, passwd", [
        ('102c0026 0a38808c8675902968a80b7c7863e0b1d4d8911d 071b'
         '6d792d776c616e2d70617373776f7264 1049000600372a000120 104a000110',
         "0a38808c8675902968a80b7c7863e0b1d4d8911d",
         0x071b, b"my-wlan-password"),
        ('102c 0036 0a38808c8675902968a80b7c7863e0b1d4d8911d 0710'
         '6d792d776c616e2d70617373776f72646d792d776c616e2d70617373776f7264'
         '1049000600372a000120 104a000110',
         "0a38808c8675902968a80b7c7863e0b1d4d8911d",
         0x0710, b"my-wlan-password" + b"my-wlan-password"),
        ('0029 102c 0016 0a38808c8675902968a80b7c7863e0b1d4d8911d 0007'
         '1049000600372a000120 104a000110',
         "0a38808c8675902968a80b7c7863e0b1d4d8911d",
         0x0007, b""),
    ])
    def test_encode(self, octets, pkhash, pwd_id, passwd):
        pkhash = bytes(bytearray.fromhex(pkhash))
        wfaext = ndef.wifi.WifiAllianceVendorExtension()
        wfaext.set_attribute('version-2', 2, 0)
        record = ndef.wifi.WifiSimpleConfigRecord()
        record.set_attribute('version-1', 1, 0)
        record.set_attribute('wfa-vendor-extension', wfaext)
        record.set_attribute('oob-password', pkhash, pwd_id, passwd)
        assert record._encode_payload() == bytes(bytearray.fromhex(octets))


class TestWifiConfigTokenFormat:
    one_credential_payload = (
        '100E 0037'                            # 000: Credential
        '     1003 0002 0001'                  # 004: Authentication Type
        '     100F 0002 0001'                  # 010: Encryption Type
        '     1020 0006 010203040506'          # 016: MAC Address
        '     1026 0001 01'                    # 026: Network Index
        '     1027 000a 31323334353637383930'  # 031: Network Key
        '     1045 000a 6162636465666768696a'  # 045: SSID
        '1049 0006 00372a000120'               # 059: WFA Extension
    )                                          # 069: end
    two_credential_payload = (
        '100E 0037'                            # Credential
        '     1003 0002 0001'                  # Authentication Type
        '     100F 0002 0001'                  # Encryption Type
        '     1020 0006 010203040506'          # MAC Address 01:02:03:04:05:06
        '     1026 0001 01'                    # Network Index
        '     1027 000a 31323334353637383930'  # Network Key
        '     1045 000a 6162636465666768696a'  # SSID
        '100E 0037'                            # Credential
        '     1003 0002 0001'                  # Authentication Type
        '     100F 0002 0001'                  # Encryption Type
        '     1020 0006 060504030201'          # MAC Address 06:05:04:03:02:01
        '     1026 0001 01'                    # Network Index
        '     1027 000a 31323334353637383930'  # Network Key
        '     1045 000a 6162636465666768696a'  # SSID
        '1049 0006 00372a000120'               # WFA Extension
    )

    def test_decode_one_credential_payload(self):
        RECORD = ndef.wifi.WifiSimpleConfigRecord
        octets = bytes(bytearray.fromhex(self.one_credential_payload))
        record = RECORD._decode_payload(octets, 'strict')
        assert (record.get_attribute('wfa-vendor-extension')
                .get_attribute('version-2').value) == (2, 0)
        assert record.get('credential') is not None
        assert len(record.get('credential')) == 1
        cred = record.get_attribute('credential')
        assert cred.get_attribute('authentication-type').value[0] == 1
        assert cred.get_attribute('authentication-type').value[1] == 'Open'
        assert cred.get_attribute('encryption-type').value[0] == 1
        assert cred.get_attribute('encryption-type').value[1] == 'None'
        assert cred.get_attribute('mac-address').value == b'\1\2\3\4\5\6'
        assert cred.get_attribute('network-index').value == 1
        assert cred.get_attribute('network-key').value == b'1234567890'
        assert cred.get_attribute('ssid').value == b'abcdefghij'
    
    def test_encode_one_credential_payload(self):
        octets = bytes(bytearray.fromhex(self.one_credential_payload))
        record = ndef.wifi.WifiSimpleConfigRecord()
        record.set_attribute('wfa-vendor-extension', ('version-2', b'\x20'))
        cred = ndef.wifi.Credential()
        cred.set_attribute('authentication-type', 'Open')
        cred.set_attribute('encryption-type', 'None')
        cred.set_attribute('mac-address', b'\1\2\3\4\5\6')
        cred.set_attribute('network-index', 1)
        cred.set_attribute('network-key', b'1234567890')
        cred.set_attribute('ssid', b'abcdefghij')
        record.set_attribute('credential', cred)
        assert record._encode_payload() == octets

    def test_decode_one_credential_payload(self):
        RECORD = ndef.wifi.WifiSimpleConfigRecord
        octets = bytes(bytearray.fromhex(self.two_credential_payload))
        record = RECORD._decode_payload(octets, 'strict')
        assert (record.get_attribute('wfa-vendor-extension')
                .get_attribute('version-2').value) == (2, 0)
        assert record.get('credential') is not None
        assert len(record.get('credential')) == 2
        for index in range(2):
            mac = (b'\1\2\3\4\5\6', b'\6\5\4\3\2\1')[index]
            cred = record.get_attribute('credential', index)
            assert cred.get_attribute('authentication-type').value[0] == 1
            assert cred.get_attribute('authentication-type').value[1] == 'Open'
            assert cred.get_attribute('encryption-type').value[0] == 1
            assert cred.get_attribute('encryption-type').value[1] == 'None'
            assert cred.get_attribute('mac-address').value == mac
            assert cred.get_attribute('network-index').value == 1
            assert cred.get_attribute('network-key').value == b'1234567890'
            assert cred.get_attribute('ssid').value == b'abcdefghij'
    
    def test_encode_two_credential_payload(self):
        octets = bytes(bytearray.fromhex(self.two_credential_payload))
        record = ndef.wifi.WifiSimpleConfigRecord()
        record.set_attribute('wfa-vendor-extension', ('version-2', b'\x20'))
        for mac_address in (b'\1\2\3\4\5\6', b'\6\5\4\3\2\1'):
            cred = ndef.wifi.Credential()
            cred.set_attribute('authentication-type', 'Open')
            cred.set_attribute('encryption-type', 'None')
            cred.set_attribute('mac-address', mac_address)
            cred.set_attribute('network-index', 1)
            cred.set_attribute('network-key', b'1234567890')
            cred.set_attribute('ssid', b'abcdefghij')
            record.add_attribute('credential', cred)
        assert record._encode_payload() == octets


class TestWifiPeerToPeerRecord:
    CLASSNAME = "ndef.wifi.WifiPeerToPeerRecord"
    hp_printer_payload = (
        '0089'                                        # 000: WSC Data Length
        '1021 0002 4850'                              # 002: Manufacturer
        '1023 001a 4850204f66666963 656a65742050726f' # 008: Model Name
        '          203237366477204d 4650'
        '1024 0006 513132333454'                      # 038: Model Number
        '102c 0026 0000000000000000 0000000000000000' # 048: OOB Password
        '          00000000787a100a 200b300c400d500e'
        '          600f70018002'
        '103c 0001 01'                                # 090: RF Bands
        '1042 000a 5858585858585858 5858'             # 095: Serial Number
        '1047 0010 dc1281ef012c4839 831ee9f1e8944393' # 109: UUID-E
        '1049 0006 00372a 000120'                     # 129: WFA Extension
        '0051'                                        # 139: P2P Data Length
        '02 0002 0783'                                # 141: P2P Capability
        '0d 001d 02bad0f8f0e00098 00030050f2040005'   # 146: P2p Device Info
        '        0010110008485020 50686f746f'
        '0f 0020 d89d675302474449 524543542d34362d'   # 178: P2P Group ID
        '        454e565920353530 3020736572696573'
        '13 0006 4b5204510602'                        # 213: Negotiation Channel
    )                                                 # 222: end

    def test_hp_printer_payload(self):
        RECORD = ndef.wifi.WifiPeerToPeerRecord
        octets = bytes(bytearray.fromhex(self.hp_printer_payload))
        record = RECORD._decode_payload(octets, 'strict')
        assert record.get_attribute('manufacturer').value == "HP"
        assert record.get_attribute('model-name').value == "HP Officejet Pro 276dw MFP"
        assert record.get_attribute('model-number').value == "Q1234T"
        oobpwd = record.get_attribute('oob-password')
        assert oobpwd.public_key_hash == 20 * b'\x00'
        assert oobpwd.password_id == 30842
        assert oobpwd.device_password == b'\x10\n \x0b0\x0c@\rP\x0e`\x0fp\x01\x80\x02'
        assert record.get_attribute('rf-bands').value == (1, '2.4GHz')
        assert record.get_attribute('serial-number').value == "XXXXXXXXXX"
        assert record.get_attribute('uuid-enrollee').value == "dc1281ef-012c-4839-831e-e9f1e8944393"
        wfaext = record.get_attribute('wfa-vendor-extension')
        assert wfaext.get_attribute('version-2').value == (2, 0)
        assert record.get_attribute('p2p-capability').device_capability == \
            (7, 'Service Discovery', 'P2P Client Discoverability', 'Concurrent Operation')
        assert record.get_attribute('p2p-capability').group_capability == \
            (131, 'P2P Group Owner', 'Persistent P2P Group', 'IP Address Allocation')
        dvinfo = record.get_attribute('p2p-device-info')
        assert dvinfo.device_address == b'\x02\xba\xd0\xf8\xf0\xe0'
        assert dvinfo.config_methods == (152, 'Display', 'External NFC Token', 'Push Button')
        assert dvinfo.primary_device_type == "Printer::Multifunction"
        assert dvinfo.secondary_device_type_list == ()
        assert dvinfo.device_name == "HP Photo"
        negoch = record.get_attribute('negotiation-channel')
        assert negoch.country_string == b"KR\x04"
        assert negoch.operating_class == 81
        assert negoch.channel_number == 6
        p2pgrp = record.get_attribute('p2p-group-id')
        assert p2pgrp.device_address == b'\xd8\x9dgS\x02G'
        assert p2pgrp.ssid == b'DIRECT-46-ENVY 5500 series'
        assert record._encode_payload() == octets

    password_id_seven_payload = (
        '0079'                                        # 000: WSC Data Length
        '1021 0002 4850'                              # 002: Manufacturer
        '1023 001a 4850204f66666963 656a65742050726f' # 008: Model Name
        '          203237366477204d 4650'
        '1024 0006 513132333454'                      # 038: Model Number
        '102c 0016 0000000000000000 0000000000000000' # 048: OOB Password
        '          000000000007'
        '103c 0001 01'                                # 074: RF Bands
        '1042 000a 5858585858585858 5858'             # 079: Serial Number
        '1047 0010 dc1281ef012c4839 831ee9f1e8944393' # 093: UUID-E
        '1049 0006 00372a 000120'                     # 113: WFA Extension
        '0051'                                        # 123: P2P Data Length
        '02 0002 0783'                                # 125: P2P Capability
        '0d 001d 02bad0f8f0e00098 00030050f2040005'   # 130: P2p Device Info
        '        0010110008485020 50686f746f'
        '0f 0020 d89d675302474449 524543542d34362d'   # 162: P2P Group ID
        '        454e565920353530 3020736572696573'
        '13 0006 4b5204510602'                        # 197: Negotiation Channel
    )                                                 # 206: end
    def test_password_id_seven_payload(self):
        RECORD = ndef.wifi.WifiPeerToPeerRecord
        octets = bytes(bytearray.fromhex(self.password_id_seven_payload))
        record = RECORD._decode_payload(octets, 'strict')
        assert record.get_attribute('manufacturer').value == "HP"
        assert record.get_attribute('model-name').value == "HP Officejet Pro 276dw MFP"
        assert record.get_attribute('model-number').value == "Q1234T"
        oobpwd = record.get_attribute('oob-password')
        assert oobpwd.public_key_hash == 20 * b'\x00'
        assert oobpwd.password_id == 7
        assert record.get_attribute('rf-bands').value == (1, '2.4GHz')
        assert record.get_attribute('serial-number').value == "XXXXXXXXXX"
        assert record.get_attribute('uuid-enrollee').value == "dc1281ef-012c-4839-831e-e9f1e8944393"
        wfaext = record.get_attribute('wfa-vendor-extension')
        assert wfaext.get_attribute('version-2').value == (2, 0)
        assert record.get_attribute('p2p-capability').device_capability == \
            (7, 'Service Discovery', 'P2P Client Discoverability', 'Concurrent Operation')
        assert record.get_attribute('p2p-capability').group_capability == \
            (131, 'P2P Group Owner', 'Persistent P2P Group', 'IP Address Allocation')
        dvinfo = record.get_attribute('p2p-device-info')
        assert dvinfo.device_address == b'\x02\xba\xd0\xf8\xf0\xe0'
        assert dvinfo.config_methods == (152, 'Display', 'External NFC Token', 'Push Button')
        assert dvinfo.primary_device_type == "Printer::Multifunction"
        assert dvinfo.secondary_device_type_list == ()
        assert dvinfo.device_name == "HP Photo"
        negoch = record.get_attribute('negotiation-channel')
        assert negoch.country_string == b"KR\x04"
        assert negoch.operating_class == 81
        assert negoch.channel_number == 6
        p2pgrp = record.get_attribute('p2p-group-id')
        assert p2pgrp.device_address == b'\xd8\x9dgS\x02G'
        assert p2pgrp.ssid == b'DIRECT-46-ENVY 5500 series'
        assert record._encode_payload() == octets


    def test_missing_wsc_data(self):
        RECORD = ndef.wifi.WifiPeerToPeerRecord
        octets = bytes(bytearray.fromhex('0000 0000'))
        errstr = "insufficient WSC Data Length, got 0 octets"
        with pytest.raises(ndef.DecodeError) as excinfo:
            RECORD._decode_payload(octets, 'strict')
        assert str(excinfo.value) == self.CLASSNAME + " " + errstr

    def test_missing_attribute(self):
        RECORD = ndef.wifi.WifiPeerToPeerRecord
        octets = bytes(bytearray.fromhex('0005 104A000110 0000'))
        assert RECORD._decode_payload(octets, 'relax')
        errstr = "'manufacturer' attribute is required if errors is 'strict'"
        with pytest.raises(ndef.DecodeError) as excinfo:
            RECORD._decode_payload(octets, 'strict')
        assert str(excinfo.value) == self.CLASSNAME + " " + errstr
        errstr = "'manufacturer' attribute is required for encoding"
        with pytest.raises(ndef.EncodeError) as excinfo:
            RECORD()._encode_payload()
        assert str(excinfo.value) == self.CLASSNAME + " " + errstr



