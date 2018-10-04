#!/usr/bin/env python3
import json
import os

import requests
from cryptojwt.jwt import JWT
from cryptojwt.key_jar import KeyJar
from oidcmsg.oidc import JsonWebToken

EDIR = 'entities'
EM = 'entity_metadata'

for _dir in [EM]:
    if not os.path.isdir(_dir):
        os.makedirs(_dir)

for _name in os.listdir(EDIR):
    fname = os.path.join(EDIR, _name)
    einfo = json.loads(open(fname).read())
    keyjar = KeyJar()
    keyjar.import_jwks_as_json(einfo['signing_keys'], einfo['entity_id'])

    try:
        resp = requests.request('GET', einfo['metadata_endpoint'], verify=False)
    except Exception as err:
        continue

    if resp.status_code == 200:
        _jwt = JWT(keyjar)
        metadata_statement = _jwt.unpack(resp.text)
        # Remove the JWT attributes
        for attr in JsonWebToken.c_param.keys():
            try:
                del metadata_statement[attr]
            except KeyError:
                pass
        try:
            del metadata_statement['kid']
        except KeyError:
            pass

        fp = open('{}/{}'.format(EM, _name), 'w')
        fp.write(json.dumps(metadata_statement))
        fp.close()
