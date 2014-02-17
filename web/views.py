import json
from urllib2 import HTTPError
from django.contrib.auth.views import logout
import re
from django.conf import settings
from django.shortcuts import render, render_to_response
from pyatomiadns.client import AtomiaClient

# Create your views here.
from django.template import RequestContext
from web.utils import get_client


def home(request, offset=0):
    if request.session.has_key('logged_in'):
        offset = int(offset) if offset else 0
        username = request.session.get('username')
        password = request.session.get('password')
        client = get_client(request.session)
        zones = json.loads(client.FindZones(username, "%", settings.PAGINATION_OFFSET, offset))
        if 'error_message' in zones:
            return render_to_response('error.html',
                                      {
                                          "error_message": zones['error_message']
                                      },
                                      context_instance=RequestContext(request))
        next = False
        if int(zones.get('total')) > offset + settings.PAGINATION_OFFSET:
            next = True
        return render_to_response("main.html",
                                  {
                                      "zones": zones,
                                      "offset": offset,
                                      "next": next,
                                      "next_offset": offset + settings.PAGINATION_OFFSET,
                                      "prev_offset": offset - settings.PAGINATION_OFFSET,
                                  },
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('login.html', context_instance=RequestContext(request))


def login(request):
    if not request.POST:
        return render_to_response("error.html",
                                  {"message": "Only POST allowed for login"},
                                  context_instance=RequestContext(request))
    username = request.POST.get("username")
    password = request.POST.get("password")

    if not username or not password:
        return home(request)

    client = AtomiaClient(settings.PYATOMIADNS_JSON_URL, username, password)
    zones = None
    try:
        client.Noop()
        request.session['username'] = username
        request.session['password'] = password
        request.session['logged_in'] = True
        s_zones = client.FindZones(username, "%", 25, 0)
        zones = json.loads(s_zones)
        return home(request)
    except HTTPError, e:
        if request.session.has_key('username'):
            del request.session['username']
        if request.session.has_key('password'):
            del request.session['password']
        if request.session.has_key('logged_in'):
            del request.session['logged_in']

        return render_to_response("error.html",
                                  {
                                      "error_message": "Code: %s, message: %s" % (e.code, e.reason)
                                  },
                                  context_instance=RequestContext(request))


def edit(request, zone):
    if not request.session.has_key('logged_in'):
        return home(request)

    username = request.session.get('username')
    password = request.session.get('password')
    client = AtomiaClient(settings.PYATOMIADNS_JSON_URL, username, password)
    records = json.loads(client.GetZone(zone))
    return render_to_response('edit.html',
                              {
                                  "zone": zone,
                                  "records": records
                              }, context_instance=RequestContext(request))


def export(request, zone):
    if not request.session.has_key("logged_in"):
        return home(request)

    if not zone:
        return render_to_response('error.html',
                                  {
                                      "error_message": "Cannot proceed without zone information"
                                  },
                                  context_instance=RequestContext(request)
        )

    client = get_client(request.session)
    data = json.loads(client.GetZoneBinary(zone))

    bind_data = list()
    regex = r"(?P<label>[^\s]+)\s+(?P<class>[^\s]+)\s+(?P<ttl>[^\s]+)\s+(?P<type>[^\s]+)\s+(?P<rdata>.*)"
    for line in data.splitlines():
        match = re.match(regex, line)
        group_dict = match.groupdict()
        bind_data.append("%s %s %s %s %s" % ( group_dict['label'],
                                              group_dict['ttl'],
                                              group_dict['class'],
                                              group_dict['type'],
                                              group_dict['rdata']))

    return render_to_response('export.html',
                              {
                                  "data": data,
                                  "zone": zone,
                                  "bind_data": "\n".join(bind_data)
                              },
                              context_instance=RequestContext(request)
    )


def import_zone(request, zone):
    if not request.session.has_key("logged_in"):
        return home(request)

    if not zone:
        return render_to_response('error.html',
                                  {
                                      "error_message": "Cannot proceed without zone information"
                                  },
                                  context_instance=RequestContext(request)
        )
    return render_to_response("import.html",
                              {
                                  "zone": zone
                              },
                              context_instance=RequestContext(request))


def change_password(request):
    if request.method == 'GET':
        return render_to_response("change_password.html", {}, context_instance=RequestContext(request))

    if not request.session.has_key("logged_in"):
        return home(request)

    old_password = request.POST.get('old_pass', None)
    password = request.POST.get('pass', None)
    conf_password = request.POST.get('conf_pass', None)

    if old_password != request.session.get('password'):
        return render_to_response("error.html",
                                  {
                                      "error_message": "Incorrect old password!"
                                  },
                                  context_instance=RequestContext(request))

    if password == conf_password:
        client = get_client(request.session)
        res = json.loads(client.EditAccount(request.session.get('username'), password))

        if "error_message" in res:
            return render_to_response("error.html",
                                      {
                                          "error_message": "Server error while changing password."
                                      },
                                      context_instance=RequestContext(request))
        return logout(request, next_page='/')
    else:
        return render_to_response("error.html",
                                  {
                                      "error_message": "Password and confirmation do not match."
                                  },
                                  context_instance=RequestContext(request))
