.. -*- mode: rst; fill-column: 80 -*-

###############################
Bluetooth Secure Simple Pairing
###############################

.. note:: This is "work in progress" towards version 0.3

.. versionadded:: 0.3

Introduction
============

.. _Bluetooth Assigned Numbers: https://www.bluetooth.com/specifications/assigned-numbers

Bluetooth Secure Simple Pairing (SSP) has been introduced in Bluetooth Core
Specification Version 2.1 + EDR as a method by which two Bluetooth devices can
establish secure communication. With Bluetooth Core Specification Version 4.0
this was extended to cover Bluetooth Low Energy devices.

Bluetooth Secure Simple Pairing defines four different association models, one
of them is using an out-of-band channel such as NFC. Secure Simple Pairing
introduced in Bluetooth Version 2.1 + EDR uses Elliptic Curve Diffie-Hellman
with curve P-192. Bluetooth Version 4.1 added the Secure Connections feature,
which upgraded Secure Simple Pairing to utilize the P-256 elliptic curve. In
either case the out-of-band communication transfers a public key commitment
through a 128-bit hash and randomizer prior to in-band public key exchange.
Bluetooth BR/EDR key generation is performed in the Controller. Bluetooth Low
Energy, introduced with Core Specification Version 4.0, uses a Security Manager
component on the device host to generate keys. Three pairing methods - Just
Works, Passkey Entry, and Out of Band - were initially defined with protection
levels depending on the secrecy of temporary keys exchanged while
pairing. Bluetooth Version 4.2 then added LE Secure Connections with the same
pairing methods and P-256 based Elliptic Curve Diffie-Hellman as for BR/EDR
Secure Connections.

Bluetooth pairing is the process of connecting with a Bluetooth devices that has
been found by device discovery. The discovery process provides the identity of
the other device. The pairing process then yields a shared secret that is used
to derive encryption keys. There are four pairing methods: Numeric Comparision,
Just Works, Passkey Entry, and Out of Band. Numeric Comparision protects against
man-in-the-middle by having the user confirm equality of a six digit number
displayed on both devices. Just Works is basically the same but the number is
not shown for confirmation. Passkey Entry requires one device to have a keypad
and the other to have a display. A number entered into the keypad is shown on
the other device for confirmation. Out of Band uses some external communication
means to ensure that key material exchanged in-band belongs to the adressed
communication partner.

NFC is a perfect fit for an out-of-band communication channel for Bluetooth
device pairing. NFC communication only starts when two devices are in very close
proximity, literally touched to each other, but works without any discovery,
device selection or confirmation steps. NFC is comparatively slow and it is not
always convinient to keep proximity for a longer period of time. So Bluetooth is
also a perfect fit for NFC when larger or longer data transfers are requested.
From an NFC point of view this is :ref:`connection-handover` with Bluetooth
out-of-band data transmitted as an alternative carrier.

Connection Handover may be performed between two NFC Devices (negotiated
handover) or one NFC Device and another device that has an NFC Tag attached
(static handover). In negotiated handover, the NFC Device that wants to
establish an alternative connection sends a Connection Handover Request and
waits for a Connection Handover Select message. In static handover, the NFC
Device reads a Connection Handover Select message from the NFC Tag.




Bluetooth BR/EDR Out-of-Band Data
---------------------------------

.. table:: Bluetooth BR/EDR Secure Simple Pairing OOB Data

   +-------------------+------+--------------------------------------------------------+
   | Element           | Size | Description                                            |
   +===================+======+========================================================+
   | OOB Data Length   | 2    | Total length of OOB data including the Length field    |
   +-------------------+------+--------------------------------------------------------+
   | Bluetooth Address | 6    | The 48-bit Bluetooth Device Address (MAC Address)      |
   +-------------------+------+--------------------------------------------------------+
   | OOB Optional Data | N    | Additional OOB data as Extended Inquiry Response [#]_  |
   +-+-----------------+------+--------------------------------------------------------+
   | | EIR 0x02 or 0x03 --- Incomplete or Complete List of 16-bit Service Class UUIDs  |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x04 or 0x05 --- Incomplete or Complete List of 32-bit Service Class UUIDs  |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x06 or 0x07 --- Incomplete or Complete List of 128-bit Service Class UUIDs |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x08 or 0x09 --- Shortened or Complete Bluetooth Local Name                 |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x0D         --- Class of Device                                            |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x0E         --- Simple Pairing Hash C-192                                  |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x0F         --- Simple Pairing Randomizer R-192                            |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x1D         --- Simple Pairing Hash C-256                                  |
   +-+---------------------------------------------------------------------------------+
   | | EIR 0x1E         --- Simple Pairing Randomizer R-256                            |
   +-+---------------------------------------------------------------------------------+
   | | << Other EIR data types >>                                                      |
   +-+---------------------------------------------------------------------------------+

.. [#] Data elements within an Extended Inquiry Response are in no specific
       order. The order shown is only for illustration.

Bluetooth LE Out-of-Band Data
-----------------------------


.. table:: Bluetooth AD Types for OOB Pairing over NFC

   +--------------+--------------+-----------------------------------------------------+
   | AD Type      | Significance | Description                                         |
   +==============+==============+=====================================================+
   | 0x1B         | Mandatory    | LE Bluetooth Device Address                         |
   +--------------+--------------+-----------------------------------------------------+
   | 0x1C         | Mandatory    | LE Role                                             |
   +--------------+--------------+-----------------------------------------------------+
   | 0x10         | Optional     | Security Manager TK Value (LE legacy pairing)       |
   +--------------+--------------+-----------------------------------------------------+
   | 0x19         | Optional     | Appearance                                          |
   +--------------+--------------+-----------------------------------------------------+
   | 0x01         | Optional     | Flags                                               |
   +--------------+--------------+-----------------------------------------------------+
   | 0x08 or 0x09 | Optional     | Shortened or Complete Bluetooth Local Name          |
   +--------------+--------------+-----------------------------------------------------+
   | 0x22         | Optional     | LE Secure Connections Confirmation Value            |
   +--------------+--------------+-----------------------------------------------------+
   | 0x23         | Optional     | LE Secure Connections Random Value                  |
   +--------------+--------------+-----------------------------------------------------+
   | << Other AD types >>                                                              |
   +-----------------------------------------------------------------------------------+


NDEF Records
============

.. class:: ndef.bluetooth.BluetoothRecord

   A base class implementing dictionary-like EIR/AD data type access for the
   `BluetoothEasyPairingRecord` and the `BluetoothLowEnergyRecord`. It should
   not be used directly as an NDEF record type.

   Dictionary-like access works with either numeric or text keys. Numeric keys
   are defined in `Bluetooth Assigned Numbers`_ under Generic Access
   Profile. Recognized text keys are the data type names that are given by
   `attribute_names`.

   >>> import ndef
   >>> dict_like = ndef.bluetooth.BluetoothRecord()
   >>> dict_like[0x09] = b'Device Name'
   >>> dict_like.get('Complete Local Name')
   b'Device Name'
   >>> dict_like.get('Shortened Local Name', b'default name')
   b'default name'
   >>> [dict_like.get(name) for name in dict_like.attribute_names if name in dict_like]
   [b'Device Name']

   .. attribute:: attribute_names

      Returns all Bluetooth EIR/AD data type names that may be used as text
      keys. Note that 'Simple Pairing Hash C' and 'Simple Pairing Hash C-192' as
      well as 'Simple Pairing Randomizer R' and 'Simple Pairing Randomizer
      R-192' resolve to the same numeric key, respectively.

      >>> import ndef
      >>> print('\n'.join(sorted(ndef.bluetooth.BluetoothRecord().attribute_names)))
      Appearance
      Class of Device
      Complete List of 128-bit Service Class UUIDs
      Complete List of 16-bit Service Class UUIDs
      Complete List of 32-bit Service Class UUIDs
      Complete Local Name
      Flags
      Incomplete List of 128-bit Service Class UUIDs
      Incomplete List of 16-bit Service Class UUIDs
      Incomplete List of 32-bit Service Class UUIDs
      LE Bluetooth Device Address
      LE Role
      LE Secure Connections Confirmation Value
      LE Secure Connections Random Value
      Manufacturer Specific Data
      Security Manager Out of Band Flags
      Security Manager TK Value
      Shortened Local Name
      Simple Pairing Hash C
      Simple Pairing Hash C-192
      Simple Pairing Hash C-256
      Simple Pairing Randomizer R
      Simple Pairing Randomizer R-192
      Simple Pairing Randomizer R-256


Easy Pairing Record
-------------------

.. class:: BluetoothEasyPairingRecord(device_address, *eir)

   This class decodes and encodes Bluetooth BR/EDR Secure Simple Pairing
   Out-of-Band data and provides access to the embedded information.

   A `BluetoothEasyPairingRecord` must be initialized with at least the
   Bluetooth Device Address as the first argument. Any following arguments are
   expected to be key-value tuples where the key may be an EIR data type number
   or a recognized data type name and the value must be a `bytes` object with
   the corresponding data type octets (in little endian order for multi-byte
   values)..

   >>> import ndef
   >>> eir_list = [(0x0D, b'\x04\x01\x12'), ('Shortened Local Name', b'My Blue')]
   >>> record = ndef.BluetoothEasyPairingRecord('01:02:03:04:05:06', *eir_list)
   >>> record['Incomplete List of 16-bit Service Class UUIDs'] = b'\x0A\x11'
   >>> print(record)
   NDEF Bluetooth Easy Pairing Record ID '' Attributes 0x08 0x02 0x0D
   >>> octets = b''.join(ndef.message_encoder([record]))
   >>> print(list(ndef.message_decoder(octets))[0])
   NDEF Bluetooth Easy Pairing Record ID '' Attributes 0x08 0x02 0x0D

   .. attribute:: type

      The read-only Bluetooth Easy Pairing Record type.

      >>> record.type
      'application/vnd.bluetooth.ep.oob'

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

      >>> record.name = 'Easy Pairing Record'
      >>> record.name
      'Easy Pairing Record'

   .. attribute:: device_address

      The `~ndef.bluetooth.DeviceAddress` decoded from or to be encoded into the
      out-of-band BD_ADDR field.

      >>> record.device_address = '01:02:03:04:05:06'
      >>> record.device_address
      ndef.bluetooth.DeviceAddress('01:02:03:04:05:06', 'public')

   .. attribute:: device_name

      Get or set the Bluetooth Local Name.
      
      The Local Name, if configured on the Bluetooth device, is the name that
      may be displayed to the device user as part of the UI involving operations
      with Bluetooth devices. It may be encoded as either 'Complete Local name'
      or 'Shortened Local Name' EIR data type.

      This attribute provides the Local Name as a text string. The value
      returned is the 'Complete Local Name' or 'Shortened Local Name' evaluated
      in that order. None is returned if neither EIR data type exists.

      A device name assigned to this attribute is always stored as the 'Complete
      Local Name' and removes a 'Shortened Local Name' EIR data type if formerly
      present.

      >>> record['Shortened Local Name'] = b'shortened name'
      >>> record.device_name
      'shortened name'
      >>> record.device_name = "My \u2039BR/EDR\u203a Device"
      >>> record.device_name
      'My ‹BR/EDR› Device'
      >>> assert record.get('Shortened Local Name') is None
      >>> record['Complete Local Name']
      b'My \xe2\x80\xb9BR/EDR\xe2\x80\xba Device'

   .. attribute:: device_class

      Get or set the Bluetooth Class of Device information. Reading returns a
      `~ndef.bluetooth.DeviceClass` object. The attribute may be set to either a
      `~ndef.bluetooth.DeviceClass` object or the 24-bit Class of Device integer
      value. If the Bluetooth Class of Device EIR data type is not present when
      reading, the attribute is ``ndef.bluetooth.DeviceClass(0x000000)``.

      >>> record.device_class
      ndef.bluetooth.DeviceClass(0x120104)
      >>> ndef.bluetooth.DeviceClass.decode(record.get('Class of Device'))
      ndef.bluetooth.DeviceClass(0x120104)
      >>> record.device_class = 0x120104

   .. attribute:: service_class_list

      A read-only list of `~ndef.bluetooth.ServiceClass` instances build from
      all available Bluetooth Service Class UUID attributes (complete/incomplete
      and 16/32/128 bit EIR/AD types).

      >>> record.service_class_list
      [ndef.bluetooth.ServiceClass('0000110a-0000-1000-8000-00805f9b34fb')]

   .. method:: add_service_class(service_class, complete=False)

      Add a *service_class* identifier and set the resulting list of 16, 32 or
      128 bit Service Class UUIDs to either *complete* or incomplete. The
      *service_class* argument must be a `~ndef.bluetooth.ServiceClass` or an
      initializer thereof.

      >>> assert 'Incomplete List of 16-bit Service Class UUIDs' in record
      >>> assert 'Complete List of 16-bit Service Class UUIDs' not in record
      >>> record.add_service_class(0x110B, complete=True)
      >>> assert 'Incomplete List of 16-bit Service Class UUIDs' not in record
      >>> assert 'Complete List of 16-bit Service Class UUIDs' in record
      >>> [sc.name for sc in record.service_class_list]
      ['Audio Source', 'Audio Sink']

   .. attribute:: simple_pairing_hash_192

      Get or set the Simple Pairing Hash C-192.

      The Simple Pairing Hash C-192 is a commitment of the device's public key
      computed as HMAC-SHA-256 for the Curve-192 ECPK and Randomizer R-192. The
      Hash C should be generated anew for each pairing.

      This attribute returns either the 128-bit integer converted from the
      16-octet 'Simple Pairing Hash C-192' EIR value or None if the EIR data
      type is not present. When set, it stores a 128-bit integer as the 16-octet
      value of the 'Simple Pairing Hash C-192' EIR data type.

      >>> record.simple_pairing_hash_192 = 0x1234567890ABCDEF1234567890ABCDEF
      >>> record.get('Simple Pairing Hash C-192').hex()
      'efcdab9078563412efcdab9078563412'

   .. attribute:: simple_pairing_randomizer_192

      Get or set the Simple Pairing Randomizer R-192.

      If both devices transmit and receive data over NFC, then mutual
      authentication is based on the commitments of the public keys by Hash C
      exchanged out-of-band. If one device can only send information (typically
      an NFC Tag that is read by the other device), then authentication of the
      reading device will be based on that device knowing a random number R read
      from the NFC Tag. In this case, R must be secret: it can be created afresh
      every time (if the NFC Tag content can be modified by the host), or access
      to the device sending R must be restricted. Generally, if R is not sent by
      a device it is assumed to be 0 by the device receiving the out-of-band
      information.

      The Simple Pairing Randomizer R-192 is used with P192 Elliptic Curve
      Diffie Hellmann.

      This attribute returns either the 128-bit integer converted from the
      16-octet 'Simple Pairing Randomizer R-192' EIR value or None if the EIR
      data type is not present. When set, it stores a 128-bit integer as the
      16-octet value of the 'Simple Pairing Randomizer R-192' EIR data type.

      >>> record.simple_pairing_randomizer_192 = 0x010203040506070809000A0B0C0D0E0F
      >>> record.get('Simple Pairing Randomizer R-192').hex()
      '0f0e0d0c0b0a00090807060504030201'

   .. attribute:: simple_pairing_hash_256

      Get or set the Simple Pairing Hash C-256.

      The Simple Pairing Hash C-256 is a commitment of the device's public key
      computed as HMAC-SHA-256 for the Curve-256 ECPK and Randomizer R-256. The
      Hash C should be generated anew for each pairing.

      This attribute returns either the 128-bit integer converted from the
      16-octet 'Simple Pairing Hash C-256' EIR value or None if the EIR data
      type is not present. When set, it stores a 128-bit integer as the 16-octet
      value of the 'Simple Pairing Hash C-256' EIR data type.

      >>> record.simple_pairing_hash_256 = 0x1234567890ABCDEF1234567890ABCDEF
      >>> record.get('Simple Pairing Hash C-256').hex()
      'efcdab9078563412efcdab9078563412'

   .. attribute:: simple_pairing_randomizer_256

      Get or set the Simple Pairing Randomizer R-256.

      If both devices transmit and receive data over NFC, then mutual
      authentication is based on the commitments of the public keys by Hash C
      exchanged out-of-band. If one device can only send information (typically
      an NFC Tag that is read by the other device), then authentication of the
      reading device will be based on that device knowing a random number R read
      from the NFC Tag. In this case, R must be secret: it can be created afresh
      every time (if the NFC Tag content can be modified by the host), or access
      to the device sending R must be restricted. Generally, if R is not sent by
      a device it is assumed to be 0 by the device receiving the out-of-band
      information.

      The Simple Pairing Randomizer R-256 is used with P256 Elliptic Curve
      Diffie Hellmann.

      This attribute returns either the 128-bit integer converted from the
      16-octet 'Simple Pairing Randomizer R-256' EIR value or None if the EIR
      data type is not present. When set, it stores a 128-bit integer as the
      16-octet value of the 'Simple Pairing Randomizer R-256' EIR data type.

      >>> record.simple_pairing_randomizer_256 = 0x010203040506070809000A0B0C0D0E0F
      >>> record.get('Simple Pairing Randomizer R-256').hex()
      '0f0e0d0c0b0a00090807060504030201'


Low Energy Record
-----------------

.. class:: BluetoothLowEnergyRecord(device_address, *advertising_data)

   >>> import ndef
   >>> record = ndef.BluetoothLowEnergyRecord((0x08, b'My Blue'), (0x0D, b'100420'))
   >>> print(record)
   NDEF Bluetooth Low Energy Record ID '' Attributes 0x08 0x0D

   .. attribute:: type

      The read-only Bluetooth Low Energy Record type.

      >>> record.type
      'application/vnd.bluetooth.le.oob'

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

      >>> record.name = 'BLE Record'
      >>> record.name
      'BLE Record'

   .. attribute:: device_address

      Get or set the LE Bluetooth Device Address.

      The LE Bluetooth Device Address data value consists of 7 octets made up
      from the 48 bit address that is used for Bluetooth pairing over the LE
      transport and a flags octet that defines the address type. The address
      type distinguishes a Public Device Address versus a Random Device
      Address. A Random Device Address sent with BLE out-of-band data should be
      used on the LE transport for at least ten minutes after the NFC data
      exchange.

      This attribute returns a :class:`~ndef.bluetooth.DeviceAddress` or `None`,
      depending on whether the 'LE Bluetooth Device Address' AD type is present
      or not (under rare circumstances or just by failure it may not be). The
      *device_address* attribute may be set by assigning it another
      :class:`~ndef.bluetooth.DeviceAddress`, a tuple of address and address
      type strings, or a sole address string which implies a public address
      type.

      >>> record.device_address = '01:02:03:04:05:06'
      >>> record.device_address
      ndef.bluetooth.DeviceAddress('01:02:03:04:05:06', 'public')
      >>> record.device_address = ('01:02:03:04:05:06', 'random')
      >>> record.device_address
      ndef.bluetooth.DeviceAddress('01:02:03:04:05:06', 'random')

   .. attribute:: device_name

      Get or set the Bluetooth Local Device Name.

      The Local Name, if configured on the Bluetooth device, is the name that
      may be displayed to the device user as part of the UI involving operations
      with Bluetooth devices. It may be encoded as either 'Complete Local name'
      or 'Shortened Local Name' AD type.

      This attribute provides the Local Name as a text string. The value
      returned is the 'Complete Local Name' or 'Shortened Local Name' evaluated
      in that order. None is returned if neither AD type exists.

      A device name assigned to this attribute is always stored as the 'Complete
      Local Name' and removes a 'Shortened Local Name' AD type if formerly
      present.

      >>> record['Shortened Local Name'] = b'shortened name'
      >>> record.device_name
      'shortened name'
      >>> record.device_name = "My \u2039BLE\u203a Device"
      >>> record.device_name
      'My ‹BLE› Device'
      >>> assert record.get('Shortened Local Name') is None
      >>> record.get('Complete Local Name')
      b'My \xe2\x80\xb9BLE\xe2\x80\xba Device'

   .. attribute:: appearance

      Get or set the representation of the external appearance of the device,
      used by the discovering device to represent an icon, string, or similar to
      the user. The returned value is a tuple with the numeric value and a
      textual description, or None if the 'Appearance' AD type is not found. The
      appearance attribute accepts either a numeric value or a description
      string.

      Appearance strings consist of a generic category and an optional
      subtype. If a subtype is present it follows the generic category text
      after a colon.

      >>> record['Appearance'] = b'\x81\x03'
      >>> print(record.appearance)
      (897, 'Blood Pressure: Arm')
      >>> print("category '{0[0]}' subtype '{0[1]}'".format(record.appearance[1].split(': ')))
      category 'Blood Pressure' subtype 'Arm'
      >>> record.appearance = "Thermometer"
      >>> record['Appearance']
      b'\x00\x03'
      >>> record.appearance = 0x0280
      >>> print(record.appearance)
      (640, 'Media Player')

   .. attribute:: appearance_strings

      A list of all known appearance strings that may be assigned to
      :attr:`appearance`.

      >>> print('\n'.join(record.appearance_strings))
      Unknown
      Phone
      Computer
      Watch
      Watch: Sports Watch
      Clock
      Display
      Remote Control
      Eye-glasses
      Tag
      Keyring
      Media Player
      Barcode Scanner
      Thermometer
      Thermometer: Ear
      Heart Rate Sensor
      Heart Rate Sensor: Belt
      Blood Pressure
      Blood Pressure: Arm
      Blood Pressure: Wrist
      Human Interface Device
      Human Interface Device: Keyboard
      Human Interface Device: Mouse
      Human Interface Device: Joystick
      Human Interface Device: Gamepad
      Human Interface Device: Digitizer Tablet
      Human Interface Device: Card Reader
      Human Interface Device: Digital Pen
      Human Interface Device: Barcode Scanner
      Glucose Meter
      Running Walking Sensor
      Running Walking Sensor: In-Shoe
      Running Walking Sensor: On-Shoe
      Running Walking Sensor: On-Hip
      Cycling
      Cycling: Cycling Computer
      Cycling: Speed Sensor
      Cycling: Cadence Sensor
      Cycling: Power Sensor
      Cycling: Speed and Cadence Sensor
      Pulse Oximeter
      Pulse Oximeter: Fingertip
      Pulse Oximeter: Wrist Worn
      Weight Scale
      Outdoor Sports
      Outdoor Sports: Location Display Device
      Outdoor Sports: Location and Navigation Display Device
      Outdoor Sports: Location Pod
      Outdoor Sports: Location and Navigation Pod

   .. attribute:: role_capabilities

      Get or set the LE role capabilities of the device. The value is a string
      describing one of the four defined roles ``Peripheral``, ``Central``,
      ``Peripheral/Central`` (Peripheral Role preferred for connection
      establishment), or ``Central/Peripheral`` (Central is preferred for
      connection establishment).

      >>> record['LE Role'] = b'\x02'
      >>> print(record.role_capabilities)
      Peripheral/Central
      >>> record.role_capabilities = "Central"
      >>> assert record['LE Role'] == b'\x01'

   .. attribute:: flags

      Get or set the Flags bitmap.

      The 'Flags' AD type contains information on which discoverable mode to use
      and BR/EDR support and capability. The attribute returns the numerical
      flags value and descriptions for raised bits as an N-tuple. The attribute
      accepts either a numerical flags value or a tuple of description strings.

      >>> record['Flags'] = b'\x05'
      >>> print(record.flags)
      (5, 'LE Limited Discoverable Mode', 'BR/EDR Not Supported')
      >>> record.flags = ("LE General Discoverable Mode",)
      >>> record['Flags']
      b'\x02'
      >>> record.flags = 8
      >>> print(record.flags)
      (8, 'Simultaneous LE and BR/EDR to Same Device Capable (Controller)')

   .. attribute:: security_manager_tk_value
               
      Get or set the Security Manager TK Value.

      The Security Manager TK Value is used by the LE Security Manager in the
      OOB association model with LE Legacy pairing. Reading this attribute
      returns an unsigned integer converted from the 16 byte 'Security Manager
      TK Value' AD type octets, or None if the AD type is not found. An unsigned
      integer assigned to this attribute is written as the 16 byte 'Security
      Manager TK Value' AD type after conversion.

      >>> record.security_manager_tk_value = 0x1234567890ABCDEF1234567890ABCDEF
      >>> record.get('Security Manager TK Value').hex()
      'efcdab9078563412efcdab9078563412'
      >>> record.security_manager_tk_value
      24197857200151252728969465429440056815

   .. attribute:: secure_connections_confirmation_value

      Get or set the LE Secure Connections Confirmation Value.

      The LE Secure Connections Confirmation Value is used by the LE Security
      Manager if the OOB association model with LE Secure Connections pairing is
      used. Reading this attribute returns an unsigned integer converted from
      the 16 byte 'LE Secure Connections Confirmation Value' AD type octets, or
      None if the AD type is not found. An unsigned integer assigned to this
      attribute is written as the 16 byte 'LE Secure Connections Confirmation
      Value' AD type after conversion.

      >>> record.secure_connections_confirmation_value = 0x1234567890ABCDEF1234567890ABCDEF
      >>> record.get('LE Secure Connections Confirmation Value').hex()
      'efcdab9078563412efcdab9078563412'
      >>> record.secure_connections_confirmation_value
      24197857200151252728969465429440056815

   .. attribute:: secure_connections_random_value

      Get the LE Secure Connections Random Value.

      The LE Secure Connections Random Value is used by the LE Security Manager
      if the OOB association model with LE Secure Connections pairing is
      used. Reading this attribute returns an unsigned integer converted from
      the 16 byte 'LE Secure Connections Random Value' AD type octets, or None
      if the AD type is not found. An unsigned integer assigned to this
      attribute is written as the 16 byte 'LE Secure Connections Random Value'
      AD type after conversion.

      >>> record.secure_connections_random_value = 0x1234567890ABCDEF1234567890ABCDEF
      >>> record.get('LE Secure Connections Random Value').hex()
      'efcdab9078563412efcdab9078563412'
      >>> record.secure_connections_random_value
      24197857200151252728969465429440056815


Data Types
==========

Device Address
--------------

.. class:: ndef.bluetooth.DeviceAddress(address, address_type='public')

   Representation of a Bluetooth device address, either initialized with
   *address* and *address_type* or decoded from octets. The *address* argument
   for initialization is a MAC address string with colons or dashes as
   separators. The default *address_type* is 'public', for a Bluetooth LE
   address it may be set to 'random'. Note that this only makes a difference
   when encoding.

   >>> import ndef
   >>> print(ndef.bluetooth.DeviceAddress('01:02:03:04:05:06'))
   Device Address 01:02:03:04:05:06 (public)

   .. staticmethod:: decode(octets)

      Returns a `~ndef.bluetooth.DeviceAddress` instance constructed from either
      a BD_ADDR (6 octets) or 'LE Bluetooth Device Address' (7 octets).

      >>> ndef.bluetooth.DeviceAddress.decode(b'\x06\x05\x04\x03\x02\x01')
      ndef.bluetooth.DeviceAddress('01:02:03:04:05:06', 'public')
      >>> ndef.bluetooth.DeviceAddress.decode(b'\x06\x05\x04\x03\x02\x01\x01')
      ndef.bluetooth.DeviceAddress('01:02:03:04:05:06', 'random')

   .. method:: encode(context='LE')

      Returns the Bluetooth address as `bytes` in little endian order. The
      *context* argument determines the encoding format. For a Bluetooth LE
      address seven bytes are returned and the last byte discriminates between a
      public or random address. For BD_ADDR encoding the *context* must be 'EP'
      (for Easy Pairing).

      >>> ndef.bluetooth.DeviceAddress('01:02:03:04:05:06').encode('EP')
      b'\x06\x05\x04\x03\x02\x01'
      >>> ndef.bluetooth.DeviceAddress('01:02:03:04:05:06').encode('LE')
      b'\x06\x05\x04\x03\x02\x01\x00'

   .. attribute:: addr

      Get or set the Bluetooth Device Address. The address is a string in
      typical MAC address notation, both `:` and `-` are acceptable
      delimiters.

      >>> bdaddr = ndef.bluetooth.DeviceAddress('01:02:03:04:05:06')
      >>> bdaddr.addr
      '01:02:03:04:05:06'
      >>> bdaddr.addr = '06-05-04-03-02-01'
      >>> bdaddr.addr
      '06:05:04:03:02:01'

   .. attribute:: type

      Get or set the Bluetooth LE address type which may be either 'public' or
      'random'.

      >>> bdaddr = ndef.bluetooth.DeviceAddress('01:02:03:04:05:06', 'public')
      >>> bdaddr.type = 'random'
      >>> bdaddr
      ndef.bluetooth.DeviceAddress('01:02:03:04:05:06', 'random')


Device Class
------------

.. class:: ndef.bluetooth.DeviceClass(cod)

   Mapping of the Bluetooth 'Class of Device' information. An instance can be
   created with an integer argument that represents the 24 bits of the Class of
   Device structure, or by decoding a 3-byte sequence with the 24 bits in
   transmission order (little endian).

   >>> import ndef
   >>> print(ndef.bluetooth.DeviceClass(0x120104))
   Device Class Computer - Desktop workstation - Networking and Object Transfer

   .. staticmethod:: decode(octets)

      Returns a `~ndef.bluetooth.DeviceClass` instance with the 24 bits 'Class
      of Device' information decoded from *octets*. The *octets* argument must
      be a `bytes` or `bytearray` object of length 3 and in little endian order.

      >>> ndef.bluetooth.DeviceClass.decode(b'\x04\x01\x12')
      ndef.bluetooth.DeviceClass(0x120104)

   .. method:: encode()

      Returns 3 `bytes` with the 'Class of Device' integer in little endian
      order.

      >>> ndef.bluetooth.DeviceClass(0x120104).encode()
      b'\x04\x01\x12'

   .. attribute:: major_device_class

      The major device class string (read-only).

      >>> ndef.bluetooth.DeviceClass(0x120104).major_device_class
      'Computer'

   .. attribute:: minor_device_class

      The minor device class string (read-only).

      >>> ndef.bluetooth.DeviceClass(0x120104).minor_device_class
      'Desktop workstation'

   .. attribute:: major_service_class

      A tuple of major service class strings (read-only).

      >>> ndef.bluetooth.DeviceClass(0x120104).major_service_class
      ('Networking', 'Object Transfer')

Service Class
-------------

.. class:: ndef.bluetooth.ServiceClass(*args, **kwargs)

   The ServiceClass represents a single Bluetooth Service Class UUID. The first
   positional argument may be a Bluetooth 'uuid16' or 'uuid32' integer, a
   Bluetooth service class name, or any of the UUID string formats accepted by
   `uuid.UUID`. Alternatively, the same keyword arguments supported by
   `uuid.UUID` may be used.

   >>> import ndef
   >>> ndef.bluetooth.ServiceClass(0x110A)
   ndef.bluetooth.ServiceClass('0000110a-0000-1000-8000-00805f9b34fb')
   >>> ndef.bluetooth.ServiceClass("Audio Source")
   ndef.bluetooth.ServiceClass('0000110a-0000-1000-8000-00805f9b34fb')

   .. staticmethod:: decode(octets)

      Returns a `~ndef.bluetooth.ServiceClass` instance decoded from
      *octets*. The *octets* argument must be a `bytes` or `bytearray` object of
      either length 2, 4, or 16 in little endian order.

      >>> ndef.bluetooth.ServiceClass.decode(b'\x0A\x11')
      ndef.bluetooth.ServiceClass('0000110a-0000-1000-8000-00805f9b34fb')

   .. method:: encode()

      Return the `bytes` representation of the Service Class UUID in little
      endian order. The number of octets is 2 or 4 for a Bluetooth 'uuid16' or
      'uuid32' and 16 for any other UUID value.

      >>> ndef.bluetooth.ServiceClass(0x110A).encode()
      b'\n\x11'
      >>> ndef.bluetooth.ServiceClass(0x1000110A).encode()
      b'\n\x11\x00\x10'

   .. attribute:: uuid

      A `uuid.UUID` object that represents the Bluetooth Service Class UUID
      (read-only).

      >>> ndef.bluetooth.ServiceClass(0x110A).uuid
      UUID('0000110a-0000-1000-8000-00805f9b34fb')

   .. attribute:: name

      The Bluetooth Service Class UUID name (read-only). Depending on the UUID
      value this is either one of `names` or the UUID string representation.

      >>> ndef.bluetooth.ServiceClass(0x110A).name
      'Audio Source'
      >>> ndef.bluetooth.ServiceClass(0x1000110A).name
      '1000110a-0000-1000-8000-00805f9b34fb'

   .. staticmethod:: get_uuid_names()

      Returns a tuple of all known Bluetooth Service Class UUID names.

      >>> print('\n'.join(sorted(ndef.bluetooth.ServiceClass.get_uuid_names())))
      A/V Remote Control
      A/V Remote Control Controller
      A/V Remote Control Target
      Advanced Audio Distribution
      Audio Sink
      Audio Source
      Basic Imaging Profile
      Basic Printing
      Browse Group Descriptor
      Common ISDN Access
      Cordless Telephony
      Dialup Networking
      Direct Printing
      Direct Printing Reference
      ESDP UPNP IP LAP
      ESDP UPNP IP PAN
      ESDP UPNP L2CAP
      Fax
      GN
      GNSS
      GNSS Server
      Generic Audio
      Generic File Transfer
      Generic Networking
      Generic Telephony
      HCR Print
      HCR Scan
      HDP
      HDP Sink
      HDP Source
      Handsfree
      Handsfree Audio Gateway
      Hardcopy Cable Replacement
      Headset
      Headset - Audio Gateway (AG)
      Headset - HS
      Human Interface Device
      Imaging Automatic Archive
      Imaging Referenced Objects
      Imaging Responder
      Intercom
      IrMC Sync
      IrMC Sync Command
      LAN Access Using PPP
      Message Access Profile
      Message Access Server
      Message Notification Server
      NAP
      OBEX File Transfer
      OBEX Object Push
      PANU
      Phonebook Access
      Phonebook Access - PCE
      Phonebook Access - PSE
      PnP Information
      Printing Status
      Reference Printing
      Reflected UI
      SIM Access
      Serial Port
      Service Discovery Server
      UPNP IP Service
      UPNP Service
      Video Distribution
      Video Sink
      Video Source
      WAP
      WAP Client




