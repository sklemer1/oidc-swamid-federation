#!/usr/bin/env python3
import json
import os
from urllib.parse import quote_plus

EM = 'entity_metadata'
PR = 'process_rules'

for _name in os.listdir(EM):
    fname = os.path.join(EM, _name)
    metadata = json.loads(open(fname).read())
    rule_file = os.path.join(PR, _name)
    if os.path.isfile(rule_file):
        _rule = json.loads(open(rule_file).read())

        for context, spec in _rule.items():
            for fo, data in spec.items():
                qfo = quote_plus(fo)
                mc = metadata.copy()
                mc.update(data)
                _dir = os.path.join(context, 'in', qfo)
                if not os.path.isdir(_dir):
                    os.makedirs(_dir)
                _fn = os.path.join(_dir, _name)
                fp = open(_fn, 'w')
                fp.write(json.dumps(mc))
                fp.close()
