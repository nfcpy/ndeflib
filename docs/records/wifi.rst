.. -*- mode: rst; fill-column: 80 -*-

Wi-Fi Simple Configuration
==========================

.. versionadded:: 0.2

.. _Wi-Fi Alliance: http://www.wi-fi.org/
.. _Wi-Fi Protected Setup: http://www.wi-fi.org/discover-wi-fi/wi-fi-protected-setup
.. _Wi-Fi Direct: http://www.wi-fi.org/discover-wi-fi/wi-fi-direct
.. _intro: http://www.wi-fi.org/knowledge-center/faq/how-does-wi-fi-protected-setup-work
.. _Wi-Fi Alliance specifications: http://www.wi-fi.org/discover-wi-fi/specifications

The `Wi-Fi Alliance`_ developed the Wi-Fi Simple Configuration specification to
simplify the security setup and management of wireless networks. It is branded
as `Wi-Fi Protected Setup`_ and can be used in traditional infrastructure
networks as well as with `Wi-Fi Direct`_. One of the three Wi-Fi Protected Setup
methods uses NFC as an out-of-band channel to provision Wi-Fi devices with the
network credentials (see also this short `intro`_). All details can be learned
from the `Wi-Fi Alliance specifications`_.

The Wi-Fi Simple Configuration NFC out-of-band interface provides three usage
models for provisioning an *Enrollee*, a device seeking to join a WLAN domain,
with WLAN credentials. Devices with the authority to issue and revoke
credentials are termed *Registrar*. A Registrar may be integrated into an Access
Point.

*Password Token*

  A Password Token carries an Out-of-Band Device Password from an Enrollee to an
  NFC-enabled Registrar device. The device password is then used with the Wi-Fi
  in-band registration protocol to provision network credentials; an NFC
  Interface on the Enrollee is not required.

*Configuration Token*

  A Configuration Token carries unencrypted credential from an NFC-enabled
  Registrar to an NFC-enabled Enrollee device. A Configuration Token is created
  when the user touches the Registrar to retrieve the current network settings
  and allows subsequent configuration of one or more Enrollees.

*Connection Handover*

  Connection Handover is a protocol run between two NFC Peer Devices to
  establish an alternative carrier connection. The Connection Handover protocol
  is defined by the `NFC Forum`_. Together with Wi-Fi Simple Configuration it
  helps connect to a Wi-Fi Infrastructure Access Point or a Wi-Fi Direct Group
  Owner.


Password Token Format
---------------------

A Wi-Fi Password Token carries an NDEF Record with Payload Type
"application/vnd.wfa.wsc" that contains an Out-Of-Band Device Password from the
Enrollee. When presented to an NFC-enabled Registrar, typically an Access Point,
the Wi-Fi in-band registration protocol uses the device password from the
Password Token, instead of requiring the user to manually input a
password. Compared to manual input, a Password Token increases the effective
security strength of the registration protocol by allowing for longer passwords
and no need for key pad compatible characters.

The contents of a Wi-Fi Password Token are shown below. A parser must not
rely on any specific order of the attributes, the order shown is only
representational. Wi-Fi Attributes are encoded in the Wi-Fi Simple Configuration
TLV Data Format (a Type-Length-Value format with 16-bit Type and 16-bit Length
fields).

+-----------------------+----------------------------------------------------------+
| Attribute             | Required/Conditional/Optional \| Description             |
+=======================+===+======================================================+
| OOB Device Password   | R | A TLV with fixed data structure [#oob]_              |
+-+---------------------+---+------------------------------------------------------+
| | Public Key Hash     | R | The Enrollee’s public key hash  [#pkh]_              |
+-+---------------------+---+------------------------------------------------------+
| | Password ID         | R | A 16 bit identifier for the device password [#pid]_  |
+-+---------------------+---+------------------------------------------------------+
| | Device Password     | R | The zero or 16–32 octet long device password [#pwd]_ |
+-+---------------------+---+------------------------------------------------------+
| WFA Vendor Extension  | C | Vendor Extension with Vendor ID 00:37:2A [#wfa]_     |
+-+---------------------+---+------------------------------------------------------+
| | Version2            | C | Wi-Fi Simple Configuration version [#ver]_           |
+-+---------------------+---+------------------------------------------------------+
| | <other ...>         | O | Other WFA Vendor Extension subelements               |
+-+---------------------+---+------------------------------------------------------+
| <other ...>           | O | Other Wi-Fi Simple Configuration TLVs                |
+-----------------------+---+------------------------------------------------------+

.. [#oob] The Out-Of-Band Device Password is a fixed data structure with three
   fields. The public key hash is in the first 20 octets. The password id uses
   the next 2 octets. The remaining TLV Length minus 22 octets contain the
   device password. The device passowrd must be at least 16 and at most 32
   octets.

.. [#pkh] The Public Key Hash field contains the first 160 bits of the SHA-256
   hash of the Enrollee’s public key that will be transmitted with message M1 of
   the registration protocol.

.. [#pwd] The Device Password is zero length (absent) when used in negotiated
   connection handover between two Wi-Fi Peer To Peer devices, in which case the
   Password ID is equal to *NFC-Connection-Handover* (0x0007).
      
.. [#pid] The Password ID is an arbitrarily-selected number between 0x0010 and
   0xFFFF. During the in-band registration protocol the Registrar sends the
   Password ID back to the Enrollee to identify the device password that is
   being used.

.. [#wfa] The Wi-Fi Alliance Vendor Extension is a Vendor Extension Attribute
   with the first three octets (the Vendor ID) set to 00:37:2A (the Wi-Fi
   Alliance OUI). The remaining octets hold WFA Vendor Extension sub-elements in
   a Type-Length-Value format with 8-bit Type and 8-bit Length fields.

.. [#ver] The Version2 Attribute contains the Wi-Fi Simple Configuration version
   in a 1-octet field. The octet is split into the major version number in the
   most significant 4 bits and the minor version number in the least significant
   4 bits. The Attribute is encoded as a WFA Vendor Extension sub-element with
   ID 0x00 and Length 0x01.


Configuration Token Format
--------------------------

A Wi-Fi Configuration Token carries an NDEF Record with Payload Type
"application/vnd.wfa.wsc" that contains unencrypted credential(s) issued by an
NFC-enabled Registrar. An NFC-enabled Enrollee uses the credential(s) to
directly connect to the Wi-Fi network without the need to run the Wi-Fi Simple
Configuration registration protocol.

The contents of a Wi-Fi Configuration Token are shown below. A parser must not
rely on any specific order of the attributes, the order shown is only
representational. Wi-Fi Attributes are encoded in the Wi-Fi Simple Configuration
TLV Data Format (a Type-Length-Value format with 16-bit Type and 16-bit Length
fields).

+-----------------------+---+------------------------------------------------------+
| Attribute             | Required/Conditional/Optional \| Description             |
+=======================+===+======================================================+
| Credential            | R | A single WLAN credential [#cred]_                    |
+-+---------------------+---+------------------------------------------------------+
| | Network Index       | R | Deprecated – always set to 1.                        |
+-+---------------------+---+------------------------------------------------------+
| | SSID                | R | Network name (802.11 service set identifier).        |
+-+---------------------+---+------------------------------------------------------+
| | Authentication Type | R | Network authentication type.                         |
+-+---------------------+---+------------------------------------------------------+
| | Encryption Type     | R | Encryption capabilities.                             |
+-+---------------------+---+------------------------------------------------------+
| | Network Key         | R | Encryption Key.                                      |
+-+---------------------+---+------------------------------------------------------+
| | MAC Address         | R | Enrollee's or broadcast MAC address [#mac]_          |
+-+---------------------+---+------------------------------------------------------+
| | WFA Vendor Extension| O | Vendor Extension with WFA Vendor ID 00:37:2A         |
+-+-+-------------------+---+------------------------------------------------------+
| | | Key Sharable      | O | Whether the key may be shared with other devices     |
+-+-+-------------------+---+------------------------------------------------------+
| | | <other ...>       | O | Other WFA Vendor Extension subelements               |
+-+-+-------------------+---+------------------------------------------------------+
| | <other ...>         | O | Other Wi-Fi Simple Configuration TLVs                |
+-+---------------------+---+------------------------------------------------------+
| RF Bands              | O | Operating band of the AP or P2P group owner. [#ap]_  |
+-----------------------+---+------------------------------------------------------+
| RF Channel            | O | Operating channel of AP or P2P group owner. [#ap]_   |
+-----------------------+---+------------------------------------------------------+
| MAC Address           | O | The BSSID of the AP or Wi-Fi P2P group owner. [#ap]_ |
+-----------------------+---+------------------------------------------------------+
| WFA Vendor Extension  | C | Vendor Extension with Vendor ID 00:37:2A [#wfa]_     |
+-+---------------------+---+------------------------------------------------------+
| | Version2            | C | Wi-Fi Simple Configuration version [#ver]_           |
+-+---------------------+---+------------------------------------------------------+
| | <other ...>         | O | Other WFA Vendor Extension subelements               |
+-+---------------------+---+------------------------------------------------------+
| <other ...>           | O | Other Wi-Fi Simple Configuration TLVs                |
+-----------------------+---+------------------------------------------------------+

.. [#cred] The Credential is a compound attribute that contains other Wi-Fi
   Simple Configuration TLVs. A parser must not assume any specific order of the
   enclosed data elements.

.. [#mac] This should be the Enrollee's MAC address if the credential was
   specifically issued and will be valid only for the device with this MAC
   address. This can only be if the Registrar has prior knowledge of the
   Enrollee's MAC address and it's only effective if the AP is also able to
   restrict use of the credential to the provisioned device. In any other case
   the broadcast MAC address should be used.

.. [#ap] The optional RF Bands, AP Channel and MAC Address attributes may be
   included as hints to help the Station/Enrollee to find the AP without a full
   scan. It is recommended to include those attributes if known. If the RF Bands
   attribute and AP Channel attribute are both included then the RF Bands
   attribute indicates the band that the channel specified by the AP Channel
   attribute is in. If the RF Bands attribute is included without the AP Channel
   attribute then it indicates the RF Bands in which the AP is operating with
   the network name specified by the SSID attribute in the Credential.


Wi-Fi Simple Config Record
--------------------------

The `WifiSimpleConfigRecord` carries a number of Wi-Fi Type-Length-Value
Attributes that provide the information defined in the specification. Depending
on the information contained, it represents either a Password or a Configuration
Token. Each data element can be get or set as `bytes` with the numeric Attribute
ID (Type) as a key on the `WifiSimpleConfigRecord` instance. Additionally, any
of the `WifiSimpleConfigRecord.attribute_names` may also be used as a key.
Although often implicit, the Wi-Fi TLV structure allows no assumptions on the
cardinality of keys. Thus the `WifiSimpleConfigRecord` returns and expects key
values as lists.

>>> import ndef
>>> record = ndef.WifiSimpleConfigRecord()
>>> record[0x1020] = [b'\x00\x01\x02\x03\x04\x05']
>>> record[0x1020] == record['mac-address']
True
>>> record['mac-address'].append(b'\x05\x04\x03\x02\x01\x00')
>>> record['mac-address']
[b'\x00\x01\x02\x03\x04\x05', b'\x05\x04\x03\x02\x01\x00']


>>> import ndef
>>> import random
>>> import hashlib
>>> pkhash = hashlib.sha256(b'my public key goes here').digest()[0:20]
>>> pwd_id = random.randint(16, 65535)
>>> my_pwd = b"long password can't guess"
>>> oobpwd = ndef.wifi.OutOfBandPassword(pkhash, pwd_id, my_pwd)
>>> wfaext = ndef.wifi.WifiAllianceVendorExtension((0, b'\x20'))
>>> record = ndef.WifiSimpleConfigRecord()
>>> record['oob-password'] = [oobpwd.encode()]
>>> record['vendor-extension'] = [wfaext.encode()]
>>> #b''.join(ndef.message_encoder([record]))

Typically required Wi-Fi Attributes are available as data attributes with values
decoded from the first Wi-Fi Attribute Value for the associated Attribute Type.

>>> import ndef
>>> record = ndef.WifiSimpleConfigRecord()
>>> record[0x1020] = [b'\x00\x01\x02\x03\x04\x05']
>>> mac_address = record.get_attribute('mac-address')
>>> mac_address
ndef.wifi.MacAddress(b'\x00\x01\x02\x03\x04\x05')
>>> print(mac_address)
MAC Address 00:01:02:03:04:05
>>> record.set_attribute('ap-channel', 6)
>>> ap_channel = record.get_attribute('ap-channel')
>>> ap_channel
ndef.wifi.APChannel(6)
>>> ap_channel.value
6

.. class:: WifiSimpleConfigRecord(*args)

   The `WifiSimpleConfigRecord` can be initialized with any number of Wi-Fi
   Attribute Type and Value tuples. The same Attribute Type may also appear more
   than once.

   >>> import ndef
   >>> print(ndef.WifiSimpleConfigRecord((0x1001, b'\x00\x06'), ('ap-channel', b'\x00\x06')))
   NDEF Wifi Simple Config Record ID '' Attributes 0x1001 0x1001

   .. attribute:: type

      The Wifi Simple Config Record type is ``application/vnd.wfa.wsc``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: context

      Get the decoding or set the encoding context for the Wi-Fi Simple Config
      Record. The `str` context attribute determines whether the record is part
      of a connection ``handover`` exchange between two devices or belongs to a
      Wi-Fi Password or Configuration ``token``. This is unfortunately needed
      because the Wi-Fi Simple Configuration specification uses the same Payload
      Type for two different encoding formats.

   .. attribute:: attribute_names

      A read-only `list` of all Wi-Fi Simple Configuration Attribute names that
      can be used like keys on the record instance or as names for the
      get/set/add_attribute methods below.

      | 'ap-channel'
      | 'credential'
      | 'device-name'
      | 'mac-address'
      | 'manufacturer'
      | 'model-name'
      | 'model-number'
      | 'oob-password'
      | 'primary-device-type'
      | 'rf-bands'
      | 'secondary-device-type-list'
      | 'serial-number'
      | 'uuid-enrollee'
      | 'uuid-registrar'
      | 'vendor-extension'
      | 'version-1'

   .. method:: get_attribute(name, index=0)

      The `get_attribute` method returns a :ref:`attributes`


      >>> import ndef
      >>> record = ndef.wifi.WifiSimpleConfigRecord(('ap-channel', b'\x00\x06'))
      >>> print(record.get_attribute('ap-channel'))
      AP Channel 6
      >>> print(record.get_attribute('ap-channel', 1))
      None

   .. method:: set_attribute(name, *args)

      >>> import ndef
      >>> record = ndef.wifi.WifiSimpleConfigRecord(('ap-channel', b'\x00\x06'))
      >>> record.set_attribute('ap-channel', 10)
      >>> print(record.get_attribute('ap-channel'))
      AP Channel 10
      >>> print(record.get_attribute('ap-channel', 1))
      None

   .. method:: add_attribute(name, *args)

      >>> import ndef
      >>> record = ndef.wifi.WifiSimpleConfigRecord(('ap-channel', b'\x00\x06'))
      >>> record.add_attribute('ap-channel', 10)
      >>> print(record.get_attribute('ap-channel'))
      AP Channel 6
      >>> print(record.get_attribute('ap-channel', 1))
      AP Channel 10


.. _attributes:

Wi-Fi Attributes
----------------

This section lists the Wi-Fi Simple Configuration and P2P Attribute classes that
are available for decoding and encoding of Attribute Value octets.

>>> import ndef
>>> ndef.wifi.VendorExtension.decode(b'123456').value
(b'123', b'456')
>>> ndef.wifi.VendorExtension(b'123', b'456').encode()
b'123456'


AP Channel
~~~~~~~~~~

The AP Channel Attribute specifies the 802.11 channel that the AP is using.

.. class:: ndef.wifi.APChannel(value)

   The *value* argument is the `int` or decimal integer `str` channel number.

   >>> import ndef
   >>> assert ndef.wifi.APChannel(6) == ndef.wifi.APChannel("6")
   >>> ndef.wifi.APChannel(6).value
   6

   .. attribute:: value

      The read-only AP Channel `int` value.

Authentication Type
~~~~~~~~~~~~~~~~~~~

The Authentication Type Attribute contains the authentication type for the
Enrollee to use when associating with the network. For protocol version 2.0 or
newer, the value 0x0022 can be used to indicate mixed mode operation (both
WPA-Personal and WPA2-Personal enabled). All other values are required to have
only a single bit set to one in this attribute value.

====== =================== ===========================
Value  Authentication Type Notes
====== =================== ===========================
0x0001 Open
0x0002 WPA-Personal        deprecated in version 2.0
0x0004 Shared              deprecated in version 2.0
0x0008 WPA-Enterprise      deprecated in version 2.0
0x0010 WPA2-Enterprise     includes both CCMP and GCMP
0x0020 WPA2-Personal       includes both CCMP and GCMP
====== =================== ===========================

.. class:: ndef.wifi.AuthenticationType(*args)

   The *args* arguments may be a single `int` value with a bitwise OR of values
   from the authentication type table or one or more authentication type
   names. A type name can be used to test if the corresponding bit is set.

   >>> import ndef
   >>> mixed_mode = ndef.wifi.AuthenticationType('WPA-Personal', 'WPA2-Personal')
   >>> mixed_mode.value
   (34, 'WPA-Personal', 'WPA2-Personal')
   >>> "WPA2-Personal" in mixed_mode
   True

   .. attribute:: value

      A tuple with the authentication type value and corresponding names.

Configuration Methods
~~~~~~~~~~~~~~~~~~~~~

The Configuration Methods Attribute lists the configuration methods the Enrollee
or Registrar supports.

====== ==================== ================================================================
Value  Configuration Method Description
====== ==================== ================================================================
0x0001 USBA                 Deprecated
0x0002 Ethernet             Deprecated
0x0004 Label                8 digit static PIN typically available on device.
0x0008 Display              A dynamic 4 or 8 digit PIN is available from a display. [#v2cm]_
0x0010 External NFC Token   An NFC Tag transfers the configuration or device password.
0x0020 Integrated NFC Token The NFC Tag is integrated in the device.
0x0040 NFC Interface        The device contains an NFC interface.
0x0080 PushButton           The device contains a physical or virtual pushbutton. [#v2cm]_
0x0100 Keypad               Device is capable of entering a PIN
0x0280 Virtual Push Button  A virtual push button is avilable on a user interface.
0x0480 Physical Push Button A physical push button is available on the device.
0x2008 Virtual Display PIN  The PIN is displayed through a remote user interface.
0x4008 Physical Display PIN The PIN is shown on a display that is part of the device.
====== ==================== ================================================================

.. [#v2cm] Version 2.0 devices qualify a display as *Virtual Display PIN* or
   *Physical Display PIN* and a push button as *Virtual Push Button* or
   *Physical Push Button*.

.. class:: ndef.wifi.ConfigMethods(*args)

   The *args* arguments may be a single `int` value with a bitwise OR of values
   from the configuration method table or one or more method names. Any of the
   configuration method names can be tested for containment.

   >>> import ndef
   >>> config_methods = ndef.wifi.ConfigMethods("Label", "Display")
   >>> assert ndef.wifi.ConfigMethods(0x000C) == config_methods
   >>> "Label" in config_methods
   True
   >>> config_methods.value
   (12, 'Label', 'Display')

   .. attribute:: value

      A tuple with the configuration methods value and corresponding names.

Credential
~~~~~~~~~~

.. class:: ndef.wifi.Credential(*args)

   Credential is a compound Wi-Fi Attribute. It can be initialized with any
   number of Wi-Fi Attribute Type and Value tuples.

   >>> import ndef
   >>> credential = ndef.wifi.Credential(('ssid', b'my-ssid'), ('network-key', b'secret'))
   >>> print(credential)
   Credential Attributes 0x1045 0x1027
   >>> print(credential.get_attribute('ssid'))
   SSID 6D:79:2D:73:73:69:64

   .. attribute:: attribute_names

      A read-only `list` of all Wi-Fi Simple Configuration Attribute names that
      can be used as Credential keys.

      | 'authentication-type'
      | 'encryption-type'
      | 'key-provided-automatically'
      | 'mac-address'
      | 'network-key'
      | 'ssid'
      | 'vendor-extension'

   .. method:: get_attribute(name, index=0)

      >>> import ndef
      >>> credential = ndef.wifi.Credential(('mac-address', b'123456'))
      >>> print(credential.get_attribute('mac-address'))
      MAC Address 31:32:33:34:35:36
      >>> print(credential.get_attribute('mac-address', 1))
      None

   .. method:: set_attribute(name, *args)

      >>> import ndef
      >>> credential = ndef.wifi.Credential(('mac-address', b'123456'))
      >>> credential.set_attribute('mac-address', b'654321')
      >>> print(credential.get_attribute('mac-address'))
      MAC Address 36:35:34:33:32:31
      >>> print(credential.get_attribute('mac-address', 1))
      None

   .. method:: add_attribute(name, *args)

      >>> import ndef
      >>> credential = ndef.wifi.Credential(('mac-address', b'123456'))
      >>> credential.add_attribute('mac-address', b'654321')
      >>> print(credential.get_attribute('mac-address'))
      MAC Address 31:32:33:34:35:36
      >>> print(credential.get_attribute('mac-address', 1))
      MAC Address 36:35:34:33:32:31


Device Name
~~~~~~~~~~~

The Device Name Attribute contains a user-friendly description of the device
encoded in UTF-8. Typically, this is a unique identifier that describes the
product in a way that is recognizable to the user.

.. class:: ndef.wifi.DeviceName(device_name)

   The *device_name* argument is unicode string of up to 32 characters.

   .. attribute:: value

      The device name string.

Encryption Type
~~~~~~~~~~~~~~~

The Encryption Type Attribute contains the encryption type for the Enrollee to
use when associating with the network. For protocol version 2.0 or newer, the
value 0x000C can be used to indicate mixed mode operation (both WPA-Personal
with TKIP and WPA2-Personal with AES enabled). All other values are required to
have only a single bit set to one in this attribute value.

====== =============== ===========================
Value  Encryption Type Notes
====== =============== ===========================
0x0001 None
0x0002 WEP             Deprecated.
0x0004 TKIP            Deprecated. Use only for mixed mode.
0x0008 AES             Includes both CCMP and GCMP
====== =============== ===========================

.. class:: ndef.wifi.EncryptionType(*args)

   The arguments *args* may be a single `int` value with a bitwise OR of values
   from the encryption type table or one or more encryption type names. A name
   can be used to test if that encryption type is included.

   >>> import ndef
   >>> mixed_mode = ndef.wifi.EncryptionType('TKIP', 'AES')
   >>> assert ndef.wifi.EncryptionType(0x000C) == mixed_mode
   >>> "AES" in mixed_mode
   True
   >>> mixed_mode.value
   (12, 'TKIP', 'AES')

   .. attribute:: value

      A tuple with the encryption type value and corresponding names.

Key Provided Automatically
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Key Provided Automatically Attribute specifies whether the Network Key
is provided automatically by the network.

.. class:: ndef.wifi.KeyProvidedAutomatically(value)

   The *value* argument may be any type that can be converted into `bool`.

   >>> import ndef
   >>> ndef.wifi.KeyProvidedAutomatically(1).value
   True

   .. attribute:: value

      Either True or False.

MAC Address
~~~~~~~~~~~

The MAC Address Attribute contains the 48 bit value of the MAC Address.

.. class:: ndef.wifi.MacAddress(value)

   The *value* argument may be any type that can be converted to a `bytes`
   object with the six MAC Address octets.

   >>> import ndef
   >>> mac_address = ndef.wifi.MacAddress(b"\x01\x02\x03\x04\x05\x06")
   >>> assert ndef.wifi.MacAddress([1, 2, 3, 4, 5, 6]) == mac_address
   >>> mac_address.value
   b'\x01\x02\x03\x04\x05\x06'

   .. attribute:: value

      The six MAC Address bytes.

Manufacturer
~~~~~~~~~~~~

The Manufacturer Attribute is an ASCII string that identifies the manufacturer
of the device. Generally, this should allow a user to make an association with
the labeling on the device.

.. class:: ndef.wifi.Manufacturer(value)

   The *value* argument is a text `str` or `bytes` containing ASCII characters.

   >>> import ndef
   >>> ndef.wifi.Manufacturer("Company").value
   'Company'

   .. attribute:: value

      The Manufacturer name string.

Model Name
~~~~~~~~~~

The Model Name Attribute is an ASCII string that identifies the model of the
device. Generally, this field should allow a user to make an association with
the labeling on the device.

.. class:: ndef.wifi.ModelName(value)

   The *value* argument is a text `str` or `bytes` containing ASCII characters.

   >>> import ndef
   >>> ndef.wifi.ModelName("Product").value
   'Product'

   .. attribute:: value

      The Model Name string.

Model Number
~~~~~~~~~~~~

The Model Number Attribute provides additional description of the device to the
user.

.. class:: ndef.wifi.ModelNumber(value)

   The *value* argument is a text `str` or `bytes` containing ASCII characters.

   >>> import ndef
   >>> ndef.wifi.ModelNumber("007").value
   '007'

   .. attribute:: value

      The Model Number string.

Network Index
~~~~~~~~~~~~~

The Network Index Attribute is deprecated. Value 1 must be used for backwards
compatibility when the attribute is required.

.. class:: ndef.wifi.NetworkIndex(value)

   The *value* argument is the `int` network index number.

   >>> import ndef
   >>> ndef.wifi.NetworkIndex(1).value
   1

   .. attribute:: value

      The Network Index integer.

Network Key
~~~~~~~~~~~

The Network Key Attribute specifies the wireless encryption key to be used by
the Enrollee.

.. class:: ndef.wifi.NetworkKey(value)

   The *value* argument may be any type that can be converted to a `bytes`
   object with the 0 to 64 network key octets.

   >>> import ndef
   >>> ndef.wifi.NetworkKey(b"key").value
   b'key'

   .. attribute:: value

      The Network Key bytes.

Network Key Shareable
~~~~~~~~~~~~~~~~~~~~~

The Network Key Shareable Attribute is used within Credential Attributes. It
specifies whether the Network Key included in the Credential can be shared or
not with other devices. A True value indicates that the Network Key can be
shared.

.. class:: ndef.wifi.NetworkKeyShareable(value)

   The *value* argument may be any type that can be converted into `bool`.

   >>> import ndef
   >>> ndef.wifi.NetworkKeyShareable(True).value
   True

   .. attribute:: value

      Either True or False.

Out Of Band Device Password
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Out-of-Band Device Password Attribute contains a fixed data structure with
the overall size is given by the Wi-Fi Attribute TLV Length value.

=============== ====== =============================================       
Field            Size  Description
=============== ====== =============================================       
Public Key Hash    20  First 160 bits of the public key hash.
Password ID         2  16 bit identifier for the device password.
Device Password 16-32  Zero or 16–32 octet long device password.
=============== ====== =============================================       

The Password ID of an Out-of-Band Device Password must be between 0x0010 and
0xFFFF inclusively and chosen at random, except when NFC negotiated handover is
used in which case the Password ID is set to 0x0007.

The Device Password is (Length – 22) octets long, with a maximum size of 32
octets. A Device Password length of 32 byte is recommended if the out-of-band
channel has sufficient capacity. Otherwise, it can be any size with a minimum
length of 16 bytes, except when the Password ID is equal to 0x0007 (NFC
negotiated handover) in which case it has zero length.

For Enrollee provided Device Passwords, the Public Key Hash Data field
corresponds to the first 160 bits of a SHA-256 hash of the Enrollee’s public key
exchanged in message M1. For Registrar provided Device Passwords, the Public
Key Hash Data field corresponds to the first 160 bits of a SHA-256 hash of the
Registrar’s public key exchanged in message M2.

.. class:: ndef.wifi.OutOfBandPassword(public_key_hash, password_id, password)

   The *public_key_hash* attribute is a `bytes` object with the first 20 octets
   of the SHA-256 hash of the device's public key. The *password_id* argument is
   a 16-bit unsigned `int` value. The *password* is a `bytes` object with the
   either 0 or 16-32 octets long device password.

   >>> import ndef
   >>> import random
   >>> import hashlib
   >>> pubkey_hash = hashlib.sha256(b'my public key goes here').digest()[0:20]
   >>> password_id = random.randint(16, 65535)
   >>> my_password = b"my long password you can't guess"
   >>> oob = ndef.wifi.OutOfBandPassword(pubkey_hash, password_id, my_password)
   >>> assert oob.value == (pubkey_hash, password_id, my_password)
   >>> assert oob.public_key_hash == pubkey_hash
   >>> assert oob.password_id == password_id
   >>> assert oob.device_password == b"my long password you can't guess"

   .. attribute:: value

      The Out Of Band Password Attribute as the (public_key_hash, password_id,
      password).

   .. attribute:: public_key_hash

      The Public Key Hash bytes.

   .. attribute:: password_id

      The Password ID integer.

   .. attribute:: device_password

      The Device Password bytes.

Primary Device Type
~~~~~~~~~~~~~~~~~~~

The Primary Device Type Attribute contains the primary type of the device.

::
              
   "Computer::PC"
   "Computer::Server"
   "Computer::MediaCenter"
   "Computer::UltraMobile"
   "Computer::Notebook"
   "Computer::Desktop"
   "Computer::MobileInternetDevice"
   "Computer::Netbook"
   "Computer::Tablet"
   "Computer::Ultrabook"
   "Input::Keyboard"
   "Input::Mouse"
   "Input::Joystick"
   "Input::Trackball"
   "Input::GameController"
   "Input::Remote"
   "Input::Touchscreen"
   "Input::BiometricReader"
   "Input::BarcodeReader"
   "Printer::Scanner"
   "Printer::Fax"
   "Printer::Copier"
   "Printer::Multifunction"
   "Camera::DigitalStillCamera"
   "Camera::VideoCamera"
   "Camera::WebCamera"
   "Camera::SecurityCamera"
   "Storage::NAS"
   "Network::AccessPoint"
   "Network::Router"
   "Network::Switch"
   "Network::Gateway"
   "Network::Bridge"
   "Display::Television"
   "Display::PictureFrame"
   "Display::Projector"
   "Display::Monitor"
   "Multimedia::DigitalAudioRecorder"
   "Multimedia::PersonalVideoRecorder"
   "Multimedia::MediaCenterExtender"
   "Multimedia::SetTopBox"
   "Multimedia::ServerAdapterExtender"
   "Multimedia::PortableVideoPlayer"
   "Gaming::Xbox"
   "Gaming::Xbox360"
   "Gaming::Playstation"
   "Gaming::Console"
   "Gaming::Portable"
   "Telephone::WindowsMobile"
   "Telephone::SingleModePhone"
   "Telephone::DualModePhone"
   "Telephone::SingleModeSmartphone"
   "Telephone::DualModeSmartphone"
   "Audio::Receiver"
   "Audio::Speaker"
   "Audio::PortableMusicPlayer"
   "Audio::Headset"
   "Audio::Headphone"
   "Audio::Microphone"
   "Audio::HomeTheater"
   "Dock::Computer"
   "Dock::Media"

.. class:: ndef.wifi.PrimaryDeviceType(value)

   The *value* attribute may be either a 64-bit integer equivalent to the
   Attribute Value bytes in MSB order, or one of the text values above.

   >>> import ndef
   >>> device_type_1 = ndef.wifi.PrimaryDeviceType(0x00010050F2040001)
   >>> device_type_2 = ndef.wifi.PrimaryDeviceType("Computer::PC")
   >>> assert device_type_1 == device_type_2
   >>> device_type_1.value
   'Computer::PC'
   >>> ndef.wifi.PrimaryDeviceType(0x0001FFFFFF000001).value
   'Computer::FFFFFF000001'
   >>> ndef.wifi.PrimaryDeviceType(0xABCDFFFFFF000001).value
   'ABCD::FFFFFF000001'

   .. attribute:: value

      The Primary Device Type string.

RF Bands
~~~~~~~~

The RF Bands Attribute indicates a specific RF band that is utilized during
message exchange. As an optional attribute in NFC out-of-band provisioning it
indicates the RF Band relating to a channel or the RF Bands in which an AP is
operating with a particular SSID.

===== =======
Value RF Band
===== =======
0x01  2.4GHz
0x02  5.0GHz
0x03  60GHz
===== =======

.. class:: ndef.wifi.RFBands(*args)

   The arguments *args* may be a single `int` value with a bitwise OR of values
   from the RF bands table or one or more RF band names. A name can be used to
   test if that RF band is included.

   >>> import ndef
   >>> assert ndef.wifi.RFBands(0x03) == ndef.wifi.RFBands('2.4GHz', '5.0GHz')
   >>> "5.0GHz" in ndef.wifi.RFBands(0x03)
   True
   >>> ndef.wifi.RFBands(0x03).value
   (3, '2.4GHz', '5.0GHz')

   .. attribute:: value

      The tuple of RF Bands integer value and corresponding names.

Secondary Device Type List
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Secondary Device Type List contains one or more secondary device types
supported by the device. The standard values of Category and Sub Category are
the same as for the Primary Device Type Attribute.

.. class:: SecondaryDeviceTypeList(*args)

   One or more initialization arguments my be supplied as 64-bit integers or
   device type strings.

   >>> import ndef
   >>> ndef.wifi.SecondaryDeviceTypeList(0x00010050F2040002, 'Storage::NAS').value
   ('Computer::Server', 'Storage::NAS')

   .. attribute:: value

      A tuple of all device type strings.

Serial Number
~~~~~~~~~~~~~

The Serial Number Attribute contains the serial number of the device.

.. class:: ndef.wifi.SerialNumber(value)

   The *value* argument is a text `str` or `bytes` containing ASCII characters.

   >>> import ndef
   >>> ndef.wifi.SerialNumber("CB5A281NNP").value
   'CB5A281NNP'

   .. attribute:: value

      The Serial Number string.

SSID
~~~~

The SSID Attribute represents the Service Set Identifier a.k.a network
name. This is used by the client to identify the wireless network to connect
with. The SSID Attribute value must match exactly with the value of the SSID,
i.e. no zero padding and same length.

.. class:: ndef.wifi.SSID

   The *value* argument may be any type that can be converted to a `bytes`
   object with the SSID octets.

   >>> import ndef
   >>> ndef.wifi.SSID(b"my wireless network").value
   b'my wireless network'

   .. attribute:: value

      The SSID bytes.

UUID-E
~~~~~~

The UUID-E Attribute contains the universally unique identifier (UUID) generated
as a GUID by the Enrollee. It uniquely identifies an operational device and
should survive reboots and resets.

.. class:: ndef.wifi.UUIDEnrollee(value)

   The *value* argument may be either a `uuid.UUID` object, or the 16 `bytes` of
   a UUID, or any `str` value that can be used to initialize `uuid.UUID` object.

   >>> import ndef
   >>> ndef.wifi.UUIDEnrollee(bytes(range(16))).value
   '00010203-0405-0607-0809-0a0b0c0d0e0f'
   >>> ndef.wifi.UUIDEnrollee("00010203-0405-0607-0809-0a0b0c0d0e0f").value
   '00010203-0405-0607-0809-0a0b0c0d0e0f'

   .. attribute:: value

      The UUID-E string.

UUID-R
~~~~~~

The UUID-R Attribute contains the universally unique identifier (UUID) generated
as a GUID by the Registrar. It uniquely identifies an operational device and
should survive reboots and resets.

.. class:: ndef.wifi.UUIDRegistrar

   The *value* argument may be either a `uuid.UUID` object, or the 16 `bytes` of
   a UUID, or any `str` value that can be used to initialize `uuid.UUID` object.

   >>> import ndef
   >>> ndef.wifi.UUIDRegistrar(bytes(range(16))).value
   '00010203-0405-0607-0809-0a0b0c0d0e0f'
   >>> ndef.wifi.UUIDRegistrar('00010203-0405-0607-0809-0a0b0c0d0e0f').value
   '00010203-0405-0607-0809-0a0b0c0d0e0f'

   .. attribute:: value

      The UUID-E string.

Version
~~~~~~~

The Version Attribute is deprecated and always set to 0x10 (version 1.0) for
backwards compatibility. Version 1.0h of the specification did not fully
describe the version negotiation mechanism and version 2.0 introduced a new
subelement (Version2) for indicating the version number to avoid potential
interoperability issues with deployed 1.0h-based devices.

.. class:: ndef.wifi.Version1(*args)

   A single argument provides the version number as an 8-bit unsigned `int`. Two
   arguments provide the major and minor version numbers as 4-bi unsigned `int`.

   >>> import ndef
   >>> assert ndef.wifi.Version1(0x10) == ndef.wifi.Version1(1, 0)
   >>> ndef.wifi.Version1(1, 0).value
   Version(major=1, minor=0)

   .. attribute:: value

      The Version as a `~collections.namedtuple` with
      major and minor fields.

Version2
~~~~~~~~

The Version2 Attribute specifies the Wi-Fi Simple Configuration version
implemented by the device sending this attribute. It is a subelement within a
Wi-Fi Alliance Vendor Extension that was added in the specification version
2.0. If the Version2 Attribute is not included in a message it is assumed to use
version 1.0.

.. class:: ndef.wifi.Version2(*args)

   A single argument provides the version number as an 8-bit unsigned `int`. Two
   arguments provide the major and minor version numbers as 4-bit unsigned `int`.

   >>> import ndef
   >>> assert ndef.wifi.Version2(0x20) == ndef.wifi.Version2(2, 0)
   >>> ndef.wifi.Version1(2, 0).value
   Version(major=2, minor=0)

   .. attribute:: value

      The Version2 as a `~collections.namedtuple` with major and minor fields.

Vendor Extension
~~~~~~~~~~~~~~~~

The Vendor Extension Attribute allows vendor specific extensions in the Wi-Fi
Simple Configuration message formats. The Vendor Extension Value field contains
the Vendor ID followed by a maximum of 1021 octets Vendor Data. Vendor ID
is the SMI network management private enterprise code.

.. class:: ndef.wifi.VendorExtension(vendor_id, vendor_data)

   Both the *vendor_id* and *vendor_data* arguments are `bytes` that initalize
   the fields to encode. The *vendor_id* must be 3 octets while *vendor_data*
   may contain from 0 to 1021 octets.

   >>> import ndef
   >>> vendor_id, vendor_data = (b'\x00\x37\x2A', b'123')
   >>> ndef.wifi.VendorExtension(vendor_id, vendor_data).value == (vendor_id, vendor_data)
   True

   .. attribute:: value

      The read-only Vendor Extension Attribute as the `tuple` of (vendor_id,
      vendor_data).

Wi-Fi Alliance Vendor Extension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: ndef.wifi.WifiAllianceVendorExtension


Wi-Fi Peer To Peer Record
-------------------------

.. class:: WifiPeerToPeerRecord(*args)

   The WifiPeerToPeerRecord inherits from `WifiSimpleConfigRecord` and shares
   the same Attribute access mechanism. Wi-Fi P2P Attribute numeric keys are all
   less than 256 (thus distinct from Wi-Fi Simple Config Attribute numeric keys
   that are all greater than 4095).

Wi-Fi Peer To Peer Attributes
-----------------------------

