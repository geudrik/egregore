from opensearchpy import AsyncOpenSearch

from app.env import OPENSEARCH_HOST, OPENSEARCH_PORT, OPENSEARCH_USER, OPENSEARCH_PASS, OPENSEARCH_CA_PATH

# https://github.com/opensearch-project/opensearch-py/blob/main/guides/async.md
client_args = {
    "hosts": [{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    "http_compress": True,
    "http_auth": (OPENSEARCH_USER, OPENSEARCH_PASS),
    "use_ssl": True,
    "verify_certs": False,
    "ssl_assert_hostname": False,
    "ssl_show_warn": False,
}

if OPENSEARCH_CA_PATH:
    client_args["ca_certs"] = OPENSEARCH_CA_PATH
    client_args["verify_certs"] = True

client = AsyncOpenSearch(**client_args)
