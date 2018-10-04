#!/usr/bin/env python3
import copy
import json
import os
from urllib.parse import quote_plus

from fedoidcmsg import MIN_SET
from fedoidcmsg.entity import make_federation_entity
from fedoidcmsg.test_utils import make_signing_sequence


def clear_metadata_statements(entities):
    for fedent in entities:
        fedent.metadata_statements = copy.deepcopy(MIN_SET)


for _dir in ['private', 'public', 'sms/registration', 'sms/discovery',
             'sms/response']:
    if not os.path.isdir(_dir):
        os.makedirs(_dir)

conf = json.loads(open('mdss_conf.json').read())
fe = make_federation_entity(config=conf)

FEDENT = {fe.iss: fe}
for _cnf in ['swamid_conf.json', 'edugain_conf.json']:
    conf = json.loads(open(_cnf).read())
    FEDENT[conf['entity_id']] = make_federation_entity(config=conf)

# Short cuts
SWAMID = FEDENT['https://swamid.sunet.se']
EDUGAIN = FEDENT['https://edugain.org']



for seq in [[fe.iss, SWAMID.iss, EDUGAIN.iss], [fe.iss, SWAMID.iss]]:
    for ctx in ['registration', 'discovery', 'response']:
        try:
            _sms = make_signing_sequence(seq, FEDENT, ctx, lifetime=86400)
        except Exception as err:
            print(err)
        else:
            fp = open('sms/{}/{}'.format(ctx, quote_plus(seq[-1])), 'w')
            fp.write(_sms)
            fp.close()
        clear_metadata_statements([FEDENT[SWAMID.iss], FEDENT[EDUGAIN.iss], fe])
