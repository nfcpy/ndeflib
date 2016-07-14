.. -*- mode: rst; fill-column: 80 -*-

Device Information Record
-------------------------

The NDEF Device Information Record is a well-known record type defined by the
`NFC Forum`_. It carries a number of Type-Length-Value data elements that
provide information about the device, such as the manufacturer and device model
name.

.. class:: DeviceInformationRecord(vendor_name, model_name, \
           unique_name=None, uuid_string=None, version_string=None)

   Initialize the record with required and optional device information. The
   vendor_name and model_name arguments are required, all other arguments are
   optional information.

   :param str vendor_name: sets the :attr:`vendor_name` attribute
   :param str model_name: sets the :attr:`model_name` attribute
   :param str unique_name: sets the :attr:`unique_name` attribute
   :param str uuid_string: sets the :attr:`uuid_string` attribute
   :param str version_string: sets the :attr:`version_string` attribute

   .. attribute:: type

      The Device Information Record type is ``urn:nfc:wkt:Di``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: vendor_name

      Get or set the device vendor name `str`.

   .. attribute:: model_name

      Get or set the device model name `str`.

   .. attribute:: unique_name

      Get or set the device unique name `str`.

   .. attribute:: uuid_string

      Get or set the universially unique identifier `str`.

   .. attribute:: version_string

      Get or set the device firmware version `str`.

   .. attribute:: undefined_data_elements

      A list of undefined data elements as named tuples with data_type and
      data_bytes attributes. This is a reference to the internal list and may
      thus be updated in-place but it is strongly recommended to use the
      add_undefined_data_element method with data_type and data_bytes
      validation. It would also not be safe to rely on such implementation
      detail.

   .. method:: add_undefined_data_element(data_type, data_bytes)

      Add an undefined (reserved future use) device information data
      element. The data_type must be an an integer in range(5, 256). The
      data_bytes argument provides the up to 255 octets to transmit.

      Undefined data elements should not normally be added. This method is
      primarily here to allow data elements defined by future revisions of the
      specification before this implementation is updated.

   >>> import ndef
   >>> record = ndef.DeviceInformationRecord('Sony', 'RC-S380')
   >>> record.unique_name = 'Black NFC Reader connected to PC'
   >>> record.uuid_string = '123e4567-e89b-12d3-a456-426655440000'
   >>> record.version_string = 'NFC Port-100 v1.02'
   >>> len(b''.join(ndef.message_encoder([record])))
   92

