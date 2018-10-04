#!/usr/bin/env python3
import os
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from fedoidcmsg.bundle import FSJWKSBundle
from fedoidcmsg.test_utils import create_federation_entities
from cryptojwt.key_jar import KeyJar


# make sure the necessary directories are there
for _dir in ['public', 'private', 'fo_bundle']:
    if not os.path.isdir(_dir):
        os.mkdir(_dir)

# The kind of keys the federation entities has
FED_KEYDEF = [{"type": "EC", "crv": "P-256", "use": ["sig"]}]

# Identifiers for all the Federations
ALL = ['https://edugain.org', 'https://swamid.sunet.se']

_path = os.path.realpath(__file__)
root_dir, _fname = os.path.split(_path)

# Create the federation entities
FEDENT = create_federation_entities(ALL, FED_KEYDEF, root_dir=root_dir)

# create and load the key bundle
bundle = FSJWKSBundle(iss='jra3t3', fdir='fo_bundle',
                      key_conv={'to': quote_plus, 'from': unquote_plus})

for iss in ALL:
    kj = KeyJar()
    kj.import_jwks(FEDENT[iss].signing_keys_as_jwks(), iss)
    bundle[iss] = kj
