import logging

import cherrypy

from cryptojwt.utils import as_bytes

from fedoidcmsg import MetadataStatement

from oidcop import cherryp

logger = logging.getLogger(__name__)


class OpenIDProvider(cherryp.OpenIDProvider):

    @cherrypy.expose
    def metadata(self):
        cherrypy.response.headers['Content-Type'] = 'application/jws'
        metadata_statement = MetadataStatement()
        fe = self.endpoint_context.federation_entity
        fe.add_signing_keys(metadata_statement)
        try:
            sms = fe.self_signer.sign(metadata_statement, aud=fe.fo_priority)
        except Exception as err:
            logger.exception(err)
            raise
        return as_bytes(sms)

