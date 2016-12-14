# -*- coding: utf-8 -*-
"""Decoding and encoding of Bluetooth Out-Of-Band Records.

"""
from __future__ import absolute_import, division
from .record import Record, GlobalRecord, convert, _PY2
from .record import decode_error, encode_error
from uuid import UUID
import struct
import re


class DeviceAddress(object):
    def __init__(self, address, address_type='public'):
        self.addr = address
        self.type = address_type

    @property
    def addr(self):
        return self._addr

    @addr.setter
    def addr(self, value):
        assert re.match(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', value)
        self._addr = re.sub(r'-', ':', value)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        assert value in ('public', 'random')
        self._type = value

    def __str__(self):
        return "{addr.addr} ({addr.type})".format(addr=self)

    def __repr__(self):
        return "{}.{}({!r}, {!r})".format(
            self.__module__, self.__class__.__name__, self.addr, self.type)

    def encode(self, context='LE'):
        assert context in ('LE', 'EP')
        octets = bytearray(int(x, 16) for x in reversed(self.addr.split(':')))
        if context == 'LE':
            octets.append({'public': 0, 'random': 1}[self.type])
        return bytes(octets)

    @classmethod
    def decode(cls, octets):
        if len(octets) == 6:
            addr_t = 'public'
            addr_v = ':'.join(['%02X' % x for x in bytearray(octets[::-1])])
            return cls(addr_v, addr_t)
        elif len(octets) == 7:
            addr_v, addr_t = struct.unpack('6sB', octets)
            addr_t = 'random' if addr_t & 1 else 'public'
            addr_v = ':'.join(['%02X' % x for x in bytearray(addr_v[::-1])])
            return cls(addr_v, addr_t)
        else:
            errstr = "can't be decoded from {} octets"
            raise decode_error(cls, errstr, len(octets))


class DeviceClass(object):
    service_class_name = (
        "Limited Discoverable Mode", "Reserved (bit 14)", "Reserved (bit 15)",
        "Positioning", "Networking", "Rendering", "Capturing",
        "Object Transfer", "Audio", "Telephony", "Information")

    device_class = {
        0: ('Miscellaneous', (
            {
                '000000': 'Uncategorized',
            },)),
        1: ('Computer', (
            {
                '000000': 'Uncategorized',
                '000001': 'Desktop workstation',
                '000010': 'Server-class computer',
                '000011': 'Laptop',
                '000100': 'Handheld PC/PDA (clam shell)',
                '000101': 'Palm sized PC/PDA',
                '000110': 'Wearable computer (Watch sized)',
                '000111': 'Tablet',
            },)),
        2: ('Phone', (
            {
                '000000': 'Uncategorized',
                '000001': 'Cellular',
                '000010': 'Cordless',
                '000011': 'Smartphone',
                '000100': 'Wired modem or voice gateway',
                '000101': 'Common ISDN Access',
            },)),
        3: ('LAN / Network Access point', (
            {
                '000': 'Fully available',
                '001': '1 - 17% utilized',
                '010': '17 - 33% utilized',
                '011': '33 - 50% utilized',
                '100': '50 - 67% utilized',
                '101': '67 - 83% utilized',
                '110': '83 - 99% utilized',
                '111': 'No service available',
            },)),
        4: ('Audio / Video', (
            {
                '000000': 'Uncategorized',
                '000001': 'Wearable Headset Device',
                '000010': 'Hands-free Device',
                '000011': '(Reserved)',
                '000100': 'Microphone',
                '000101': 'Loudspeaker',
                '000110': 'Headphones',
                '000111': 'Portable Audio',
                '001000': 'Car audio',
                '001001': 'Set-top box',
                '001010': 'HiFi Audio Device',
                '001011': 'VCR',
                '001100': 'Video Camera',
                '001101': 'Camcorder',
                '001110': 'Video Monitor',
                '001111': 'Video Display and Loudspeaker',
                '010000': 'Video Conferencing',
                '010001': '(Reserved)',
                '010010': 'Gaming/Toy',
            },)),
        5: ('Peripheral', (
            {
                '00': '',
                '01': 'Keyboard',
                '10': 'Pointing device',
                '11': 'Combo keyboard/pointing device',
            }, {
                '0000': 'Uncategorized device',
                '0001': 'Joystick',
                '0010': 'Gamepad',
                '0011': 'Remote control',
                '0100': 'Sensing device',
                '0101': 'Digitizer tablet',
                '0110': 'Card Reader',
                '0111': 'Digital Pen',
                '1000': 'Handheld scanner for ID codes',
                '1001': 'Handheld gestural input device',
            },)),
        6: ('Imaging', (
            {
                '0001': "Display",
                '0010': "Camera",
                '0011': "Display/Camera",
                '0100': "Scanner",
                '0101': "Display/Scanner",
                '0110': "Camera/Scanner",
                '0111': "Display/Camera/Scanner",
                '1000': "Printer",
                '1001': "Display/Printer",
                '1010': "Camera/Printer",
                '1011': "Display/Camera/Printer",
                '1100': "Scanner/Printer",
                '1101': "Display/Scanner/Printer",
                '1110': "Camera/Scanner/Printer",
                '1111': "Display/Camera/Scanner/Printer",
            },)),
        7: ('Wearable', (
            {
                '000001': 'Wristwatch',
                '000010': 'Pager',
                '000011': 'Jacket',
                '000100': 'Helmet',
                '000101': 'Glasses',
            },)),
        8: ("Toy", (
            {
                '000001': "Robot",
                '000010': "Vehicle",
                '000011': "Doll / Action figure",
                '000100': "Controller",
                '000101': "Game",
            },)),
        9: ("Health", (
            {
                '000000': "Undefined",
                '000001': "Blood Pressure Monitor",
                '000010': "Thermometer",
                '000011': "Weighing Scale",
                '000100': "Glucose Meter",
                '000101': "Pulse Oximeter",
                '000110': "Heart/Pulse Rate Monitor",
                '000111': "Health Data Display",
                '001000': "Step Counter",
                '001001': "Body Composition Analyzer",
                '001010': "Peak Flow Monitor",
                '001011': "Medication Monitor",
                '001100': "Knee Prosthesis",
                '001101': "Ankle Prosthesis",
                '001110': "Generic Health Manager",
                '001111': "Personal Mobility Device",
            },)),
        31: ('Uncategorized', ()),
    }

    def __init__(self, cod):
        self.cod = cod.cod if isinstance(cod, DeviceClass) else cod

    @property
    def major_service_class(self):
        if self.cod & 0b11 == 0:
            bits = [i-13 for i in range(13, 24) if self.cod >> i & 1]
            return tuple([self.service_class_name[i] for i in bits])

    @property
    def major_device_class(self):
        if self.cod & 0b11 == 0:
            major = self.cod >> 8 & 0b11111
            if major in self.device_class:
                return self.device_class[major][0]
            else:
                return 'Reserved {:05b}b'.format(major)

    @property
    def minor_device_class(self):
        if self.cod & 0b11 == 0:
            text = []
            major = self.cod >> 8 & 0b11111
            minor = '{:06b}'.format(self.cod >> 2 & 0b111111)
            if major in self.device_class:
                for mapping in self.device_class[major][1]:
                    bits = minor[:len(next(iter(mapping)))]
                    text.append(mapping.get(bits, 'Reserved {}b'.format(bits)))
                    minor = minor[len(bits):]
                return ' and '.join(filter(None, text))
            else:
                return 'Undefined {}b'.format(minor)

    def __str__(self):
        if self.cod & 0b11 == 0:
            if self.major_service_class:
                major_service_class = ' and '.join(self.major_service_class)
            else:
                major_service_class = 'Unspecified'
            return ('{o.major_device_class} - {o.minor_device_class} - {0}'
                    .format(major_service_class, o=self))
        else:
            return 'Unknown format {:024b}b'.format(self.cod)

    def __repr__(self):
        return "{}.{}(0x{:06X})".format(
            self.__module__, self.__class__.__name__, self.cod)

    def encode(self):
        if 0 <= self.cod <= 0xFFFFFF:
            return struct.pack('<I', self.cod)[0:3]
        else:
            errstr = "can't encode {!r} into class of device octets"
            raise encode_error(self, errstr, self.cod)

    @classmethod
    def decode(cls, octets):
        if len(octets) == 3:
            return cls(struct.unpack('I', octets + b'\0')[0])
        else:
            errstr = "can't decode class of device from {} octets"
            raise decode_error(cls, errstr, len(octets))


class ServiceClass(UUID):
    bluetooth_base_uuid = UUID('00000000-0000-1000-8000-00805F9B34FB')
    bluetooth_uuid_list = {
        0x00001000: "Service Discovery Server",
        0x00001001: "Browse Group Descriptor",
        0x00001101: "Serial Port",
        0x00001102: "LAN Access Using PPP",
        0x00001103: "Dialup Networking",
        0x00001104: "IrMC Sync",
        0x00001105: "OBEX Object Push",
        0x00001106: "OBEX File Transfer",
        0x00001107: "IrMC Sync Command",
        0x00001108: "Headset",
        0x00001109: "Cordless Telephony",
        0x0000110a: "Audio Source",
        0x0000110b: "Audio Sink",
        0x0000110c: "A/V Remote Control Target",
        0x0000110d: "Advanced Audio Distribution",
        0x0000110e: "A/V Remote Control",
        0x0000110f: "A/V Remote Control Controller",
        0x00001110: "Intercom",
        0x00001111: "Fax",
        0x00001112: "Headset - Audio Gateway (AG)",
        0x00001113: "WAP",
        0x00001114: "WAP Client",
        0x00001115: "PANU",
        0x00001116: "NAP",
        0x00001117: "GN",
        0x00001118: "Direct Printing",
        0x00001119: "Reference Printing",
        0x0000111a: "Basic Imaging Profile",
        0x0000111b: "Imaging Responder",
        0x0000111c: "Imaging Automatic Archive",
        0x0000111d: "Imaging Referenced Objects",
        0x0000111e: "Handsfree",
        0x0000111f: "Handsfree Audio Gateway",
        0x00001120: "Direct Printing Reference",
        0x00001121: "Reflected UI",
        0x00001122: "Basic Printing",
        0x00001123: "Printing Status",
        0x00001124: "Human Interface Device",
        0x00001125: "Hardcopy Cable Replacement",
        0x00001126: "HCR Print",
        0x00001127: "HCR Scan",
        0x00001128: "Common ISDN Access",
        0x0000112d: "SIM Access",
        0x0000112e: "Phonebook Access - PCE",
        0x0000112f: "Phonebook Access - PSE",
        0x00001130: "Phonebook Access",
        0x00001131: "Headset - HS",
        0x00001132: "Message Access Server",
        0x00001133: "Message Notification Server",
        0x00001134: "Message Access Profile",
        0x00001135: "GNSS",
        0x00001136: "GNSS Server",
        0x00001200: "PnP Information",
        0x00001201: "Generic Networking",
        0x00001202: "Generic File Transfer",
        0x00001203: "Generic Audio",
        0x00001204: "Generic Telephony",
        0x00001205: "UPNP Service",
        0x00001206: "UPNP IP Service",
        0x00001300: "ESDP UPNP IP PAN",
        0x00001301: "ESDP UPNP IP LAP",
        0x00001302: "ESDP UPNP L2CAP",
        0x00001303: "Video Source",
        0x00001304: "Video Sink",
        0x00001305: "Video Distribution",
        0x00001400: "HDP",
        0x00001401: "HDP Source",
        0x00001402: "HDP Sink",
    }

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], int):
            fields = (args[0],) + self.bluetooth_base_uuid.fields[1:]
            super(ServiceClass, self).__init__(fields=fields)
        elif args and args[0] in self.bluetooth_uuid_list.values():
            index = list(self.bluetooth_uuid_list.values()).index(args[0])
            value = list(self.bluetooth_uuid_list.keys())[index]
            fields = (value,) + self.bluetooth_base_uuid.fields[1:]
            super(ServiceClass, self).__init__(fields=fields)
        else:
            super(ServiceClass, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "{}.{}({!r})".format(
            self.__module__, self.__class__.__name__, str(self))

    @property
    def name(self):
        if self.fields[1:] == self.bluetooth_base_uuid.fields[1:]:
            return self.bluetooth_uuid_list.get(self.fields[0], str(self))
        return super(ServiceClass, self).__str__()

    @classmethod
    def get_uuid_names(cls):
        return tuple(cls.bluetooth_uuid_list.values())

    def encode(self):
        if self.fields[1:] == self.bluetooth_base_uuid.fields[1:]:
            fmt = '<H' if self.fields[0] < 0x10000 else '<I'
            return struct.pack(fmt, self.fields[0])
        return self.bytes_le

    @classmethod
    def decode(cls, octets):
        if len(octets) in (2, 4):
            value = struct.unpack('<H' if len(octets) == 2 else '<I', octets)
            return cls(fields=value+cls.bluetooth_base_uuid.fields[1:])
        elif len(octets) == 16:
            return cls(bytes_le=octets)
        else:
            errstr = "can't decode service class uuid from {} octets"
            raise decode_error(cls, errstr, len(octets))


class BluetoothRecord(GlobalRecord):
    _attribute_name_mapping = {
        'Flags': 0x01,
        'Incomplete List of 16-bit Service Class UUIDs': 0x02,
        'Complete List of 16-bit Service Class UUIDs': 0x03,
        'Incomplete List of 32-bit Service Class UUIDs': 0x04,
        'Complete List of 32-bit Service Class UUIDs': 0x05,
        'Incomplete List of 128-bit Service Class UUIDs': 0x06,
        'Complete List of 128-bit Service Class UUIDs': 0x07,
        'Shortened Local Name': 0x08,
        'Complete Local Name': 0x09,
        'Class of Device': 0x0D,
        'Simple Pairing Hash C': 0x0E,
        'Simple Pairing Hash C-192': 0x0E,
        'Simple Pairing Randomizer R': 0x0F,
        'Simple Pairing Randomizer R-192': 0x0F,
        'Security Manager TK Value': 0x10,
        'Security Manager Out of Band Flags': 0x11,
        'LE Secure Connections Confirmation Value': 0x22,
        'LE Secure Connections Random Value': 0x23,
        'LE Bluetooth Device Address': 0x1B,
        'LE Role': 0x1C,
        'Simple Pairing Hash C-256': 0x1D,
        'Simple Pairing Randomizer R-256': 0x1E,
        'Manufacturer Specific Data': 0xFF,
    }

    @property
    def attribute_names(self):
        return tuple(self._attribute_name_mapping.keys())

    def _map_key(self, key):
        if isinstance(key, int):
            return key
        elif key in self._attribute_name_mapping:
            return self._attribute_name_mapping[key]
        else:
            errstr = "unknown attribute name '{name}'"
            raise ValueError(errstr.format(name=key))

    def __init__(self, *args):
        self._attributes = dict()
        for _type, _value in args:
            self[_type] = _value

    def __getitem__(self, key):
        return self._attributes[self._map_key(key)]

    def __setitem__(self, key, value):
        assert isinstance(value, (bytes, bytearray))
        self._attributes[self._map_key(key)] = value

    def __delitem__(self, key):
        del self._attributes[self._map_key(key)]

    def __contains__(self, key):
        return self._map_key(key) in self._attributes

    def __iter__(self):
        return self._attributes.__iter__()

    def get(self, key, default=None):
        return self._attributes.get(self._map_key(key), default)

    def setdefault(self, key, default=None):
        return self._attributes.setdefault(self._map_key(key), default)

    def keys(self):
        return self._attributes.keys()

    def values(self):
        return self._attributes.values()

    def items(self):
        return self._attributes.items()

    def __format__(self, format_spec):
        if format_spec == 'args':
            afmt = "(0x{:02X}, {!r})"
            args = [afmt.format(k, v) for k, v in self.items()]
            return ', '.join(args)
        elif format_spec == 'data':
            keys = ["0x{:02X}".format(k) for k in self]
            return "Attributes {}".format(' '.join(keys))
        else:
            return super(BluetoothRecord, self).__format__(format_spec)


class BluetoothEasyPairingRecord(BluetoothRecord):
    _type = 'application/vnd.bluetooth.ep.oob'

    def __init__(self, device_address, *eir):
        super(BluetoothEasyPairingRecord, self).__init__(*eir)
        self.device_address = device_address

    @property
    def device_address(self):
        return DeviceAddress.decode(self.bd_addr)

    @device_address.setter
    def device_address(self, value):
        if not isinstance(value, DeviceAddress):
            value = DeviceAddress(value)
        self.bd_addr = value.encode('EP')

    @property
    def device_name(self):
        return (
            self.get('Complete Local Name') or
            self.get('Shortened Local Name', b'')
        ).decode('utf-8')

    @device_name.setter
    @convert('value_to_unicode')
    def device_name(self, value):
        self['Complete Local Name'] = value.encode('utf-8')
        if 'Shortened Local Name' in self:
            del self['Shortened Local Name']

    @property
    def device_class(self):
        try:
            return DeviceClass.decode(self['Class of Device'])
        except KeyError:
            return DeviceClass(0)

    @device_class.setter
    def device_class(self, value):
        if not isinstance(value, DeviceClass):
            value = DeviceClass(value)
        self['Class of Device'] = value.encode()

    @property
    def service_class_list(self):
        """List of service class UUIDs build from all available service class
        UUID attributes.

        """
        uuid_list = []
        octets = self.get(0x02, b'') + self.get(0x03, b'')
        for offset in range(0, len(octets), 2):
            uuid_list.append(ServiceClass.decode(octets[offset:offset+2]))
        octets = self.get(0x04, b'') + self.get(0x05, b'')
        for offset in range(0, len(octets), 4):
            uuid_list.append(ServiceClass.decode(octets[offset:offset+4]))
        octets = self.get(0x06, b'') + self.get(0x07, b'')
        for offset in range(0, len(octets), 16):
            uuid_list.append(ServiceClass.decode(octets[offset:offset+16]))
        return uuid_list

    def add_service_class(self, service_class, complete=False):
        """Add a service class identifier. The *service_class* argument must
        be given as either a `ServiceClass` object, a UUID string, or
        as the integer value of a 16 or 32 bit Bluetooth Service Class
        UUID. The optional argument *complete* determines whether a
        list of complete or incomplete service class identifiers is
        populated. In case of multiple additions it is the last value
        of *complete* that counts.

        """
        if not isinstance(service_class, ServiceClass):
            service_class = ServiceClass(service_class)

        octets = service_class.encode()
        if len(octets) == 2:
            octets = self.get(0x02, b'') + self.get(0x03, b'') + octets
            self[0x03 if complete else 0x02] = octets
            try:
                del self[0x02 if complete else 0x03]
            except KeyError:
                pass
        elif len(octets) == 4:
            octets = self.get(0x04, b'') + self.get(0x05, b'') + octets
            self[0x05 if complete else 0x04] = octets
            try:
                del self[0x04 if complete else 0x05]
            except KeyError:
                pass
        else:
            octets = self.get(0x06, b'') + self.get(0x07, b'') + octets
            self[0x07 if complete else 0x06] = octets
            try:
                del self[0x06 if complete else 0x07]
            except KeyError:
                pass

    def get_simple_pairing_hash(self, variant='C-192'):
        assert variant in ('C-192', 'C-256')
        octets = self.get('Simple Pairing Hash {}'.format(variant))
        if octets is not None:
            return (int((octets[::-1]).encode('hex'), base=16) if _PY2
                    else int.from_bytes(octets, byteorder='little'))

    def set_simple_pairing_hash(self, value, variant='C-192'):
        assert variant in ('C-192', 'C-256')
        octets = ('{:032x}'.format(value).decode('hex')[::-1] if _PY2
                  else value.to_bytes(16, byteorder='little'))
        self['Simple Pairing Hash {}'.format(variant)] = octets

    def get_simple_pairing_randomizer(self, variant='R-192'):
        assert variant in ('R-192', 'R-256')
        octets = self.get('Simple Pairing Randomizer {}'.format(variant))
        if octets is not None:
            return (int((octets[::-1]).encode('hex'), base=16) if _PY2
                    else int.from_bytes(octets, byteorder='little'))

    def set_simple_pairing_randomizer(self, value, variant='R-192'):
        assert variant in ('R-192', 'R-256')
        octets = ('{:032x}'.format(value).decode('hex')[::-1] if _PY2
                  else value.to_bytes(16, byteorder='little'))
        self['Simple Pairing Randomizer {}'.format(variant)] = octets

    # BR/EDR out-of-band payload is OOB data length (2 octets), BDADDR
    # (6 octets), and a sequence of Extended Inquiry Response (EIR)
    # structures [CORE SPEC Vol 3 Part C Sect 5.2.2.7]. An EIR
    # structure is a single octet Length and Length octets Data
    # part. The Data part contains the EIR Type (n octets) and EIR
    # Data (Length - n octets). All defined EIR Types are single
    # octets.

    def _encode_payload(self):
        octets = [self.bd_addr]
        for attr_type, attr_data in self.items():
            data = self._encode_struct('B*', attr_type, attr_data)
            octets.append(self._encode_struct('B+', data))

        octets.insert(0, self._encode_struct('<H', 2 + sum(map(len, octets))))
        return b''.join(octets)

    _decode_min_payload_length = 8  # 2 octets OOB length and 6 octets BDADDR

    @classmethod
    def _decode_payload(cls, octets, errors):
        ooblen = cls._decode_struct('<H', octets)
        bdaddr = DeviceAddress.decode(octets[2:8])

        if len(octets) < ooblen:
            errstr = "oob data length {} exceeds payload size {}"
            raise cls._decode_error(errstr, ooblen, len(octets))

        if len(octets) > ooblen and errors == "strict":
            errstr = "payload size {} exceeds oob data length {}"
            raise cls._decode_error(errstr, len(octets), ooblen)

        offset, attrs = 8, []
        while offset < ooblen:
            data = cls._decode_struct('B+', octets, offset)
            if len(data) > 0:
                attr_type, attr_data = cls._decode_struct('B*', data)
                attrs.append((attr_type, attr_data))
                offset += len(attr_data) + 2
            else:
                offset += 1

        return cls(bdaddr, *attrs)


class BluetoothLowEnergyRecord(BluetoothRecord):
    _type = 'application/vnd.bluetooth.le.oob'

    @property
    def device_address(self):
        try:
            octets = self['LE Bluetooth Device Address']
            return DeviceAddress.decode(octets)
        except KeyError:
            return None

    @device_address.setter
    def device_address(self, value):
        if not isinstance(value, DeviceAddress):
            if isinstance(value, (tuple, list)):
                value = DeviceAddress(*value)
            else:
                value = DeviceAddress(value)
        self['LE Bluetooth Device Address'] = value.encode('LE')

    # Bluetooth LE out-of-band payload is coded as Advertising or Scan
    # Response Data (AD) format (only significant part). The format
    # consists of a sequence of AD structures made of a single octet
    # Length and Length octets Data part. The Data part contains the
    # AD Type (n octets) and AD Data (Length - n octets). All defined
    # AD Types are single octets.

    def _encode_payload(self):
        octets = []
        for attr_type, attr_data in self.items():
            data = self._encode_struct('B*', attr_type, attr_data)
            octets.append(self._encode_struct('B+', data))
        return b''.join(octets)

    @classmethod
    def _decode_payload(cls, octets, errors):
        offset, attrs = 0, []
        while offset < len(octets):
            data = cls._decode_struct('B+', octets, offset)
            if len(data) > 0:
                attr_type, attr_data = cls._decode_struct('B*', data)
                attrs.append((attr_type, attr_data))
                offset += len(attr_data) + 2
            else:
                offset += 1

        return cls(*attrs)


Record.register_type(BluetoothEasyPairingRecord)
Record.register_type(BluetoothLowEnergyRecord)
