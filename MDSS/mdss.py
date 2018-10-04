#!/usr/bin/env python3
import importlib
import logging
import os
import sys
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

import cherrypy
from cryptojwt.utils import as_bytes
from cryptojwt.jwt import JWT
from cryptojwt.key_jar import init_key_jar

logger = logging.getLogger(__name__)


def get_sign_alg(keyjar, iss=''):
    """
    Based on the keys in a keyjar and a order of priority
    between key types pick the 'best' signing algorithm.

    :param keyjar: A :py:class`oidcmsg.key_jar.KeyJar` instance
    :param iss: An identifier for an issuer
    :return: The name of a signing algorithm
    """
    priority_order = ['EC', 'RSA', 'OCT']
    po_inv = {'EC': 'ES256', 'RSA': 'RS256', 'OCT': 'HS256'}

    best = len(priority_order) - 1
    for key in keyjar.get_signing_key(owner=iss):
        if priority_order.index(key.kty) < best:
            best = priority_order.index(key.kty)

    return po_inv[priority_order[best]]


def handle_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [
        b"<html><body>Sorry, an error occured</body></html>"
    ]


class Consumer(object):
    _cp_config = {'request.error_response': handle_error}

    def __init__(self, ms_uri_pattern, key_jar, root_dir='', entity_id=''):
        self.ms_uri_pattern = ms_uri_pattern
        self.key_jar = key_jar
        self.root_dir = root_dir
        self.entity_id = entity_id

    @cherrypy.expose
    def index(self):
        return b'OK'

    @cherrypy.expose
    def getsmscol(self, context, entity_id):
        """
        {
            "https://swamid.sunet.se/": "https://mdss.sunet.se/getsms/https%3A%2F%2Frp.example.com
                %2Fms.jws/https%3A%2F%2Fswamid.sunet.se%2F"
        }
        :param context: The context in which the signed metadata statement is
            to be used.
        :param entity_id: The identifier of the entity
        :return: A signed JWT containing a collection of signed metadata
            statements
        """
        smscol = {}
        qp_eid = quote_plus(entity_id)
        _top_dir = os.path.join(self.root_dir, context, 'out')
        for _fo in os.listdir(_top_dir):
            if os.path.isfile(os.path.join(_top_dir, _fo, qp_eid)):
                smscol[unquote_plus(_fo)] = self.ms_uri_pattern.format(context,
                                                                       qp_eid,
                                                                       _fo)

        sig_alg = get_sign_alg(self.key_jar, '')
        # Create signed JWT
        _jwt = JWT(self.key_jar, iss=self.entity_id, sign_alg=sig_alg)
        _jws = _jwt.pack(payload=smscol)
        return as_bytes(_jws)

    @cherrypy.expose
    def getsms(self, context, entity_id, fo):
        """
        GET */getsms/{context}/{entityID}/{FO}*

        :param context: The context in which the signed metadata statement is
            to be used.
        :param entity_id: The identifier of the entity
        :param fo: The identifier of the federation operator
        :return: A signed metadata statement
        """
        _fname = os.path.join(self.root_dir, context, 'out', quote_plus(fo),
                              quote_plus(entity_id))
        if os.path.isfile(_fname):
            return as_bytes(open(_fname).read())

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if vpath[0] == 'getsmscol':
            if len(vpath) != 3:
                return cherrypy.HTTPError(message='Incorrect path')
            vpath.pop(0)
            cherrypy.request.params['context'] = vpath.pop(0)
            cherrypy.request.params['entity_id'] = vpath.pop(0)
            return self.getsmscol
        elif vpath[0] == 'getsms':
            if len(vpath) != 4:
                return cherrypy.HTTPError(message='Incorrect path')
            vpath.pop(0)
            cherrypy.request.params['context'] = vpath.pop(0)
            cherrypy.request.params['entity_id'] = vpath.pop(0)
            cherrypy.request.params['fo'] = vpath.pop(0)
        else:
            return cherrypy.HTTPError(402, 'Unknown page')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tls', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    folder = os.path.abspath(os.curdir)
    sys.path.insert(0, ".")
    config = importlib.import_module(args.config)
    try:
        _port = config.PORT
    except AttributeError:
        if args.tls:
            _port = 443
        else:
            _port = 80

    cherrypy.config.update(
        {
            'environment': 'production',
            'log.error_file': 'error.log',
            'log.access_file': 'access.log',
            'tools.trailing_slash.on': False,
            'server.socket_host': '0.0.0.0',
            'log.screen': True,
            'tools.sessions.on': True,
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8',
            'server.socket_port': _port
        })

    provider_config = {
        '/': {
            'root_path': 'localhost',
            'log.screen': True
        }
    }

    _key_jar = init_key_jar(**config.KEYJAR_CONFIG)
    cherrypy.tree.mount(Consumer(config.MS_URI_PATTERN, _key_jar,
                                 config.ROOT_DIR,config.ENTITY_ID),
                        '/', provider_config)

    # If HTTPS
    if args.tls:
        cherrypy.server.ssl_certificate = config.SERVER_CERT
        cherrypy.server.ssl_private_key = config.SERVER_KEY
        if config.CA_BUNDLE:
            cherrypy.server.ssl_certificate_chain = config.CA_BUNDLE

    cherrypy.engine.start()
    cherrypy.engine.block()
