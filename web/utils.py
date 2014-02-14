from django.conf import settings
from pyatomiadns.client import AtomiaClient


def get_client(session):
    username = session.get('username')
    password = session.get('password')
    client = AtomiaClient(settings.PYATOMIADNS_JSON_URL, username, password)
    return client
