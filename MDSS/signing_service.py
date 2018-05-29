#!/usr/bin/env python3

# Go through one directory structure, pick up each metadata statement.
# Add metadata statements from superiors, sign it and place it in the other
# directory structure.

# in/[FO]/[entity_id]
import json
import os

from urllib.parse import unquote

from atomicwrites import atomic_write
from fedoidcmsg import MetadataStatement
from fedoidcmsg.entity import make_federation_entity


def process(incoming, outgoing, fe):
    for fo in os.listdir(incoming):
        _dir = os.path.join(incoming, fo)
        fed = unquote(fo)
        if os.path.isdir(_dir):
            for entity_id in os.listdir(_dir):
                _fname = os.path.join(_dir, entity_id)
                if os.path.isfile(_fname):
                    _ms = MetadataStatement().from_json(open(_fname).read())
                    fe.add_sms_spec_to_request(_ms, federation=fed, context=ctx)
                    sms = fe.self_signer.sign(_ms, iss=fe.entity_id)

                    _out_dir = os.path.join(outgoing, fo)
                    if not os.path.isdir(_out_dir):
                        os.makedirs(_out_dir)
                    out = os.path.join(outgoing, fo, entity_id)

                    with atomic_write(out, overwrite=True) as f:
                        f.write(sms)


if __name__ == '__main__':
    conf = json.loads(open('mdss_conf.json').read())
    federation_entity = make_federation_entity(config=conf,
                                               eid=conf['entity_id'])

    for ctx in ['registration', 'discovery', 'response']:
        _in = '{}/in'.format(ctx)
        if not os.path.isdir(_in):
            continue

        _out = '{}/out'.format(ctx)
        process(_in, _out, federation_entity)
