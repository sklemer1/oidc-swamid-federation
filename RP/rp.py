#!/usr/bin/env python3
import importlib
import logging
import os
import sys

import cherrypy
import requests
from fedoidcmsg.entity import make_federation_entity
from fedoidcrp import oidc
from fedoidcservice.service import factory
from cryptojwt.key_jar import init_key_jar
from oidcrp import RPHandler

logger = logging.getLogger("")
LOGFILE_NAME = 'farp.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

SIGKEY_NAME = 'sigkey.jwks'

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='tls', action='store_true')
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    folder = os.path.abspath(os.curdir)
    sys.path.insert(0, ".")
    config = importlib.import_module(args.config)
    cprp = importlib.import_module('cprp')

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
            'server.socket_port': config.PORT
        })

    provider_config = {
        '/': {
            'root_path': 'localhost',
            'log.screen': True
        },
        '/public': {
            'tools.staticdir.dir': os.path.join(folder, 'static'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'tools.staticdir.content_types': {
                'json': 'application/json',
                'jwks': 'application/json',
                'jose': 'application/jose'
            },
            'log.screen': True,
            'cors.expose_public.on': True
        }
    }

    _base_url = config.BASEURL

    _kj = init_key_jar(**config.RP_CONFIG['jwks'])

    if args.insecure:
        verify_ssl = False
    else:
        verify_ssl = True

    federation_entity = make_federation_entity(config.CLIENTS['']['federation'],
                                               httpcli=requests.request,
                                               verify_ssl=verify_ssl)

    rph = RPHandler(base_url=_base_url, hash_seed="BabyDriver", keyjar=_kj,
                    jwks_path=config.RP_CONFIG['jwks_url_path'],
                    client_configs=config.CLIENTS, service_factory=factory,
                    client_cls=oidc.RP, verify_ssl=verify_ssl,
                    federation_entity=federation_entity)

    cherrypy.tree.mount(cprp.Consumer(rph, 'html'), '/', provider_config)

    # If HTTPS
    if args.tls:
        cherrypy.server.ssl_certificate = config.SERVER_CERT
        cherrypy.server.ssl_private_key = config.SERVER_KEY
        if config.CA_BUNDLE:
            cherrypy.server.ssl_certificate_chain = config.CA_BUNDLE

    cherrypy.engine.start()
    cherrypy.engine.block()
