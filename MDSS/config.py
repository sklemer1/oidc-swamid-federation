PORT = 8089

# If PORT and not default port
BASEURL = "https://localhost:{}".format(PORT)

MS_URI_PATTERN = '{}/getsms/{{}}/{{}}/{{}}'.format(BASEURL)
ROOT_DIR = ''

SERVER_CERT = 'certs/cert.pem'
SERVER_KEY = 'certs/key.pem'
CA_BUNDLE = ''

ENTITY_ID = 'https://mdss.sunet.se'

KEYJAR_CONFIG = {
    "private_path": "private/mdss.json",
    "public_path": "public/mdss.json"
}
