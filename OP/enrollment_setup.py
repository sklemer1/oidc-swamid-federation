#!/usr/bin/env python3
import importlib
import json
import os
import sys
from urllib.parse import quote_plus

from cryptojwt.key_jar import init_key_jar


for _dir in ['public', 'private']:
    if not os.path.isdir(_dir):
        os.makedirs(_dir)

sys.path.insert(0, '.')
config = importlib.import_module('conf')
sys.path.pop(0)

kj = init_key_jar(
    **config.CONFIG['server_info']['federation']['self_signer'])

iss = config.CONFIG['server_info']['issuer']
ent_id = quote_plus(iss)

enrolement_info = {
    'entity_id': iss,
    'signing_keys': kj.export_jwks_as_json(),
    'metadata_endpoint': '{}/metadata'.format(iss)
}

fp = open('enrollment_info', 'w')
fp.write(json.dumps(enrolement_info))
fp.close()


