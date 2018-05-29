#!/usr/bin/env python3
import json
import os
import sys
from urllib.parse import quote_plus

for _dir in ['entities']:
    if not os.path.isdir(_dir):
        os.makedirs(_dir)

mdss_sign_key = open('public/mdss.json').read()

for entity in sys.argv[1:]:
    einfo = json.loads(open('../{}/enrollment_info'.format(entity)).read())
    eid = quote_plus(einfo['entity_id'])
    fp = open('entities/{}'.format(eid), 'w')
    fp.write(json.dumps(einfo))
    fp.close()

    fp = open('../{}/mdss.jwks'.format(entity), 'w')
    fp.write(mdss_sign_key)
    fp.close()
