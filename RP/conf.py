PORT = 8080

# BASE = "https://lingon.ladok.umu.se"
BASEURL = "https://localhost:{}".format(PORT)

# If BASE is https these has to be specified
SERVER_CERT = "certs/cert.pem"
SERVER_KEY = "certs/key.pem"
CA_BUNDLE = None

VERIFY_SSL = False

FED_KEYDEF = [{"type": "RSA", "key": '', "use": ["sig"]}]

OIDC_KEYDEF = [{"type": "RSA", "key": '', "use": ["sig"]},
               {"type": "EC", "crv": "P-256", "use": ["sig"]}]

RP_CONFIG = {
    'jwks': {
        'private_path': 'private/jwks.json',
        'key_defs': OIDC_KEYDEF,
        'public_path': 'public/jwks.json'
    },
    'jwks_url_path': '{}/public/jwks.json'.format(BASEURL)
}

client_config = {
    'base_url': BASEURL,
    'client_preferences': {
        "application_type": "web", "application_name": "rphandler",
        "contacts": ["ops@example.com"],
        "response_types": ["code", "id_token", "id_token token",
                           "code id_token", "code id_token token",
                           "code token"],
        "scope": ["openid", "profile", "email", "address", "phone"],
        "token_endpoint_auth_method": "client_secret_basic"
    },
    'services': {
        'FedProviderInfoDiscovery': {}, 'FedRegistrationRequest': {},
        'Authorization': {}, 'AccessToken': {}, 'WebFinger': {},
        'RefreshAccessToken': {}, 'UserInfo': {}
    },
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
        'context': 'registration',
        'entity_id': '{}/metadata'.format(BASEURL),
        'fo_priority': ['https://edugain.org', 'https://swamid.sunet.se']
    }
}

# The keys in this dictionary are the OPs short user friendly name
# not the issuer (iss) name.
# The special key '' is used for OPs that support dynamic interactions.

CLIENTS = {
    # The ones that support webfinger, OP discovery and client registration
    # This is the default, any client that is not listed here is expected to
    # support dynamic discovery and registration.
    "": client_config,
}
