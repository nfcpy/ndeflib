# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import ndef
import pytest
import _test_record_base

def pytest_generate_tests(metafunc):
    _test_record_base.generate_tests(metafunc)

class TestUriRecord(_test_record_base._TestRecordBase):
    RECORD = ndef.uri.UriRecord
    ATTRIB = "iri, uri"

    test_init_args_data = [
        ((), ('', '')),
        ((None,), ('', '')),
        (('http://nfcpy.org',), ('http://nfcpy.org', 'http://nfcpy.org')),
        ((u'http://nfcpy.org',), ('http://nfcpy.org', 'http://nfcpy.org')),
        ((b'http://nfcpy.org',), ('http://nfcpy.org', 'http://nfcpy.org')),
        (('nfcpy',), ('nfcpy', 'nfcpy')),
        (("http://www.nfcpy",), ("http://www.nfcpy", "http://www.nfcpy")),
        (("https://www.nfcpy",), ("https://www.nfcpy", "https://www.nfcpy")),
        (("http://nfcpy",), ("http://nfcpy", "http://nfcpy")),
        (("https://nfcpy",), ("https://nfcpy", "https://nfcpy")),
        (("tel:01234",), ("tel:01234", "tel:01234")),
        (("mailto:nfcpy",), ("mailto:nfcpy", "mailto:nfcpy")),
        (("ftp://anonymous:anonymous@nfcpy",),
         ("ftp://anonymous:anonymous@nfcpy","ftp://anonymous:anonymous@nfcpy")),
        (("ftp://ftp.nfcpy",), ("ftp://ftp.nfcpy", "ftp://ftp.nfcpy")),
        (("ftps://nfcpy",), ("ftps://nfcpy", "ftps://nfcpy")),
        (("sftp://nfcpy",), ("sftp://nfcpy", "sftp://nfcpy")),
        (("smb://nfcpy",), ("smb://nfcpy", "smb://nfcpy")),
        (("nfs://nfcpy",), ("nfs://nfcpy", "nfs://nfcpy")),
        (("ftp://nfcpy",), ("ftp://nfcpy", "ftp://nfcpy")),
        (("dav://nfcpy",), ("dav://nfcpy", "dav://nfcpy")),
        (("news:nfcpy",), ("news:nfcpy", "news:nfcpy")),
        (("telnet://nfcpy",), ("telnet://nfcpy", "telnet://nfcpy")),
        (("imap://nfcpy",), ("imap://nfcpy", "imap://nfcpy")),
        (("rtsp://nfcpy",), ("rtsp://nfcpy", "rtsp://nfcpy")),
        (("urn:nfcpy",), ("urn:nfcpy", "urn:nfcpy")),
        (("pop:nfcpy",), ("pop:nfcpy", "pop:nfcpy")),
        (("sip:123@server.net",), ("sip:123@server.net", "sip:123@server.net")),
        (("sips:nfcpy",), ("sips:nfcpy", "sips:nfcpy")),
        (("tftp:nfcpy",), ("tftp:nfcpy", "tftp:nfcpy")),
        (("btspp://nfcpy",), ("btspp://nfcpy", "btspp://nfcpy")),
        (("btl2cap://nfcpy",), ("btl2cap://nfcpy", "btl2cap://nfcpy")),
        (("btgoep://nfcpy",), ("btgoep://nfcpy", "btgoep://nfcpy")),
        (("tcpobex://nfcpy",), ("tcpobex://nfcpy", "tcpobex://nfcpy")),
        (("irdaobex://nfcpy",), ("irdaobex://nfcpy", "irdaobex://nfcpy")),
        (("file://nfcpy",), ("file://nfcpy", "file://nfcpy")),
        (("urn:epc:id:12345",), ("urn:epc:id:12345", "urn:epc:id:12345")),
        (("urn:epc:tag:12345",), ("urn:epc:tag:12345", "urn:epc:tag:12345")),
        (("urn:epc:pat:12345",), ("urn:epc:pat:12345", "urn:epc:pat:12345")),
        (("urn:epc:raw:12345",), ("urn:epc:raw:12345", "urn:epc:raw:12345")),
        (("urn:epc:12345",), ("urn:epc:12345", "urn:epc:12345")),
        (("urn:nfc:12345",), ("urn:nfc:12345", "urn:nfc:12345")),
        ((u"http://www.hääyö.com/~user/index.html",),
         (u"http://www.hääyö.com/~user/index.html",
          u"http://www.xn--hy-viaa5g.com/%7Euser/index.html")),
    ]
    test_init_kwargs_data = [
        (('URI',), "iri='URI'"),
    ]
    test_init_fail_data = [
        ((1,), ".iri accepts str or bytes, but not int"),
    ]
    test_decode_valid_data = [
        ('006e66637079', ("nfcpy",)),
        ('016e66637079', ("http://www.nfcpy",)),
        ('026e66637079', ("https://www.nfcpy",)),
        ('036e66637079', ("http://nfcpy",)),
        ('046e66637079', ("https://nfcpy",)),
        ('053031323334', ("tel:01234",)),
        ("066e66637079", ("mailto:nfcpy",)),
        ("076e66637079", ("ftp://anonymous:anonymous@nfcpy",)),
        ("086e66637079", ("ftp://ftp.nfcpy",)),
        ("096e66637079", ("ftps://nfcpy",)),
        ("0a6e66637079", ("sftp://nfcpy",)),
        ("0b6e66637079", ("smb://nfcpy",)),
        ("0c6e66637079", ("nfs://nfcpy",)),
        ("0d6e66637079", ("ftp://nfcpy",)),
        ("0e6e66637079", ("dav://nfcpy",)),
        ("0f6e66637079", ("news:nfcpy",)),
        ("106e66637079", ("telnet://nfcpy",)),
        ("116e66637079", ("imap:nfcpy",)),
        ("126e66637079", ("rtsp://nfcpy",)),
        ("136e66637079", ("urn:nfcpy",)),
        ("146e66637079", ("pop:nfcpy",)),
        ("156e66637079", ("sip:nfcpy",)),
        ("166e66637079", ("sips:nfcpy",)),
        ("176e66637079", ("tftp:nfcpy",)),
        ("186e66637079", ("btspp://nfcpy",)),
        ("196e66637079", ("btl2cap://nfcpy",)),
        ("1a6e66637079", ("btgoep://nfcpy",)),
        ("1b6e66637079", ("tcpobex://nfcpy",)),
        ("1c6e66637079", ("irdaobex://nfcpy",)),
        ("1d6e66637079", ("file://nfcpy",)),
        ("1e3132333435", ("urn:epc:id:12345",)),
        ("1f3132333435", ("urn:epc:tag:12345",)),
        ("203132333435", ("urn:epc:pat:12345",)),
        ("213132333435", ("urn:epc:raw:12345",)),
        ("223132333435", ("urn:epc:12345",)),
        ("233132333435", ("urn:nfc:12345",)),
    ]
    test_decode_error_data = [
        ('246e66637079', "decoding of URI identifier 36 is not defined"),
        ('ff6e66637079', "decoding of URI identifier 255 is not defined"),
        ('0380', "URI field is not valid UTF-8 data"),
        ('0300', "URI field contains invalid characters"),
    ]
    test_decode_relax_data = [
        ('246e66637079', ("nfcpy",)),
        ('ff6e66637079', ("nfcpy",)),
    ]
    test_encode_error = None
    test_format_args_data = [
        ((), "''"),
        (('http://example.com',), "'http://example.com'"),
    ]
    test_format_str_data = [
        ((), "NDEF Uri Record ID '' Resource ''"),
        (('tel:1234',), "NDEF Uri Record ID '' Resource 'tel:1234'"),
    ]

def test_uri_to_iri_conversion():
    record = ndef.UriRecord()
    # no netloc -> no conversion
    record.uri = u"tel:1234"
    assert record.iri == u"tel:1234"
    # with netloc -> conversion
    record.uri = u"http://www.xn--hy-viaa5g.com/%7Euser/index.html"
    assert record.iri == u"http://www.hääyö.com/~user/index.html"

uri_messages = [
    ('D1010a55036e666370792e6f7267',
     [ndef.UriRecord('http://nfcpy.org')]),
    ('91010a55036e666370792e6f7267 51010a55046e666370792e6f7267',
     [ndef.UriRecord('http://nfcpy.org'),
      ndef.UriRecord('https://nfcpy.org')]),
    ('D101115500736d74703a2f2f6e666370792e6f7267',
     [ndef.UriRecord('smtp://nfcpy.org')]),
]

@pytest.mark.parametrize("encoded, message", uri_messages)
def test_message_decode(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    print(list(ndef.message_decoder(octets)))
    assert list(ndef.message_decoder(octets)) == message

@pytest.mark.parametrize("encoded, message", uri_messages)
def test_message_encode(encoded, message):
    octets = bytes(bytearray.fromhex(encoded))
    print(list(ndef.message_encoder(message)))
    assert b''.join(list(ndef.message_encoder(message))) == octets

