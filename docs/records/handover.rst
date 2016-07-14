.. -*- mode: rst; fill-column: 80 -*-

Connection Handover
===================

The `NFC Forum`_ Connection Handover specification defines a number of Record
structures that are used to exchange messages between Handover Requester,
Selector and Mediator devices to eventually establish alternative carrier
connections for additional data exchange.  Generally, a requester device sends a
Handover Request Message to announce supported alternative carriers and expects
the selector device to return a Handover Select Message with a selection of
alternative carriers supported by both devices. If the two devices are not close
enough for NFC communication, a third device may use the Handover Mediation and
Handover Initiate Messages to relay information between the two.

Any of above mentioned Handover Messages is constructed as an NDEF Message where
the first record associates the processing context. The Handover Request,
Select, Mediation, and Initiate Record classes implement the appropriate
context, i.e. record types known by context are decoded by associated record
type classes while others are decoded as generic NDEF Records.

Handover Request Record
-----------------------

The Handover Request Record is the first record of a connection handover request
message. Information enclosed within the payload of a handover request record
includes the handover version number, a random number for resolving a handover
request collision (when both peer devices simultaenously send a handover request
message) and a number of references to alternative carrier information records
subsequently encoded in the same message.

>>> import ndef
>>> from os import urandom
>>> wsc = 'application/vnd.wfa.wsc'
>>> message = [ndef.HandoverRequestRecord('1.3', urandom(2))]
>>> message.append(ndef.HandoverCarrierRecord(wsc, None, 'wifi'))
>>> message[0].add_alternative_carrier('active', message[1].name)

.. class:: HandoverRequestRecord(version='1.3', crn=None, *alternative_carrier)

   Initialize the record with a *version* number, a collision resolution random
   number *crn* and zero or more *alternative_carrier*. The version number can
   be set as an 8-bit integer (with 4-bit major and minor part), or as a
   ``'{major}.{minor}'`` version string. An alternative carrier is given by a
   tuple with *carrier power state*, *carrier data reference* and zero or more
   *auxiliary data references*. The collision resolution number (crn) argument
   is the unsigned 16-bit random integer for connection handover version '1.2'
   or later, for any prior version number it must be None.

   :param version: handover version number
   :type version: int or str
   :param int crn: collision resolution random number
   :param tuple alternative_carrier: alternative carrier entry

   .. attribute:: type

      The Handover Request Record type is ``urn:nfc:wkt:Hr``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: hexversion

      The version as an 8-bit integer with 4-bit major and minor part. This is a
      read-only attribute.

   .. attribute:: version_info

      The version as a named tuple with major and minor version number
      attributes. This is a read-only attribute.

   .. attribute:: version_string

      The version as the '{major}.{minor}' formatted string. This is a read-only
      attribute.

   .. attribute:: collision_resolution_number

      Get or set the random number for handover request message collision
      resolution. May be None if the random number was neither decoded or set.

   .. attribute:: alternative_carriers

      A `list` of alternative carriers with attributes carrier_power_state,
      carrier_data_reference, and auxiliary_data_reference list.


   .. method:: add_alternative_carrier(cps, cdr, *adr):

      Add a reference to a carrier data record within the handover request
      message. The carrier data reference *cdr* is the name (NDEF Record ID) of
      the carrier data record. The carrier power state *cps* is either
      'inactive', 'active', 'activating', or 'unknown'. Any number of auxiliary
      data references *adr* may be added to link with other records in the
      message that carry information related to the carrier.


Handover Select Record
----------------------

The Handover Select Record is the first record of a connection handover select
message. Information enclosed within the payload of a handover select record
includes the handover version number, error reason and associated error data
when processing of the previously received handover request message failed, and
a number of references to alternative carrier information records subsequently
encoded in the same message.

>>> import ndef
>>> carrier = ndef.Record('mimetype/subtype', 'ref', b'1234')
>>> message = [ndef.HandoverSelectRecord('1.3'), carrier]
>>> message[0].add_alternative_carrier('active', carrier.name)

.. class:: HandoverSelectRecord(version='1.3', error=None, *alternative_carrier)

   Initialize the record with a *version* number, an *error* information tuple,
   and zero or more *alternative_carrier*. The version number can be either an
   8-bit integer (4-bit major, 4-bit minor), or a ``'{major}.{minor}'`` version
   string. An alternative carrier is given by a tuple with *carrier power
   state*, *carrier data reference* and zero or more *auxiliary data
   references*. The *error* argument is a tuple with error reason and error
   data. Error information, if not None, is encoded as the local Error Record
   after all given alternative carriers.
           
   :param version: handover version number
   :type version: int or str
   :param tuple error: error reason and data
   :param tuple alternative_carrier: alternative carrier entry

   .. attribute:: type

      The Handover Select Record type is ``urn:nfc:wkt:Hs``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: hexversion

      The version as an 8-bit integer with 4-bit major and minor part. This is a
      read-only attribute.

   .. attribute:: version_info

      The version as a named tuple with major and minor version number
      attributes. This is a read-only attribute.

   .. attribute:: version_string

      The version as the '{major}.{minor}' formatted string. This is a read-only
      attribute.

   .. attribute:: error

      Either error information or None. Error details can be accessed with
      ``error.error_reason`` and ``error.error_data``. Formatted error
      information is provided with ``error.error_reason_string``.

   .. method:: set_error(error_reason, error_data):

      Set error information. The *error_reason* argument is an 8-bit integer
      value but only values 1, 2 and 3 are defined in the specification. For
      defined error reasons the *error_data* argument is the associated value
      (which is a number in all cases). For undefined error reason values the
      *error_data* argument is `bytes`. Error reason value 0 is strictly
      reserved and never encoded or decoded.

   .. attribute:: alternative_carriers

      A `list` of alternative carriers with attributes carrier_power_state,
      carrier_data_reference, and auxiliary_data_reference list.


   .. method:: add_alternative_carrier(cps, cdr, *adr):

      Add a reference to a carrier data record within the handover select
      message. The carrier data reference *cdr* is the name (NDEF Record ID) of
      the carrier data record. The carrier power state *cps* is either
      'inactive', 'active', 'activating', or 'unknown'. Any number of auxiliary
      data references *adr* may be added to link with other records in the
      message that carry information related to the carrier.


Handover Mediation Record
-------------------------

The Handover Mediation Record is the first record of a connection handover
mediation message. Information enclosed within the payload of a handover
mediation record includes the version number and zero or more references to
alternative carrier information records subsequently encoded in the same
message.

>>> import ndef
>>> carrier = ndef.Record('mimetype/subtype', 'ref', b'1234')
>>> message = [ndef.HandoverMediationRecord('1.3'), carrier]
>>> message[0].add_alternative_carrier('active', carrier.name)

.. class:: HandoverMediationRecord(version='1.3', *alternative_carrier)

   Initialize the record with *version* number and zero or more
   *alternative_carrier*.  The version number can be either an 8-bit integer
   (4-bit major, 4-bit minor), or a ``'{major}.{minor}'`` version string. An
   alternative carrier is given by a tuple with *carrier power state*, *carrier
   data reference* and zero or more *auxiliary data references*.
           
   :param version: handover version number
   :type version: int or str
   :param tuple alternative_carrier: alternative carrier entry

   .. attribute:: type

      The Handover Select Record type is ``urn:nfc:wkt:Hm``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: hexversion

      The version as an 8-bit integer with 4-bit major and minor part. This is a
      read-only attribute.

   .. attribute:: version_info

      The version as a named tuple with major and minor version number
      attributes. This is a read-only attribute.

   .. attribute:: version_string

      The version as the '{major}.{minor}' formatted string. This is a read-only
      attribute.

   .. attribute:: alternative_carriers

      A `list` of alternative carriers with attributes carrier_power_state,
      carrier_data_reference, and auxiliary_data_reference list.


   .. method:: add_alternative_carrier(cps, cdr, *adr):

      Add a reference to a carrier data record within the handover mediation
      message. The carrier data reference *cdr* is the name (NDEF Record ID) of
      the carrier data record. The carrier power state *cps* is either
      'inactive', 'active', 'activating', or 'unknown'. Any number of auxiliary
      data references *adr* may be added to link with other records in the
      message that carry information related to the carrier.


Handover Initiate Record
------------------------

The Handover Initiate Record is the first record of a connection handover initiate
message. Information enclosed within the payload of a handover initiate record
includes the version number and zero or more references to alternative carrier
information records subsequently encoded in the same message.

>>> import ndef
>>> carrier = ndef.Record('mimetype/subtype', 'ref', b'1234')
>>> message = [ndef.HandoverInitiateRecord('1.3'), carrier]
>>> message[0].add_alternative_carrier('active', carrier.name)

.. class:: HandoverInitiateRecord(version='1.3', *alternative_carrier)

   Initialize the record with *version* number and zero or more
   *alternative_carrier*.  The version number can be either an 8-bit integer
   (4-bit major, 4-bit minor), or a ``'{major}.{minor}'`` version string. An
   alternative carrier is given by a tuple with *carrier power state*, *carrier
   data reference* and zero or more *auxiliary data references*.
           
   :param version: handover version number
   :type version: int or str
   :param tuple alternative_carrier: alternative carrier entry

   .. attribute:: type

      The Handover Select Record type is ``urn:nfc:wkt:Hi``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: hexversion

      The version as an 8-bit integer with 4-bit major and minor part. This is a
      read-only attribute.

   .. attribute:: version_info

      The version as a named tuple with major and minor version number
      attributes. This is a read-only attribute.

   .. attribute:: version_string

      The version as the '{major}.{minor}' formatted string. This is a read-only
      attribute.

   .. attribute:: alternative_carriers

      A `list` of alternative carriers with attributes carrier_power_state,
      carrier_data_reference, and auxiliary_data_reference list.


   .. method:: add_alternative_carrier(cps, cdr, *adr):

      Add a reference to a carrier data record within the handover initiate
      message. The carrier data reference *cdr* is the name (NDEF Record ID) of
      the carrier data record. The carrier power state *cps* is either
      'inactive', 'active', 'activating', or 'unknown'. Any number of auxiliary
      data references *adr* may be added to link with other records in the
      message that carry information related to the carrier.


Handover Carrier Record
-----------------------

The Handover Carrier Record allows a unique identification of an alternative
carrier technology in a handover request message when no carrier configuration
data is to be provided. If the handover selector device has the same carrier
technology available, it would respond with a carrier configuration record with
payload type equal to the carrier type (that is, the triples (TNF, TYPE_LENGTH,
TYPE) and (CTF, CARRIER_TYPE_LENGTH, CARRIER_TYPE) match exactly).

>>> import ndef
>>> record = ndef.HandoverCarrierRecord('application/vnd.wfa.wsc')
>>> record.name = 'wlan'
>>> print(record)
NDEF Handover Carrier Record ID 'wlan' CARRIER 'application/vnd.wfa.wsc' DATA 0 byte

.. class:: HandoverCarrierRecord(carrier_type, carrier_data=None, reference=None)

   Initialize the HandoverCarrierRecord with *carrier_type*, *carrier_data*, and
   a *reference* that sets the `Record.name` attribute. The carrier type has the
   same format as a record type name, i.e. the combination of NDEF Record TNF
   and TYPE that is used by the `Record.type` attribute. The carrier_data
   argument must be a valid `bytearray` initializer, or None.

   :param str carrier_type: initial value of the `carrier_type` attribute
   :param sequence carrier_data: initial value of the `carrier_data` attribute
   :param str reference: initial value of the the `name` attribute

   .. attribute:: type

      The Handover Select Record type is ``urn:nfc:wkt:Hc``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set. The
      *reference* init argument can also be used to set this value.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: carrier_type

      Get or set the carrier type as a `Record.type` formatted representation of
      the Handover Carrier Record CTF and CARRIER_TYPE fields.

   .. attribute:: carrier_data

      Contents of the Handover Carrier Record CARRIER_DATA field as a
      `bytearray`. The attribute itself is read-only but the content may be
      modified or expanded.


