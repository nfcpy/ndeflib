.. -*- mode: rst; fill-column: 80 -*-

Smartposter Record
------------------

The `NFC Forum`_ Smart Poster Record Type Definition defines a structure that
associates an Internationalized Resource Identifier (or Uniform Resource
Identifier) with various types of metadata. For a user this is most noteably the
ability to attach descriptive text in different languages as well as image data
for icon rendering. For a smartposter application this is a recommendation for
processing as well as resource type and size hints to guide a strategy for
retrieving the resource.

.. class:: SmartposterRecord(resource, title=None, action=None, icon=None, \
           resource_size=None, resource_type=None)

   Initialize a `SmartposterRecord` instance. The only required argument is the
   Internationalized Resource Identifier *resource*, all other arguments are
   optional metadata.

   :param str resource: Internationalized Resource Identifier
   :param title: English title `str` or `dict` with language keys and title values
   :type title: str or dict
   :param action: assigns a value to the :attr:`action` attribute
   :type action: str or int
   :param icon: PNG data `bytes` or `dict` with {icon-type: icon_data} items
   :type icon: bytes or dict
   :param int resource_size: assigns a value to the :attr:`resource_size` attribute
   :param str resource_type: assigns a value to the :attr:`resource_type` attribute

   .. attribute:: type

      The Smartposter Record type is ``urn:nfc:wkt:Sp``.

   .. attribute:: name

      Value of the NDEF Record ID field, an empty `str` if not set.

   .. attribute:: data

      A `bytes` object containing the NDEF Record PAYLOAD encoded from the
      current attributes.

   .. attribute:: resource

      Get or set the Smartposter resource identifier. A set value is interpreted
      as an internationalized resource identifier (so it can be unicode). When
      reading, the resource attribute returns a :class:`UriRecord` which can be
      used to set the :attr:`UriRecord.iri` and :attr:`UriRecord.uri` directly.

   .. attribute:: title

      The title string for language code 'en' or the first title string that was
      decoded or set. If no title string is available the value is `None`. The
      attribute can not be set, use :meth:`set_title`.

   .. attribute:: titles

      A dictionary of all decoded or set titles with language `str` keys and
      title `str` values. The attribute can not be set, use :meth:`set_title`.

   .. method:: set_title(title, language='en', encoding='UTF-8')

      Set the title string for a specific language which defaults to 'en'. The
      transfer encoding may be set to either 'UTF-8' or 'UTF-16', the default is
      'UTF-8'.

   .. attribute:: action

      Get or set the recommended action for handling the Smartposter resource. A
      set value may be 'exec', 'save', 'edit' or an index thereof. A read value
      is either one of above strings or `None` if no action value was decoded or
      set.

   .. attribute:: icon

      The image data `bytes` for an 'image/png' type smartposter icon or the
      first icon decoded or added. If no icon is available the value is
      `None`. The attribute can not be set, use :meth:`add_icon`.

   .. attribute:: icons

      A dictionary of icon images with mime-type `str` keys and icon-data
      `bytes` values. The attribute can not be set, use :meth:`add_icon`.

   .. method:: add_icon(icon_type, icon_data)

      Add a Smartposter icon as icon_data bytes for the image or video mime-type
      string supplied with icon_type.

   .. attribute:: resource_size

      Get or set the `int` size hint for the Smartposter resource. `None` if a
      size hint was not decoded or set.

   .. attribute:: resource_type

      Get or set the `str` type hint for the Smartposter resource. `None` if a
      type hint was not decoded or set.

   >>> import ndef
   >>> record = ndef.SmartposterRecord('https://github.com/nfcpy/ndeflib')
   >>> record.set_title('Python package for parsing and generating NDEF', 'en')
   >>> record.resource_type = 'text/html'
   >>> record.resource_size = 1193970
   >>> record.action = 'exec'
   >>> len(b''.join(ndef.message_encoder([record])))
   115

