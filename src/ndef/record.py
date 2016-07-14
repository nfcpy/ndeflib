# -*- coding: utf-8 -*-
"""Implementation of the generic NDEF Record class.

This module provides the generic NDEF Record class implementation. All
specialized records are subclasses of the ndef.record.Record base with
type-specific payload decode and encode method implementations. This
module also defines the DecodeError and EncodeError exceptions that
may be raised when decoding from or encoding to transmission octets.
Finally, the record module defines a decorator helper function to
convert the value argument of attribute setter functions into ascii,
latin or unicode restricted str or unicode type for Python 2 or 3.

"""
from __future__ import absolute_import, division
from types import FunctionType, MethodType
from abc import ABCMeta, abstractmethod
from functools import wraps
from io import BytesIO
import collections
import struct
import re

import sys
_PY2 = sys.version_info < (3,)

if _PY2:  # pragma: no cover
    from urlparse import urlsplit
    from binascii import hexlify
else:  # pragma: no cover
    from urllib.parse import urlsplit
    unicode = str

    def hexlify(octets):
        return octets.hex()


class DecodeError(Exception):
    """NDEF decode error exception class."""
    pass


class EncodeError(Exception):
    """NDEF encode error exception class."""
    pass


class Record(object):
    """The Record class implements generic decoding and encoding of an
    NDEF Record. The NDEF Record TNF and TYPE fields are represented
    by the Record.type attribute. The NDEF Record ID field and the
    PAYLOAD field are represented by the Record.name and Record.data
    attributes. A Record instance is initialized with record type,
    name, and data arguments.

    The record type reflects the NDEF Record TNF and TYPE fields in a
    single string value. For TNF value 0 it is an empty string. For
    TNF value 1 or 4 it is the prefix 'urn:nfc:wkt:' or 'urn:nfc:ext:'
    followed by the TYPE field. For TNF value 5 or 6 it is the single
    word 'unknown' (TNF 5) or 'unchanged' (TNF 6). For TNF value 2 it
    is the Internet Media Type formatted TYPE field. For TNF value 3
    it is the Absolute URI formatted TYPE field. The Record.type
    attribute is read-only.

    >>> import ndef
    >>> record = ndef.Record('urn:nfc:wkt:T')
    >>> list(ndef.message_encoder([record]))
    [b'\\xd1\\x01\\x00T']

    The record name corresponds to the NDEF Record ID field. The
    Record.name attribute is read-writable.

    >>> record.name = 'identifier'
    >>> list(ndef.message_encoder([record]))
    [b'\\xd9\\x01\\x00\\nTidentifier']

    The record data is the content of the NDEF Record PAYLOAD field
    octets. The Record.data attribute is read-only but presents a
    bytearray object that may be modified.

    >>> record.data.extend(b'\\x02enHello World')
    >>> list(ndef.message_encoder([record]))
    [b'\\xd9\\x01\\x0e\\nTidentifier\\x02enHello World']

    For derived record classes the data attribute is a bytes object
    that can not be modified but reflects the the current PAYLOAD
    encoding of the record's state.

    >>> record = ndef.TextRecord('Hello World')
    >>> record.data
    b'\\x02enHello World'

    """
    # A Record object is not be hashable because we allow state
    # modifications.
    __hash__ = None

    # NDEF supports up to 4 GB payload but it seems practical and wise
    # to restrict the maximum capacity we're dealing with to 1 MB.
    MAX_PAYLOAD_SIZE = 0x100000

    # The _known_types dictionary holds the record type / record class
    # associations that can be decoded into specialized classes. It is
    # set via register_type. For specialized records it may be
    # shadowed by a version that is specific for the context of the
    # specialized record class.
    _known_types = dict()

    @classmethod
    def register_type(cls, record_class):
        """Register a derived record class as a well-known type for
        decoding. This creates an entry for the record_class type
        string to be decoded as a record_class instance. Well-known
        type registrations are associated with the record class on
        which register_type was called. A Record.register_type call
        adds to the global mapping of well-known types. For a derived
        record class the type will be well-known only in the context
        of the derived record class.

        """
        assert issubclass(record_class, Record)
        if cls != Record and id(cls._known_types) == id(Record._known_types):
            cls._known_types = {}  # shadow Record.known_types
        cls._known_types[record_class._type] = record_class

    def __init__(self, type=None, name=None, data=None):
        """Initialize the Record instance with type, name and data
        attributes. The type argument should not normally be None,
        unless an empty NDEF Record is desired.

        """
        self._type = self._decode_type(*self._encode_type(type))
        self.name = name
        if data is None:
            self._data = bytearray()
        elif isinstance(data, str):
            self._data = bytearray(data if _PY2 else data.encode('latin'))
        elif isinstance(data, (bytearray, collections.Sequence)):
            self._data = bytearray(data)
        else:
            errstr = "data may be sequence or None, but not {}"
            raise self._type_error(errstr, data.__class__.__name__)

    @property
    def type(self):
        """A str object representing the NDEF Record TNF and TYPE fields. The
        type attribute is read-only.

        """
        return self._type

    @property
    def name(self):
        """A str object representing the NDEF Record ID field. The name
        attribute is read-writable.

        """
        return getattr(self, '_name', '')

    @name.setter
    def name(self, value):
        if value is None:
            _value = ''
        elif isinstance(value, str):
            _value = (str(value) if _PY2 else
                      value.encode('latin').decode('latin'))
        elif isinstance(value, (bytes, bytearray)):
            _value = (bytes(value) if _PY2 else
                      value.decode('latin'))
        else:
            errstr = "name may be str or None, but not {}"
            raise self._type_error(errstr, type(value).__name__)

        if len(_value) > 255:
            errstr = 'name can not be more than 255 octets NDEF Record ID'
            raise self._value_error(errstr)

        self._name = _value

    @property
    def data(self):
        """A bytearray or bytes object that holds the octets of the NDEF
        Record PAYLOAD field. For a generic Record class instance this
        is a bytearray. For a derived record class instance this is a
        bytes object (a bytes str for Python 2 - note that unlike the
        Python 3 bytes type this is a sequence of characters).

        """
        if type(self) is Record:
            return self._data
        else:
            return bytes(self._encode_payload())

    def __eq__(self, other):
        """Compare this Record instance against an other Record instance. The
        two records are equal if their type, name and data attributes
        match exactly. For derived record classes this means that the
        payload will be encoded for comparision.

        """
        return (isinstance(other, Record) and
                self.type == other.type and
                self.name == other.name and
                self.data == other.data)

    def __repr__(self):
        """Return a formal representation of the Record object."""
        return "{}.{}({:args})".format(
            self.__module__, self.__class__.__name__, self)

    def __format__(self, format_spec):
        """Return an init argument string if format_spec is 'args', otherwise
        apply the default str formatting.

        """
        if format_spec == 'args':
            return "{!r}, {!r}, {!r}".format(self.type, self.name, self.data)
        if format_spec == 'data':
            _data = self.data  # let derived records encode only once
            s = "PAYLOAD {} byte".format(len(_data))
            if len(_data) > 0:
                s += " '{}'".format(hexlify(_data[0:10]))
            if len(_data) > 10:
                s += " ... {} more".format(len(_data) - 10)
            return s
        return format(str(self), format_spec)

    def __str__(self):
        """Return an informal representation suitable for printing."""
        cls = type(self)
        if cls is Record:
            s = "NDEF Record TYPE '{r.type}'"
        else:
            name = (cls.__module__.split('.')[-1].capitalize() + cls.__name__
                    if isinstance(self, LocalRecord) else cls.__name__)
            s = "NDEF {}".format(re.sub('(?!^)([A-Z]+)', r' \1', name))
        return (s + " ID '{r.name}' {r:data}").format(r=self)

    #
    # private encode/decode interface for the message encoder/decoder
    #

    def _encode(self, mb=False, me=False, cf=False, stream=None):
        """Encode the NDEF record and return the encoded octets as a bytes
        object (if stream is None) or write the octets into the
        file-like byte stream and return the number of octets
        written. The mb, me, and cf arguments are interpreted as truth
        values for the NDEF Record Message Begin, Message End, and
        Chunk Flag bits in the first octet.

        """
        TNF, TYPE = self._encode_type(self.type)
        if TNF == 0:
            TYPE, ID, PAYLOAD = b'', b'', b''
        elif TNF == 5:
            TYPE, ID, PAYLOAD = b'', self.name.encode('latin'), self.data
        elif TNF == 6:
            TYPE, ID, PAYLOAD = b'', b'', self.data
        else:
            ID, PAYLOAD = self.name.encode('latin'), self.data

        if len(PAYLOAD) > self.MAX_PAYLOAD_SIZE:
            errstr = "payload of more than {} octets can not be encoded"
            raise self._encode_error(errstr.format(self.MAX_PAYLOAD_SIZE))

        MB = 0b10000000 if mb else 0
        ME = 0b01000000 if me else 0
        CF = 0b00100000 if cf else 0
        SR = 0b00010000 if len(PAYLOAD) < 256 else 0
        IL = 0b00001000 if len(ID) > 0 else 0

        octet0 = MB | ME | CF | SR | IL | TNF
        layout = '>BB' + ('B' if SR else 'L') + ('B' if IL else '')
        fields = (octet0, len(TYPE), len(PAYLOAD)) + ((len(ID),) if IL else ())

        s = BytesIO() if stream is None else stream
        n = s.write(struct.pack(layout, *fields) + TYPE + ID + PAYLOAD)
        return s.getvalue() if stream is None else n

    @classmethod
    def _decode(cls, stream, errors, known_types):
        try:
            octet0 = ord(stream.read(1)[0]) if _PY2 else stream.read(1)[0]
        except IndexError:
            return (None, False, False, False)

        MB = bool(octet0 & 0b10000000)
        ME = bool(octet0 & 0b01000000)
        CF = bool(octet0 & 0b00100000)
        SR = bool(octet0 & 0b00010000)
        IL = bool(octet0 & 0b00001000)
        TNF = octet0 & 0b00000111

        if TNF == 7:
            raise cls._decode_error("TNF field value must be between 0 and 6")

        try:
            layout = '>B' + ('B' if SR else 'L') + ('B' if IL else '')
            bcount = struct.calcsize(layout)
            fields = struct.unpack(layout, stream.read(bcount)) + (0,)
        except struct.error:
            errstr = "buffer underflow at reading length fields"
            raise cls._decode_error(errstr)

        try:
            if TNF in (0, 5, 6):
                assert fields[0] == 0, "TYPE_LENGTH must be 0"
            if TNF == 0:
                assert fields[2] == 0, "ID_LENGTH must be 0"
                assert fields[1] == 0, "PAYLOAD_LENGTH must be 0"
            if TNF in (1, 2, 3, 4):
                assert fields[0] > 0, "TYPE_LENGTH must be > 0"
        except AssertionError as error:
            raise cls._decode_error(str(error) + " for TNF value {}", TNF)

        if fields[1] > cls.MAX_PAYLOAD_SIZE:
            errstr = "payload of more than {} octets can not be decoded"
            raise cls._decode_error(errstr.format(cls.MAX_PAYLOAD_SIZE))

        TYPE, ID, PAYLOAD = [stream.read(fields[i]) for i in (0, 2, 1)]

        try:
            assert fields[0] == len(TYPE), "TYPE field"
            assert fields[2] == len(ID), "ID field"
            assert fields[1] == len(PAYLOAD), "PAYLOAD field"
        except AssertionError as error:
            raise cls._decode_error("buffer underflow at reading {}", error)

        record_type = cls._decode_type(TNF, TYPE)
        if record_type in known_types:
            record_cls = known_types[record_type]
            min_payload_length = record_cls._decode_min_payload_length
            max_payload_length = record_cls._decode_max_payload_length
            if len(PAYLOAD) < min_payload_length:
                errstr = "payload length can not be less than {}"
                raise record_cls._decode_error(errstr, min_payload_length)
            if len(PAYLOAD) > max_payload_length:
                errstr = "payload length can not be more than {}"
                raise record_cls._decode_error(errstr, max_payload_length)
            record = record_cls._decode_payload(PAYLOAD, errors)
            assert isinstance(record, Record)
            record.name = ID
        else:
            record = Record(record_type, ID, PAYLOAD)

        return (record, MB, ME, CF)

    _decode_min_payload_length = 0
    _decode_max_payload_length = 0xffffffff

    @classmethod
    def _decode_payload(cls, octets, errors):
        # This classmethod is called to decode the PAYLOAD of a known
        # record type. The PAYLOAD data is supplied with the octets
        # argument as a bytes object (which on Python 2 is a str). The
        # implementation must either return a new Record subclass
        # object or raise a self._decode_error(...) exception. The
        # errors argument indicates whether to be 'strict' or 'relax'
        # on decoding errors.
        clsname = cls.__module__ + '.' + cls.__name__
        errstr = "{cls} must implement the _decode_payload() method"
        raise NotImplementedError(errstr.format(cls=clsname))

    @classmethod
    def _decode_type(cls, TNF, TYPE):
        # Convert an NDEF Record TNF and TYPE to a record type
        # string. For TNF 1 and 4 the record type string is a prexix
        # plus TYPE, for TNF 0, 5, and 6 it is a fixed string, for TNF
        # 2 and 3 it is directly the TYPE string. Other TNF values are
        # not allowed.
        prefix = ('', 'urn:nfc:wkt:', '', '', 'urn:nfc:ext:',
                  'unknown', 'unchanged')
        if not 0 <= TNF <= 6:
            raise cls._value_error('NDEF Record TNF values must be 0 to 6')
        if TNF in (0, 5, 6):
            TYPE = b''
        return prefix[TNF] + (TYPE if _PY2 else TYPE.decode('ascii'))

    @classmethod
    def _encode_type(cls, value):
        # Convert a record type string to an NDEF Record TNF and TYPE
        # tuple. Record type strings '', 'unknown' and 'unchanged'
        # become TNF values 0, 5, and 6, respectively. Record types
        # starting with 'urn:nfc:wkt:' or 'urn:nfc:ext:' become TNF 1
        # or 4. A record type that looks like a mime type becomes TNF
        # 2. A record type that looks like an absolute URI becomes TNF
        # 3. Anything else produces a ValueError. A record type that
        # results in a TYPE field longer than 255 byte also produces a
        # ValueError.
        if value is None:
            _value = b''
        elif isinstance(value, bytearray):
            _value = bytes(value)
        elif isinstance(value, (bytes, str)):
            _value = (value if _PY2 or isinstance(value, bytes)
                      else value.encode('ascii'))
        else:
            errstr = 'record type string may be str or bytes, but not {}'
            raise cls._type_error(errstr.format(type(value).__name__))

        if _value == b'':
            (TNF, TYPE) = (0, b'')
        elif _value.startswith(b'urn:nfc:wkt:'):
            (TNF, TYPE) = (1, _value[12:])
        elif re.match(b'[a-zA-Z0-9-]+/[a-zA-Z0-9-+.]+', _value):
            (TNF, TYPE) = (2, _value)
        elif all(urlsplit(_value)[0:3]):
            (TNF, TYPE) = (3, _value)
        elif _value.startswith(b'urn:nfc:ext:'):
            (TNF, TYPE) = (4, _value[12:])
        elif _value == b'unknown':
            (TNF, TYPE) = (5, b'')
        elif _value == b'unchanged':
            (TNF, TYPE) = (6, b'')
        else:
            errstr = "can not convert the record type string '{}'"
            raise cls._value_error(errstr, value)

        if len(TYPE) > 255:
            errstr = "an NDEF Record TYPE can not be more than 255 octet"
            raise cls._value_error(errstr)

        return (TNF, TYPE)

    @classmethod
    def _decode_struct(cls, fmt, octets, offset=0):
        # Decode octets from a packed structure using the struct
        # module with slightly extended format string syntax. A
        # trailing '*' means to return all remaining octets as an
        # additional bytes value. A trailing '+' means to return an
        # additional bytes value with as many octets as the value of
        # the last converted value (which must be an integer) or raise
        # a DecodeError there are fewer remaining octets than
        # required. A 'BB+' format is the equivalent of 8-bit TLV
        # decoding that returns a Type and Value.
        s = struct.Struct(fmt.rstrip('*+'))
        try:
            values = s.unpack_from(octets, offset)
            if fmt.endswith('*'):
                values += (octets[(offset + s.size):],)
            elif fmt.endswith('+'):
                length = values[-1]
                offset = offset + s.size
                values = values[0:-1] + (octets[offset:(offset + length)],)
                if len(values[-1]) < length:
                    errstr = "need {} more octet to unpack format '{}'"
                    needed = length - len(values[-1])
                    raise cls._decode_error(errstr, needed, fmt)
        except struct.error as error:
            raise cls._decode_error(str(error))
        else:
            return values if len(values) > 1 else values[0]

    @classmethod
    def _encode_struct(cls, fmt, *values):
        # Encode values into a packed structure using the struct
        # module with slightly extended format string syntax. A
        # trailing '*' means that the last value is not part of the
        # format string but to be appended to the returned octets. A
        # trailing '+' means that the length of the last argument is
        # encoded as the value of the last format string element and
        # the last argument value then appended. A 'BB+' format with
        # two input values (one 8-bit integer and one octet sequence)
        # is the equivalent of 8-bit TLV encoding.
        s = struct.Struct(fmt.rstrip('*+'))
        try:
            if fmt.endswith('*'):
                octets = s.pack(*values[0:-1]) + values[-1]
            elif fmt.endswith('+'):
                length = len(values[-1])
                octets = s.pack(*(values[0:-1] + (length,))) + values[-1]
            else:
                octets = s.pack(*values)
        except struct.error as error:
            raise cls._encode_error(str(error))
        else:
            return octets

    @classmethod
    def _decode_error(cls, fmt, *args, **kwargs):
        # Return a DecodeError instance with a formatted error string
        # that starts with the module and class name.
        clname = cls.__module__ + "." + cls.__name__
        return DecodeError(clname + " " + fmt.format(*args, **kwargs))

    @classmethod
    def _encode_error(cls, fmt, *args, **kwargs):
        # Return a EncodeError instance with a formatted error string
        # that starts with the module and class name.
        clname = cls.__module__ + "." + cls.__name__
        return EncodeError(clname + " " + fmt.format(*args, **kwargs))

    @classmethod
    def _type_error(cls, fmt, *args, **kwargs):
        # Return a TypeError instance with a formatted error string.
        # The error string starts with module and class name. The
        # formatted string fmt is joined with a '.' if the first word
        # of fmt is the name of a non-function class attribute,
        # otherwise it is joined with ' '.
        record = cls.__module__ + "." + cls.__name__
        attrib = getattr(cls, fmt.split(' ', 1)[0], Record._type_error)
        joinby = ('.', ' ')[isinstance(attrib, (FunctionType, MethodType))]
        return TypeError(record + joinby + fmt.format(*args, **kwargs))

    @classmethod
    def _value_error(cls, fmt, *args, **kwargs):
        # Return a ValueError instance with a formatted error string.
        # The error string starts with module and class name. The
        # formatted string fmt is joined with a '.' if the first word
        # of fmt is the name of a non-function class attribute,
        # otherwise it is joined with ' '.
        record = cls.__module__ + "." + cls.__name__
        attrib = getattr(cls, fmt.split(' ', 1)[0], Record._value_error)
        joinby = ('.', ' ')[isinstance(attrib, (FunctionType, MethodType))]
        return ValueError(record + joinby + fmt.format(*args, **kwargs))

    @classmethod
    def _value_to_ascii(cls, value, name):
        # Convert a str or bytes value to ascii text returned as str
        # type. Accepted input types are str, unicode, bytes, and
        # bytearray. For Python 3 the unicode type is mapped to
        # str. The Python 2 bytes type is equal to str. The name
        # argument is used for error string formatting.
        try:
            if isinstance(value, (str, unicode, bytes)):
                return (value.encode('ascii') if _PY2 else
                        value.decode('ascii') if isinstance(value, bytes) else
                        value.encode('ascii').decode('ascii'))
            if isinstance(value, bytearray):
                return (str(value).encode('ascii') if _PY2 else
                        value.decode('ascii'))
            errstr = name + ' accepts str or bytes, but not {}'
            raise cls._type_error(errstr, type(value).__name__)
        except UnicodeError:
            errstr = name + ' conversion requires ascii text, but got {!r}'
            raise cls._value_error(errstr, value)

    @classmethod
    def _value_to_latin(cls, value, name):
        # Convert a str or bytes value to latin text returned as str
        # type. Accepted input types are str, unicode, bytes, and
        # bytearray. For Python 3 the unicode type is mapped to
        # str. The Python 2 bytes type is equal to str. The name
        # argument is used for error string formatting.
        try:
            if isinstance(value, (str, unicode, bytes)):
                return (value if _PY2 and isinstance(value, str) else
                        value.encode('latin') if _PY2 else
                        value.decode('latin') if isinstance(value, bytes) else
                        value.encode('latin').decode('latin'))
            if isinstance(value, bytearray):
                return str(value) if _PY2 else value.decode('latin')
            errstr = name + ' accepts str or bytes, but not {}'
            raise cls._type_error(errstr, type(value).__name__)
        except UnicodeError:
            errstr = name + ' conversion requires latin text, but got {!r}'
            raise cls._value_error(errstr, value)

    @classmethod
    def _value_to_unicode(cls, value, name):
        # Convert a str or bytes value to unicode. The return type is
        # unicode for Python 2 and str for Python 3. Accepted input
        # types are str, unicode, bytes, and bytearray. For Python 3
        # the unicode type is mapped to str. The Python 2 bytes type
        # is equal to str. Conversion from non-unicode input requires
        # ascii text. The name argument is used for error string
        # formatting.
        try:
            if isinstance(value, (str, unicode, bytes)):
                return (unicode(value) if _PY2 else
                        value if isinstance(value, str) else
                        value.decode('ascii'))
            if isinstance(value, bytearray):
                return value.decode('ascii')
            errstr = name + ' accepts str or bytes, but not {}'
            raise cls._type_error(errstr, type(value).__name__)
        except UnicodeError:
            errstr = name + ' conversion requires ascii text, but got {!r}'
            raise cls._value_error(errstr, value)


class GlobalRecord(Record):  # pragma: no cover
    """The GlobalRecord class is mostly to provide a namespace for
    grouping record classes in help(). Beyond that it is real abstract
    class that helps ensure derived classes implement the required
    interface methods.

    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        assert hasattr(self, '_type'),\
            "derived class must define the '_type' class attribute"

    @abstractmethod
    def _encode_payload(self):
        pass

    @abstractmethod
    def _decode_payload(cls, octets, errors):
        pass


class LocalRecord(Record):  # pragma: no cover
    """The LocalRecord class is mostly to provide a namespace for
    grouping record classes in help(). Beyond that it is real abstract
    class that helps ensure derived classes implement the required
    interface methods.

    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        assert hasattr(self, '_type'),\
            "derived class must define the '_type' class attribute"

    @abstractmethod
    def _encode_payload(self):
        pass

    @abstractmethod
    def _decode_payload(cls, octets, errors):
        pass


# A decorator for property setters that runs a given conversion on the
# value argument and automatically supplies the property name to the
# conversion method for error string formatting.


def convert(conversion):
    def converter(setter):
        @wraps(setter)
        def wrapper(self, value):
            _convert = getattr(self, '_' + conversion)
            return setter(self, _convert(value, setter.__name__))
        return wrapper
    return converter


"""
class MyRecord(Record):
    _type = ''

    def __init__(self):
        self._xyz = u''

    def _encode_payload(self):
        return b''

    @property
    def xyz(self):
        return self._xyz

    @xyz.setter
    @convert('value_to_unicode')
    def xyz(self, value):
        self._xyz = value
"""
