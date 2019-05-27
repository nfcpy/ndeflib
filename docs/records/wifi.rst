.. -*- mode: rst; fill-column: 80 -*-

##########################
Wi-Fi Simple Configuration
##########################

.. versionadded:: 0.2

Overview
========

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

`Password Token`_

  A Password Token carries an Out-of-Band Device Password from an Enrollee to an
  NFC-enabled Registrar device. The device password is then used with the Wi-Fi
  in-band registration protocol to provision network credentials; an NFC
  Interface on the Enrollee is not required.

`Configuration Token`_

  A Configuration Token carries unencrypted credential from an NFC-enabled
  Registrar to an NFC-enabled Enrollee device. A Configuration Token is created
  when the user touches the Registrar to retrieve the current network settings
  and allows subsequent configuration of one or more Enrollees.

`Connection Handover`_

  Connection Handover is a protocol run between two NFC Peer Devices to
  establish an alternative carrier connection. The Connection Handover protocol
  is defined by the `NFC Forum`_. Together with Wi-Fi Simple Configuration it
  helps connect to a Wi-Fi Infrastructure Access Point or a Wi-Fi Direct Group
  Owner.


Password Token
--------------

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

**Example**

>>> import ndef
>>> import random
>>> import hashlib
>>> pkhash = hashlib.sha256(b'my public key goes here').digest()[0:20]
>>> pwd_id = random.randint(16, 65535)
>>> my_pwd = b"long password can't guess"
>>> oobpwd = ndef.wifi.OutOfBandPassword(pkhash, pwd_id, my_pwd)
>>> wfaext = ndef.wifi.WifiAllianceVendorExtension((0, b'\x20'))
>>> record = ndef.WifiSimpleConfigRecord()
>>> record.name = 'my password token'
>>> record['oob-password'] = [oobpwd.encode()]
>>> record['vendor-extension'] = [wfaext.encode()]
>>> print(record)
NDEF Wifi Simple Config Record ID 'my password token' Attributes 0x102C 0x1049
>>> octets = b''.join(ndef.message_encoder([record]))
>>> len(octets)
105

Configuration Token
-------------------

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

**Example**

>>> import ndef
>>> credential = ndef.wifi.Credential()
>>> credential.set_attribute('network-index', 1)
>>> credential.set_attribute('ssid', b'my network name')
>>> credential.set_attribute('authentication-type', 'WPA2-Personal')
>>> credential.set_attribute('encryption-type', 'AES')
>>> credential.set_attribute('network-key', b'my secret password')
>>> credential.set_attribute('mac-address', b'\xFF\xFF\xFF\xFF\xFF\xFF')
>>> wfa_ext = ndef.wifi.WifiAllianceVendorExtension()
>>> wfa_ext.set_attribute('network-key-shareable', 1)
>>> credential['vendor-extension'] = [wfa_ext.encode()]
>>> print(credential)
Credential Attributes 0x1003 0x100F 0x1020 0x1026 0x1027 0x1045 0x1049
>>> record = ndef.wifi.WifiSimpleConfigRecord()
>>> record.name = 'my config token'
>>> record.set_attribute('credential', credential)
>>> record.set_attribute('rf-bands', ('2.4GHz', '5.0GHz'))
>>> wfa_ext = ndef.wifi.WifiAllianceVendorExtension()
>>> wfa_ext.set_attribute('version-2', 0x20)
>>> record['vendor-extension'] = [wfa_ext.encode()]
>>> print(record)
NDEF Wifi Simple Config Record ID 'my config token' Attributes 0x100E 0x103C 0x1049
>>> octets = b''.join(ndef.message_encoder([record]))
>>> len(octets)
139

Connection Handover
-------------------

Two NFC Devices in close proximity establish NFC communication based on the NFC
Forum Logical Link Control Protocol (LLCP) specification. If one of the devices
has intention to activate a further communication method, it can then use the
NFC Forum Connection Handover protocol to announce possible communication means
(potentially including configuration data) and request the other device to
respond with a selection of matching technologies, including necessary
configuration data.

An Enrollee NFC Device that has established NFC LLCP communication with a
Registrar NFC Device sends a Connection Handover Request Message indicating
Wi-Fi communication capability. A Registrar NFC Device responds with a
Connection Handover Select Message indicating the Wi-Fi carrier which the
Enrollee should associate with. The Enrollee is then provisioned by the
Registrar through in-band WSC protocol message exchange (with encrypted
ConfigData from the Registrar included in M2).

The following table shows the format of the Wi-Fi Carrier Configuration Record
as transmitted within a Connection Handover Request Message. The UUID-E
attribute is included to assist with the discovery over 802.11 that follows the
exchange of the connection handover messages.

+-----------------------+----------------------------------------------------------+
| Attribute             | Required/Conditional/Optional \| Description             |
+=======================+===+======================================================+
| OOB Device Password   | R | A TLV with fixed data structure [#oob]_              |
+-+---------------------+---+------------------------------------------------------+
| | Public Key Hash     | R | The Enrollee’s public key hash  [#pkh]_              |
+-+---------------------+---+------------------------------------------------------+
| | Password ID         | R | Set to NFC-Connection-Handover (0x0007)              |
+-+---------------------+---+------------------------------------------------------+
| UUID-E                | R | Universally Unique Identifier of the Enrollee Device |
+-----------------------+---+------------------------------------------------------+
| WFA Vendor Extension  | R | Vendor Extension with Vendor ID 00:37:2A [#wfa]_     |
+-+---------------------+---+------------------------------------------------------+
| | Version2            | R | Wi-Fi Simple Configuration version [#ver]_           |
+-+---------------------+---+------------------------------------------------------+
| | <other ...>         | O | Other WFA Vendor Extension subelements               |
+-+---------------------+---+------------------------------------------------------+
| <other ...>           | O | Other Wi-Fi Simple Configuration TLVs                |
+-----------------------+---+------------------------------------------------------+

**Example:**

>>> import ndef
>>> import random
>>> import hashlib
>>> pkhash = hashlib.sha256(b'enrollee public key').digest()[0:20]
>>> oobpwd = ndef.wifi.OutOfBandPassword(pkhash, 0x0007, b'')
>>> wfaext = ndef.wifi.WifiAllianceVendorExtension(('version-2', b'\x20'))
>>> carrier = ndef.WifiSimpleConfigRecord()
>>> carrier.name = '0'
>>> carrier.set_attribute('oob-password', oobpwd)
>>> carrier.set_attribute('uuid-enrollee', '00010203-0405-0607-0809-0a0b0c0d0e0f')
>>> carrier['vendor-extension'] = [wfaext.encode()]
>>> print(carrier)
NDEF Wifi Simple Config Record ID '0' Attributes 0x102C 0x1047 0x1049
>>> hr = ndef.handover.HandoverRequestRecord('1.3', random.randint(0, 0xffff))
>>> hr.add_alternative_carrier('active', carrier.name)
>>> octets = b''.join(ndef.message_encoder([hr, carrier]))
>>> len(octets)
108

The Wi-Fi Carrier Configuration Record transmitted within a Connection Handover
Select Message from Registrar to Enrollee is shown below. The SSID attribute is
included to assist with the discovery over 802.11 that follows the exchange of
the connection handover messages. Optionally the RF Bands attribute, the AP
Channel attribute and the MAC Address attribute may be included as hints to help
the Enrollee find the AP without a full scan.

+-----------------------+----------------------------------------------------------+
| Attribute             | Required/Conditional/Optional \| Description             |
+=======================+===+======================================================+
| OOB Device Password   | R | A TLV with fixed data structure [#oob]_              |
+-+---------------------+---+------------------------------------------------------+
| | Public Key Hash     | R | The Registrar’s public key hash  [#pkh]_             |
+-+---------------------+---+------------------------------------------------------+
| | Password ID         | R | Set to NFC-Connection-Handover (0x0007)              |
+-+---------------------+---+------------------------------------------------------+
| SSID                  | R | Service Set Identifier of the network to connect     |
+-----------------------+---+------------------------------------------------------+
| RF Bands              | O | Provides the operating RF band of the AP             |
+-----------------------+---+------------------------------------------------------+
| AP Channel            | O | Provides the operating channel of the AP             |
+-----------------------+---+------------------------------------------------------+
| MAC Address           | O | Basic Service Set Identifier of the AP               |
+-----------------------+---+------------------------------------------------------+
| WFA Vendor Extension  | R | Vendor Extension with Vendor ID 00:37:2A [#wfa]_     |
+-+---------------------+---+------------------------------------------------------+
| | Version2            | R | Wi-Fi Simple Configuration version [#ver]_           |
+-+---------------------+---+------------------------------------------------------+
| | <other ...>         | O | Other WFA Vendor Extension subelements               |
+-+---------------------+---+------------------------------------------------------+
| <other ...>           | O | Other Wi-Fi Simple Configuration TLVs                |
+-----------------------+---+------------------------------------------------------+

**Example:**

>>> import ndef
>>> import hashlib
>>> pkhash = hashlib.sha256(b'registrar public key').digest()[0:20]
>>> oobpwd = ndef.wifi.OutOfBandPassword(pkhash, 0x0007, b'')
>>> wfaext = ndef.wifi.WifiAllianceVendorExtension(('version-2', b'\x20'))
>>> carrier = ndef.WifiSimpleConfigRecord()
>>> carrier.name = '0'
>>> carrier.set_attribute('oob-password', oobpwd)
>>> carrier.set_attribute('ssid', b'802.11 network')
>>> carrier.set_attribute('rf-bands', '2.4GHz')
>>> carrier.set_attribute('ap-channel', 6)
>>> carrier.set_attribute('mac-address', b'\1\2\3\4\5\6')
>>> carrier['vendor-extension'] = [wfaext.encode()]
>>> print(carrier)
NDEF Wifi Simple Config Record ID '0' Attributes 0x1001 0x1020 0x102C 0x103C 0x1045 0x1049
>>> hs = ndef.handover.HandoverSelectRecord('1.3')
>>> hs.add_alternative_carrier('active', carrier.name)
>>> octets = b''.join(ndef.message_encoder([hs, carrier]))
>>> len(octets)
120

NDEF Record Classes
===================

Wi-Fi Simple Config Record
--------------------------

A `WifiSimpleConfigRecord` holds any number of Wi-Fi TLV (Type-Length-Value)
Attributes which are defined in the Wi-Fi Simple Configuration specification. It
is organized as a `dict` with numeric Attribute ID or symbolic
`~WifiSimpleConfigRecord.attribute_names` keys. Values are returned and must be
set as a `list` of `bytes`, where each `bytes` object corresponds to one
instance of the Wi-Fi TLV Attribute.

>>> import ndef
>>> record = ndef.WifiSimpleConfigRecord()
>>> record[0x1020] = [b'\x00\x01\x02\x03\x04\x05']
>>> assert record[0x1020] == record['mac-address']
>>> record['mac-address'].append(b'\x05\x04\x03\x02\x01\x00')
>>> record['mac-address']
[b'\x00\x01\x02\x03\x04\x05', b'\x05\x04\x03\x02\x01\x00']

The `~WifiSimpleConfigRecord.get_attribute`,
`~WifiSimpleConfigRecord.set_attribute` and
`~WifiSimpleConfigRecord.add_attribute` methods can be used to get or set values
using :ref:`wsc_attributes`.

.. class:: WifiSimpleConfigRecord(*args)

   The `WifiSimpleConfigRecord` is initialized with any number of Wi-Fi Simple
   Config Attribute Type and Value tuples. The same Attribute Type may appear
   more than once.

   >>> import ndef
   >>> print(ndef.WifiSimpleConfigRecord((0x1001, b'\x00\x06'), ('ap-channel', b'\x00\x06')))
   NDEF Wifi Simple Config Record ID '' Attributes 0x1001 0x1001

   .. attribute:: type

      The read-only Wifi Simple Configuration Record type.

      >>> ndef.wifi.WifiSimpleConfigRecord().type
      'application/vnd.wfa.wsc'

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

      >>> record = ndef.wifi.WifiSimpleConfigRecord()
      >>> record.name = 'WSC Record'
      >>> record.name
      'WSC Record'

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attribute data.

      >>> record = ndef.wifi.WifiSimpleConfigRecord()
      >>> record.data
      b''
      >>> record['ap-channel'] = [b'\x00\x06']
      >>> record.data
      b'\x10\x01\x00\x02\x00\x06'

   .. attribute:: attribute_names

      The read-only `list` of all WSC Attribute names that can be used as keys
      on the record instance or as names for the get/set/add_attribute methods.

      >>> print('\n'.join(sorted(ndef.wifi.WifiSimpleConfigRecord().attribute_names)))
      ap-channel
      credential
      device-name
      mac-address
      manufacturer
      model-name
      model-number
      oob-password
      primary-device-type
      rf-bands
      secondary-device-type-list
      serial-number
      ssid
      uuid-enrollee
      uuid-registrar
      vendor-extension
      version-1

   .. method:: get_attribute(name, index=0)

      The `get_attribute` method returns the Wi-Fi Attribute selected by *name*
      and *index*.

      >>> record = ndef.WifiSimpleConfigRecord(('ap-channel', b'\x00\x06'))
      >>> print(record.get_attribute('ap-channel', 0))
      AP Channel 6
      >>> print(record.get_attribute('ap-channel', 1))
      None

   .. method:: set_attribute(name, *args)

      The `set_attribute` method sets the Wi-Fi Attribute *name* to a single
      instance constructed from *args*.

      >>> record = ndef.WifiSimpleConfigRecord(('ap-channel', b'\x00\x06'))
      >>> record.set_attribute('ap-channel', 10)
      >>> print(record.get_attribute('ap-channel', 0))
      AP Channel 10
      >>> print(record.get_attribute('ap-channel', 1))
      None

   .. method:: add_attribute(name, *args)

      The `add_attribute` method adds a Wi-Fi Attribute *name* constructed from
      *args* to any existing Wi-Fi Attributes of *name*. If there are no
      existing attributes for *name* the result is the same as for
      `set_attribute`.

      >>> record = ndef.WifiSimpleConfigRecord(('ap-channel', b'\x00\x06'))
      >>> record.add_attribute('ap-channel', 12)
      >>> print(record.get_attribute('ap-channel', 0))
      AP Channel 6
      >>> print(record.get_attribute('ap-channel', 1))
      AP Channel 12


Wi-Fi Peer To Peer Record
-------------------------

.. class:: WifiPeerToPeerRecord(*args)

   The `WifiPeerToPeerRecord` inherits from `WifiSimpleConfigRecord` and adds
   handling of Wi-Fi P2P Attributes.

   >>> import ndef
   >>> print(ndef.WifiPeerToPeerRecord(('negotiation-channel', b'de\x04\x51\x06\x01')))
   NDEF Wifi Peer To Peer Record ID '' Attributes 0x13

   .. attribute:: type

      The read-only Wifi Peer To Peer Record type.

      >>> ndef.wifi.WifiPeerToPeerRecord().type
      'application/vnd.wfa.p2p'

   .. attribute:: attribute_names

      The read-only `list` of all WSC and P2P Attribute names that may be used
      as keys on the record instance or as names for the get/set/add_attribute
      methods.

      >>> print('\n'.join(sorted(ndef.wifi.WifiPeerToPeerRecord().attribute_names)))
      ap-channel
      channel-list
      credential
      device-name
      mac-address
      manufacturer
      model-name
      model-number
      negotiation-channel
      oob-password
      p2p-capability
      p2p-device-info
      p2p-group-id
      p2p-group-info
      primary-device-type
      rf-bands
      secondary-device-type-list
      serial-number
      ssid
      uuid-enrollee
      uuid-registrar
      vendor-extension
      version-1


.. _wsc_attributes:

WSC Attribute Classes
=====================

This section documents the Wi-Fi Simple Configuration (WSC) Attribute classes.

AP Channel
----------

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
-------------------

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
---------------------

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
----------

.. class:: ndef.wifi.Credential(*args)

   Credential is a compound Wi-Fi Attribute. It can be initialized with any
   number of Wi-Fi Attribute Type and Value tuples.

   >>> import ndef
   >>> credential = ndef.wifi.Credential(('ssid', b'my-ssid'), ('network-key', b'secret'))
   >>> print(credential)
   Credential Attributes 0x1027 0x1045
   >>> print(credential.get_attribute('ssid'))
   SSID 6D:79:2D:73:73:69:64

   .. attribute:: attribute_names

      A read-only `list` of all Wi-Fi Simple Configuration Attribute names that
      can be used as Credential keys.

      >>> print('\n'.join(sorted(ndef.wifi.Credential().attribute_names)))
      authentication-type
      encryption-type
      key-provided-automatically
      mac-address
      network-index
      network-key
      ssid
      vendor-extension

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
-----------

The Device Name Attribute contains a user-friendly description of the device
encoded in UTF-8. Typically, this is a unique identifier that describes the
product in a way that is recognizable to the user.

.. class:: ndef.wifi.DeviceName(device_name)

   The *device_name* argument is unicode string of up to 32 characters.

   .. attribute:: value

      The device name string.

Encryption Type
---------------

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
--------------------------

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
-----------

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
------------

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
----------

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
------------

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
-------------

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
-----------

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
---------------------

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
---------------------------

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
-------------------

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
--------

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
--------------------------

The Secondary Device Type List contains one or more secondary device types
supported by the device. The standard values of Category and Sub Category are
the same as for the `Primary Device Type`_ Attribute.

.. class:: SecondaryDeviceTypeList(*args)

   One or more initialization arguments my be supplied as 64-bit integers or
   device type strings.

   >>> import ndef
   >>> ndef.wifi.SecondaryDeviceTypeList(0x00010050F2040002, 'Storage::NAS').value
   ('Computer::Server', 'Storage::NAS')

   .. attribute:: value

      A tuple of all device type strings.

Serial Number
-------------

The Serial Number Attribute contains the serial number of the device.

.. class:: ndef.wifi.SerialNumber(value)

   The *value* argument is a text `str` or `bytes` containing ASCII characters.

   >>> import ndef
   >>> ndef.wifi.SerialNumber("CB5A281NNP").value
   'CB5A281NNP'

   .. attribute:: value

      The Serial Number string.

SSID
----

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
------

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
------

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
-------

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
--------

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
----------------

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
-------------------------------

The Wi-Fi Alliance (WFA) Vendor Extension is a Vendor Extension attribute (ID
0x1049) that uses Vendor ID 0x00372A and contains one or more subelements. The
WFA Vendor Extension attribute is used to encode new information in a way that
avoids some backwards compatibility issues with deployed implementations that
are based on previous specification versions, but do not comply with
requirements to ignore new attributes.

.. class:: ndef.wifi.WifiAllianceVendorExtension

   The `~ndef.wifi.WifiAllianceVendorExtension` is an attribute container class
   that holds other Wi-Fi Simple Configuration attributes. It may be initialzed
   with any number of WFA sublement type-value tuples.

   >>> import ndef
   >>> wfa_ext = ndef.wifi.WifiAllianceVendorExtension(('version-2', b'\x20'))
   >>> wfa_ext[0x02] = [b'\x01'] # network key shareable
   >>> print(wfa_ext)
   WFA Vendor Extension Attributes 0x00 0x02

   .. attribute:: attribute_names

      The read-only list of all WSC attribute names (subelements) that may be
      used as a key or name for the get/set/add_attribute methods.

      >>> print('\n'.join(sorted(ndef.wifi.WifiAllianceVendorExtension().attribute_names)))
      network-key-shareable
      version-2

   .. attribute:: get_attribute(name, index=0)

      The `get_attribute` method returns the WFA subelement attribute selected
      by name and index.

      >>> wfa_ext = ndef.wifi.WifiAllianceVendorExtension(('version-2', b'\x20'))
      >>> wfa_ext.get_attribute('version-2')
      ndef.wifi.Version2(2, 0)

   .. method:: set_attribute(name, *args)

      The `set_attribute` method sets the WFA subelement attribute *name* to a
      single instance constructed from *args*.

      >>> wfa_ext = ndef.wifi.WifiAllianceVendorExtension(('version-2', b'\x20'))
      >>> wfa_ext.set_attribute('version-2', 0x21)
      >>> wfa_ext.get_attribute('version-2')
      ndef.wifi.Version2(2, 1)

   .. method:: add_attribute(name, *args)

      The `add_attribute` method adds a WFA subelement attribute *name*
      constructed from *args* to any existing *name* attributes. If there are no
      existing *name* attributes it is effectively the same as `set_attribute`.

      >>> wfa_ext = ndef.wifi.WifiAllianceVendorExtension()
      >>> wfa_ext.add_attribute('version-2', ndef.wifi.Version2(2, 0))
      >>> wfa_ext.add_attribute('version-2', ndef.wifi.Version2(2, 1))
      >>> wfa_ext.get_attribute('version-2', 0)
      ndef.wifi.Version2(2, 0)
      >>> wfa_ext.get_attribute('version-2', 1)
      ndef.wifi.Version2(2, 1)


.. _p2p_attributes:

P2P Attribute Classes
=====================

This section documents the Wi-Fi Peer To Peer (P2P) Attribute classes.

P2P Capability
--------------

The P2P Capability attribute contains a set of parameters that indicate the P2P
Device's capability and the current state of the P2P Group.

Device Capability Strings::

   'Service Discovery'
   'P2P Client Discoverability'
   'Concurrent Operation'
   'P2P Infastructure Managed'
   'P2P Device Limit'
   'P2P Invitation Procedure'
   'Reserved Bit 6'
   'Reserved Bit 7'

Group Capability Strings::

  'P2P Group Owner'
  'Persistent P2P Group'
  'P2P Group Limit'
  'Intra-BSS Distribution'
  'Cross Connection'
  'Persistent Reconnect'
  'Group Formation'
  'IP Address Allocation'

.. class:: ndef.wifi.PeerToPeerCapability(device_capability, group_capability)

   Both init arguments *device_capability* and *group_capability* may be set as
   either 8-bit integer values with each bit position corresponding to an
   individual capability, or as a list of capability strings.

   >>> import ndef
   >>> attr_1 = ndef.wifi.PeerToPeerCapability(0b00000001, 0b01000000)
   >>> attr_2 = ndef.wifi.PeerToPeerCapability(['Service Discovery'], ['Group Formation'])
   >>> assert attr_1 == attr_2
   >>> ndef.wifi.PeerToPeerCapability(3, 65).device_capability
   (3, 'Service Discovery', 'P2P Client Discoverability')

   .. attribute:: device_capability

      The P2P Device Capabilities as a tuple with the first element the
      numerical value of the device capability bitmap and following elements are
      capability strings. This attribute is read-only.

      >>> import ndef
      >>> ndef.wifi.PeerToPeerCapability(3, 0).device_capability
      (3, 'Service Discovery', 'P2P Client Discoverability')

   .. attribute:: group_capability

      The P2P Group Capabilities as a tuple with the first element the numerical
      value of the group capability bitmap and following elements are capability
      strings. This attribute is read-only.

      >>> import ndef
      >>> ndef.wifi.PeerToPeerCapability(0, 65).group_capability
      (65, 'P2P Group Owner', 'Group Formation')

Channel List
------------

The Channel List attribute contains a list of Operating Class and Channel pair
information.

.. class:: ndef.wifi.ChannelList(country_string, *channel_entry)

   The *country_string* argument determines the country code for the
   *channel_entry* argument(s). Each *channel_entry* is a tuple of an
   *operating_class* integer and a *channel_numbers* list.

   >>> import ndef
   >>> channel_list = ndef.wifi.ChannelList(b"de\x04", (81, (1, 6)), (115, (36, 44)))
   >>> print(channel_list)
   Channel List Country DE Table E-4 Class 81 Channels [1, 6], Class 115 Channels [36, 44]
   >>> len(channel_list)
   2
   >>> print(channel_list[0])
   Class 81 Channels [1, 6]
   >>> channel_list[0].operating_class
   81
   >>> channel_list[0].channel_numbers
   (1, 6)

   .. attribute:: country_string

      The Country String field is the value contained in the dot11CountryString
      attribute, specifying the country code in which the Channel Entry List is
      valid. The third octet of the Country String field is always set to hex 04
      to indicate that Table E-4 is used.

      >>> import ndef
      >>> ndef.wifi.ChannelList(b"de\x04", (81, (1,))).country_string
      b'de\x04'

P2P Device Info
---------------

The P2P Device Info attribute provides the P2P Device Address, Config Methods,
Primary Device Type, a list of Secondary Device Types and the user friendly Device
Name.

.. class:: ndef.wifi.PeerToPeerDeviceInfo(adr, cfg, pdt, sdtl, name)

   The first argument *adr* must be the 6 bytes P2P Device Address. The *cfg*
   argument is a tuple of `Configuration Methods`_ strings. The *pdt* argument
   specifies the `Primary Device Type`_ of the P2P Device as a single text
   string. The `Secondary Device Type List`_ *sdtl* argument expects a tuple of
   device type strings. The `Device Name`_ *name* argument provides the friendly
   name of the P2P Device. All arguments must be supplied.

   >>> import ndef
   >>> adr = b'\x01\x02\x03\x04\x05\x06'
   >>> cfg = ('Label', 'Display')
   >>> pdt = 'Computer::Tablet'
   >>> sdtl = ('Computer::PC', )
   >>> name = 'my tablet'
   >>> info = ndef.wifi.PeerToPeerDeviceInfo(adr, cfg, pdt, sdtl, name)
   >>> print(info)
   P2P Device Info 01:02:03:04:05:06 0x000C ['Label', 'Display'] Computer::Tablet Computer::PC 'my tablet'

   .. attribute:: device_address

      The P2P Device Identifier used to uniquely reference a P2P Device returned
      as a 6 byte string. The `device_address` attribute is read-only.

      >>> info.device_address
      b'\x01\x02\x03\x04\x05\x06'

   .. attribute:: config_methods

      The `Configuration Methods`_ that are supported by this device e.g. PIN
      from a Keypad, PBC etc. The values are returned as a tuple where the first
      entry is the config methods bitmap and remaining entries are method
      strings. The `config_methods` attribute is read-only.

      >>> info.config_methods
      (12, 'Label', 'Display')

   .. attribute:: primary_device_type

      The Primary Device Type of the P2P Device returned as a string. See
      `Primary Device Type`_ for representation of pre-defined and custom
      values. The `primary_device_type` attribute is read-only.

      >>> info.primary_device_type
      'Computer::Tablet'

   .. attribute:: secondary_device_type_list

      A list of Secondary Device Types of the P2P Client. Returns a, potentially
      empty, tuple of device type strings. The `secondary_device_type_list`
      attribute is read-only.

      >>> info.secondary_device_type_list
      ('Computer::PC',)

   .. attribute:: device_name

      The friendly name of the P2P Device which should be the same as the WSC
      `Device Name`_. The `device_name` attribute is read-only.

      >>> info.device_name
      'my tablet'

P2P Group Info
--------------

The P2P Group Info attribute contains device information of P2P Clients that
are members of the P2P Group.

.. class:: ndef.wifi.PeerToPeerGroupInfo(*client_info)

   A `PeerToPeerGroupInfo` object holds a number of client info descriptors. It
   is initialized with a number of client info data tuples as shown below.

   >>> import ndef
   >>> client_info_1 = (
   ...     b'\x01\x02\x03\x04\x05\x06',  # P2P Device Address
   ...     b'\x11\x12\x13\x14\x15\x16',  # P2P Interface Address
   ...     ('Service Discovery',),       # Device Capabilities
   ...     ('NFC Interface',),           # Configuration Methods
   ...     "Computer::Tablet",           # Primary Device Type
   ...     (),                           # Secondary Device Types
   ...     'first device',               # Device name
   ... )
   >>> client_info_2 = (
   ...     b'\x21\x22\x23\x24\x25\x26',  # P2P Device Address
   ...     b'\x31\x32\x33\x34\x35\x36',  # P2P Interface Address
   ...     ('Service Discovery',),       # Device Capabilities
   ...     ('NFC Interface',),           # Configuration Methods
   ...     "Computer::Tablet",           # Primary Device Type
   ...     (),                           # Secondary Device Types
   ...     'second device',              # Device name
   ... )
   >>> group_info = ndef.wifi.PeerToPeerGroupInfo(client_info_1, client_info_2)
   >>> print(group_info)
   P2P Group Info (Device 1: 01:02:03:04:05:06 11:12:13:14:15:16 Capability ['Service Discovery'] Config 0x0040 ['NFC Interface'] Type 'Computer::Tablet ' Name 'first device'), (Device 2: 21:22:23:24:25:26 31:32:33:34:35:36 Capability ['Service Discovery'] Config 0x0040 ['NFC Interface'] Type 'Computer::Tablet ' Name 'second device')
   >>> [client_info.device_name for client_info in group_info]
   ['first device', 'second device']
   >>> type(group_info[0])
   <class 'ndef.wifi.PeerToPeerGroupInfo.Descriptor'>

   .. class:: ndef.wifi.PeerToPeerGroupInfo.Descriptor

      P2P Client Info within a `PeerToPeerGroupInfo` is exposed as a
      `Descriptor` instance with attributes for the relevant information fields.

      >>> descriptor = group_info[0]

      .. attribute:: device_address

         The 6 byte P2P Device Identifier used to uniquely reference a P2P
         Device. The `device_address` attribute is read-only.

         >>> descriptor.device_address
         b'\x01\x02\x03\x04\x05\x06'

      .. attribute:: interface_address

         The 6 byte P2P Interface Address is used to identify a P2P Device
         within a P2P Group.  The `interface_address` attribute is read-only.

         >>> descriptor.interface_address
         b'\x11\x12\x13\x14\x15\x16'

      .. attribute:: config_methods

         The `Configuration Methods`_ that are supported by this device e.g. PIN
         from a Keypad, PBC etc. The values are returned as a tuple where the
         first entry is the config methods bitmap and remaining entries are
         method strings. The `config_methods` attribute is read-only.

         >>> descriptor.config_methods
         (64, 'NFC Interface')

      .. attribute:: primary_device_type

         The Primary Device Type of the P2P Device returned as a string. See
         `Primary Device Type`_ for representation of pre-defined and custom
         values. The `primary_device_type` attribute is read-only.

         >>> descriptor.primary_device_type
         'Computer::Tablet'

      .. attribute:: secondary_device_type_list

         A list of Secondary Device Types of the P2P Client. Returns a,
         potentially empty, tuple of device type strings. The
         `secondary_device_type_list` attribute is read-only.

         >>> descriptor.secondary_device_type_list
         ()

      .. attribute:: device_name

         The friendly name of the P2P Device which should be the same as the WSC
         `Device Name`_. The `device_name` attribute is read-only.

         >>> descriptor.device_name
         'first device'

P2P Group ID
------------

The P2P Group ID attribute contains a unique P2P Group identifier of the P2P
Group.

.. class:: ndef.wifi.PeerToPeerGroupID(device_address, ssid)

   Both the *device_address* and *ssid* arguments must be given as byte strings
   and the *device_address* must be exactly 6 byte long.

   >>> import ndef
   >>> attr = ndef.wifi.PeerToPeerGroupID(b'\1\2\3\4\5\6', b'P2P Group SSID')
   >>> print(attr)
   P2P Group ID 01:02:03:04:05:06 SSID 50:32:50:20:47:72:6F:75:70:20:53:53:49:44

   .. attribute:: device_address

      The 6 byte P2P Device Identifier used to uniquely reference a P2P
      Device. The `device_address` attribute is read-only.

      >>> attr.device_address
      b'\x01\x02\x03\x04\x05\x06'

   .. attribute:: ssid

      The service set identifier (a.k.a. network name) as a byte
      string. Although often printable it is in fact just a sequence of bytes
      with no implied text encoding. The `ssid` attribute is read-only.

      >>> attr.ssid
      b'P2P Group SSID'

Negotiation Channel
-------------------

The Out-of-Band Group Owner Negotiation Channel attribute contains the Channel
and Class information used for the Group Owner Negotiation.

.. class:: ndef.wifi.NegotiationChannel(country_string, operating_class, channel_number, role_indication)

   The *country_string* argument specifies the country code and operating class
   table (always value 0x04) in 3 bytes. The *operating_class* and
   *channel_number* must be 8-bit integer values. The *role_indication* argument
   must be either ``'Not Member'``, ``'Group Client'``, or ``'Group Owner'``.

   >>> import ndef
   >>> attr = ndef.wifi.NegotiationChannel(b'de\x04', 81, 6, 'Group Client')
   >>> print(attr)
   Negotiation Channel Country DE Table E-4 Class 81 Channel 6 Role 'Group Client'

   .. attribute:: country_string

      The Country String specifies the country code in which the Group Formation
      Class and Channel Number fields are valid. The third octet of the Country
      String is set to hex 04 to indicate that Table E-4 is used. The
      `country_string` attribute is read-only.

      >>> attr.country_string
      b'de\x04'

   .. attribute:: operating_class

      Provides the preferred Operating Class for the Group Owner Negotiation. An
      Operating Class value 0 indicates that no preferred Operating Class is
      available. If set to 0, the Operating Class information provided in the
      Channel List attribute shall be used.

      >>> attr.operating_class
      81

   .. attribute:: channel_number

      Provides the preferred channel for the Group Formation. A Channel Number
      value 0 indicates that no group formation preferred channel is available
      and P2P Group Owner negotiation with a full channel search based on the
      information provided in the Channel List attribute shall be used.

      >>> attr.channel_number
      6

   .. attribute:: role_indication

      Indicates the current role of the P2P device. It reads as a 2-tuple where
      the first value is the numerical and the second value the textual
      representation. The `role_indication` attribute is read-only.

      >>> attr.role_indication
      (1, 'Group Client')


