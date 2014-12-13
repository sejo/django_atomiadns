# django_atomiadns

A webapp written for atomiadns.
The webapp is run as your normal django project (I use gunicorn).

Change following settings according to your setup:

In django_atomiadns.settings

SECRET_KEY --> Seriously change that one!
DEBUG --> set to true unless you want it not to be :P
PYATOMIADNS_JSON_URL = 'https://dns.sejo-it.be/atomiadns.json'
ATOMIADNS_DEFAULT_NAMESERVERS = ['dns1.sejo-it.be', 'dns2.sejo-it.be', 'dns3.sejo-it.be']
ATOMIADNS_DEFAULT_SOA_EMAIL = 'jochen.sejo-it.be'
PAGINATION_OFFSET = 10
STATIC_ROOT=/path/to/static_root


Features available:

* list/add/delete zone
* import zone (atomiadns or bind format)
* list/add/delete/modify records

Have fun!

License: None, use as pleased!