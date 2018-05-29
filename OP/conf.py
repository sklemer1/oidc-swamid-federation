from fedoidcendpoint.oidc import provider_config
from fedoidcendpoint.oidc import registration

from oidcendpoint import user_info
from oidcendpoint.oidc.authorization import Authorization
from oidcendpoint.oidc.discovery import Discovery
from oidcendpoint.oidc.token import AccessToken
from oidcendpoint.oidc.userinfo import UserInfo
from oidcendpoint.user_authn.authn_context import INTERNETPROTOCOLPASSWORD

from oidcop.util import JSONDictDB

KEYDEFS = [{"type": "RSA", "key": '', "use": ["sig"]},
           {"type": "EC", "crv": "P-256", "use": ["sig"]}]

FED_KEYDEF = [{"type": "EC", "crv": "P-256", "use": ["sig"]}]

RESPONSE_TYPES_SUPPORTED = [
    ["code"], ["token"], ["id_token"], ["code", "token"], ["code", "id_token"],
    ["id_token", "token"], ["code", "token", "id_token"], ['none']]

CAPABILITIES = {
    "response_types_supported": [" ".join(x) for x in RESPONSE_TYPES_SUPPORTED],
    "token_endpoint_auth_methods_supported": [
        "client_secret_post", "client_secret_basic",
        "client_secret_jwt", "private_key_jwt"],
    "response_modes_supported": ['query', 'fragment', 'form_post'],
    "subject_types_supported": ["public", "pairwise"],
    "grant_types_supported": [
        "authorization_code", "implicit",
        "urn:ietf:params:oauth:grant-type:jwt-bearer", "refresh_token"],
    "claim_types_supported": ["normal", "aggregated", "distributed"],
    "claims_parameter_supported": True,
    "request_parameter_supported": True,
    "request_uri_parameter_supported": True,
}

CONFIG = {
    'provider': {
        'jwks': {
            'private_path': 'private/jwks.json',
            'key_defs': KEYDEFS,
            'public_path': 'public/jwks.json'
        },
        'server_info': {
            "issuer": "https://127.0.0.1:8100",
            "password": "mycket hemligt",
            "token_expires_in": 600,
            "grant_expires_in": 300,
            "refresh_token_expires_in": 86400,
            "verify_ssl": False,
            "capabilities": CAPABILITIES,
            'template_dir': 'templates',
            "jwks": {
                'url_path': '{}/public/jwks.json',
                'local_path': 'public/jwks.json',
                'private_path': 'private/jwks.json'
            },
            'endpoint': {
                'webfinger': {
                    'path': '{}/.well-known/webfinger',
                    'class': Discovery,
                    'kwargs': {'client_authn_method': None}
                },
                'provider_info': {
                    'path': '{}/.well-known/openid-configuration',
                    'class': provider_config.ProviderConfiguration,
                    'kwargs': {'client_authn_method': None}
                },
                'registration': {
                    'path': '{}/registration',
                    'class': registration.Registration,
                    'kwargs': {'client_authn_method': None}
                },
                'authorization': {
                    'path': '{}/authorization',
                    'class': Authorization,
                    'kwargs': {'client_authn_method': None}
                },
                'token': {
                    'path': '{}/token',
                    'class': AccessToken,
                    'kwargs': {}
                },
                'userinfo': {
                    'path': '{}/userinfo',
                    'class': UserInfo,
                }
            },
            'userinfo': {
                'class': user_info.UserInfo,
                'kwargs': {'db_file': 'users.json'}
            },
            'authentication': [
                {
                    'acr': INTERNETPROTOCOLPASSWORD,
                    'name': 'UserPassJinja2',
                    'kwargs': {
                        'template': 'user_pass.jinja2',
                        'db': {
                            'class': JSONDictDB,
                            'kwargs':
                                {'json_path': 'passwd.json'}
                        },
                        'page_header': "Testing log in",
                        'submit_btn': "Get me in!",
                        'user_label': "Nickname",
                        'passwd_label': "Secret sauce"
                    }
                },
                {
                    'acr': 'anon',
                    'name': 'NoAuthn',
                    'kwargs': {'user': 'diana'}
                }
            ],
            'federation': {
                'self_signer': {
                    'private_path': 'private/sign.json',
                    'key_defs': FED_KEYDEF,
                    'public_path': 'public/sign.json'
                },
                'mdss_endpoint': 'https://localhost:8089',
                'mdss_owner': 'https://mdss.sunet.se',
                'mdss_keys': 'mdss.jwks',
                'fo_bundle': {
                    'dir': '../fo_bundle',
                },
                'context': 'dynamic',
                'fo_priority': ['https://edugain.org',
                                'https://swamid.sunet.se']
            }
        }
    },
    'webserver': {
        'cert': 'certs/cert.pem',
        'key': 'certs/key.pem',
        'cert_chain': '',
        'port': 8100,
    }
}
