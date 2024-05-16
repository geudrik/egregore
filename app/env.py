from os import environ as env

DEVELOPMENT = env.get("DEVELOPMENT", False)
LOG_LEVEL = env.get("LOG_LEVEL", "INFO")

# If set to "json", will output logs in JSON format
LOG_OUTPUT = env.get("LOG_OUTPUT", "")

# Set up env vars for connecting to our OpenSearch cluster
OPENSEARCH_HOST = env.get("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = (
    9200 if not env.get("OPENSEARCH_PORT") else int(env.get("OPENSEARCH_PORT"))
)
OPENSEARCH_CA_PATH = env.get("OPENSEARCH_CA_PATH", None)
OPENSEARCH_USER = env.get("OPENSEARCH_USER", "admin")
OPENSEARCH_PASS = env.get("OPENSEARCH_PASS", "admin")
OPENSEARCH_INDEX_PREFIX = env.get("OPENSEARCH_INDEX_PREFIX", "egregore-")

# Controls whether we're going to be loading and subsequently unloading the index templates on startup and shutdown
#   of the app. Good for dev when things may be changing
CYCLE_INDEX_TEMPLATES = env.get("CYCLE_INDEX_TEMPLATES", False)

# On shutdown, will nuke the indexes. This requires that CYCLE_INDEX_TEMPLATES also be set to take effect
PURGE_INDEXES_ON_SHUTDOWN = env.get("PURGE_INDEXES_ON_SHUTDOWN", False)
