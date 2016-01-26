#!/usr/bin/env python
from datetime import datetime
from hashlib import sha1
import hmac
import sys


'''
Authorization = "AWS" + " " + AWSAccessKeyId + ":" + Signature;

Signature = Base64( HMAC-SHA1( YourSecretAccessKeyID, UTF-8-Encoding-Of( StringToSign ) ) );

StringToSign = HTTP-Verb + "\n" +
	Content-MD5 + "\n" +
	Content-Type + "\n" +
	Date + "\n" +
	CanonicalizedAmzHeaders +
	CanonicalizedResource;

CanonicalizedResource = [ "/" + Bucket ] +
	<HTTP-Request-URI, from the protocol name up to the query string> +
	[ subresource, if present. For example "?acl", "?location", "?logging", or "?torrent"];

CanonicalizedAmzHeaders = <described below>
'''


def canon_resource(vhost_mode, bucket, url):
    val = "/%s" % bucket if vhost_mode else ""
    val = val+url

    return val


def str_to_sign(method, vhost_mode, bucket, url):
    cr = canon_resource(vhost_mode, bucket, url)
    ctype = ""
    cmd5 = ""
    dt = datetime.utcnow().isoformat('T')+"Z"
    azh = ""
    retval = "%s\n%s\n%s\n%s\n%s%s" % (method,
        cmd5, ctype, dt, azh, cr)
    headers = {}
    headers['Date'] = dt
    if vhost_mode:
        headers['Host'] = bucket
    return {'s2s': retval, 'headers': headers }


def sign(key, method, vhost_mode, bucket, url):
    raw = str_to_sign(method, vhost_mode, bucket, url)
    retval = hmac.new(key, raw['s2s'], sha1)   
    return {'sign': retval.digest().encode("base64").rstrip("\n"),
        'headers': raw['headers']}

def az_h(ak, key, method, vhost_mode, bucket, url):
    sig = sign(key, method, vhost_mode, bucket, url)
    ahv = "AWS %s:%s" % (ak, sig['sign'])
    sig['headers']['Authorization'] = ahv
    return sig['headers']


if __name__ == "__main__":
    ak = sys.argv[1]
    k = sys.argv[2]
    print az_h(ak, k, "GET", True, "hw.anomalizer", "/lock.txt")
    print az_h(ak, k, "GET", False, "hw.anomalizer", "/hw.anomalizer/nq.c")
