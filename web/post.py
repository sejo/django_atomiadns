from base64 import b64encode
import json
from urllib2 import HTTPError
import re
from django.conf import settings
from django.http import HttpResponse
from web.utils import get_client


def error_json(message):
    error = {
        'status': 1,
        "msg": message
    }
    return HttpResponse(json.dumps(error), content_type="application/json")


def ok_json(message):
    ok = {
        'status': 0,
        "msg": message
    }
    return HttpResponse(json.dumps(ok), content_type="application/json")


def change_record(request):
    if not request.session.has_key('logged_in'):
        return error_json("Not logged in")

    id = request.POST.get('id', None)
    zone = request.POST.get('zone', None)
    name = request.POST.get('name', None)
    field = request.POST.get('field', None)
    value = request.POST.get('value', None)

    if not id or not name or not value or not zone or not field:
        return error_json("Not enough information")

    client = get_client(request.session)
    records = json.loads(client.GetDnsRecords(zone, name))
    for record in records:
        if record['id'] == id:
            # this record needs to be changed
            record[field] = value
    try:
        client.EditDnsRecords(zone, records)
        return ok_json("Sucessfully edited the record")
    except HTTPError, e:
        return error_json(e.reason)
    except Exception, e:
        return error_json(e.message)


def add_record(request):
    if not request.session.has_key('logged_in'):
        return error_json("Not logged in")

    zone = request.POST.get('zone', None)
    name = request.POST.get('name', None)
    ttl = request.POST.get('ttl', None)
    rdata = request.POST.get('rdata', None)
    rtype = request.POST.get('type', None)

    if not zone or not name or not ttl or not rdata or not rtype:
        return error_json("Not enough information")

    client = get_client(request.session)
    records = [
        {
            "class": "IN",
            "ttl": ttl,
            "label": name,
            "rdata": rdata,
            "type": rtype
        }
    ]
    try:
        res_json = client.AddDnsRecords(zone, records)
        res = json.loads(res_json)
        if 'error_message' in res:
            return error_json(res['error_message'])

        return ok_json("Done")
    except HTTPError, e:
        return error_json(e.reason)
    except Exception, e:
        return error_json(e.message)


def remove_record(request):
    if not request.session.has_key('logged_in'):
        return error_json("Not logged in")

    zone = request.POST.get('zone', None)
    label = request.POST.get('label', None)
    id = request.POST.get('id', None)

    if not zone or not id:
        return error_json("Not enough information")

    client = get_client(request.session)

    records = json.loads(client.GetDnsRecords(zone, label))
    for record in records:
        if record['id'] == id:
            # remove this one
            try:
                res = json.loads(client.DeleteDnsRecords(zone, [record]))
                if 'error_message' in res:
                    return error_json(res['error_message'])
                return ok_json("Done")
            except HTTPError, e:
                error_json(e.reason)
            except Exception, e:
                error_json(e.message)


def remove_zone(request):
    if not request.session.has_key('logged_in'):
        return error_json("Not logged in")

    zone = request.POST.get('zone', None)
    if not zone:
        return error_json("Missing Zone information")

    client = get_client(request.session)
    try:
        client.DeleteZone(zone)
        return ok_json("Done")
    except HTTPError, e:
        return error_json(e.reason)
    except Exception, e:
        return error_json(e.message)


def add_zone(request):
    if not request.session.has_key('logged_in'):
        return error_json("Not logged in")

    zone = request.POST.get('zone', None)
    copy_from = request.POST.get('copy_from', None)

    if not zone:
        return error_json("cannot add an empty zone")

    client = get_client(request.session)
    if not copy_from:
        # get our defaults
        try:
            client.AddZone(zone, 3600, settings.ATOMIADNS_DEFAULT_NAMESERVERS[0],
                           settings.ATOMIADNS_DEFAULT_SOA_EMAIL, 10800, 3600, 604800, 86400,
                           ["%s." % ns for ns in settings.ATOMIADNS_DEFAULT_NAMESERVERS], "default")
            return ok_json("Done")
        except HTTPError, e:
            return error_json(e.reason)
        except Exception, e:
            return error_json(e.message)

    try:
        records = json.loads(client.GetZone(copy_from))
    except HTTPError, e:
        return error_json(e.reason)

    # first add the zone
    for record in records:
        if record['name'] == '@':
            ns = list()
            for rec in record['records']:
                if rec['type'] == 'SOA':
                    soa = rec['rdata']
                    soa_ttl = rec['ttl']
                elif rec['type'] == 'NS':
                    ns.append(rec['rdata'])

    parsed_soa = soa.split(' ')
    try:
        client.AddZone(zone, soa_ttl, parsed_soa[0], parsed_soa[1], parsed_soa[3], parsed_soa[4], parsed_soa[5],
                       parsed_soa[6], ns, 'default')
    except HTTPError, e:
        return error_json("Could not add zone due to %s" % e.reason)
    try:
        new_records = list()
        for record in records:
            if record['name'] == '@':
                continue
            else:
                for rec in record['records']:
                    new_rec = dict()
                    new_rec['label'] = record['name']
                    for name in ('ttl', 'rdata', 'class', 'type'):
                        new_rec[name] = rec[name]
                    new_records.append(new_rec)
        res = client.AddDnsRecords(zone, new_records)
        return ok_json('Done')
    except HTTPError, e:
        client.DeleteZone(zone)
        return error_json("Could not add copy due to problem with record copy: %s" % e.reason)
    except Exception, e:
        client.DeleteZone(zone)
        return error_json("Could not add copy due to problem with record copy: %s" % e.reason)


def import_zone(request):
    if not request.session.has_key('logged_in'):
        return error_json("Not logged in")

    zone = request.POST.get('zone', None)
    if not zone:
        return error_json("Missing Zone information")

    data = request.POST.get('data', None)
    if not data:
        return error_json('Incorrect data')

    import_type = request.POST.get('import_type')
    if not import_type or import_type not in ('atomia', 'bind'):
        return error_json('Incorrect import_type')

    client = get_client(request.session)
    if import_type == "atomia":
        try:
            data = re.sub("^\s+", "", data)
            res = json.loads(client.RestoreZoneBinary(zone, "default", data))
            if 'error_message' in res:
                return error_json(res['error_message'])
            return ok_json("Done")
        except HTTPError, e:
            return error_json(e.reason)
        except Exception, e:
            return error_json(e.message)
    else:
        at_zone = json.loads(client.GetDnsRecords(zone, "@"))
        regex = r"^\s*(?P<label>[^\s]+)\s+(?P<ttl>[^\s]+)\s+(?P<class>[^\s]+)\s+(?P<type>[^\s]+)\s+(?P<rdata>.*)$"
        new_data = list()
        soa_lines_changed = list()
        for line in data.splitlines():
            match = re.match(regex, line)
            group_dict = match.groupdict()
            if group_dict['label'] == '@':
                #replace the @ records
                for record in at_zone:
                    if len(at_zone) == len(soa_lines_changed) or group_dict['type'] not in ("NS", "SOA"):
                        new_record = dict()
                        new_record['label'] = '@'
                        new_record['rdata'] = group_dict['rdata']
                        new_record['class'] = group_dict['class']
                        new_record['ttl'] = group_dict['ttl']
                        new_record['type'] = group_dict['type']
                        new_data.append(new_record)
                        break
                    else:
                        if record['id'] in soa_lines_changed:
                            continue
                        if group_dict['type'] == record['type']:
                            # we got a match
                            record['rdata'] = group_dict['rdata']
                            record['class'] = group_dict['class']
                            record['ttl'] = group_dict['ttl']
                            record['type'] = group_dict['type']
                            soa_lines_changed.append(record['id'])
                            break
            else:
                new_record = dict()
                new_record['label'] = group_dict['label']
                new_record['rdata'] = group_dict['rdata']
                new_record['class'] = group_dict['class']
                new_record['ttl'] = group_dict['ttl']
                new_record['type'] = group_dict['type']
                new_data.append(new_record)

        if soa_lines_changed:
            try:
                res = json.loads(client.EditDnsRecords(zone, at_zone))
                if 'error_message' in res:
                    return error_json(res['error_message'])
            except HTTPError, e:
                return error_json("Cannot change @ records %s" % e.reason)
            except Exception, e:
                return error_json("Cannot change @ records %s" % e.message)

        try:
            res = json.loads(client.AddDnsRecords(zone, new_data))
            if 'error_message' in res:
                return error_json(res['error_message'])
            return ok_json("Done")
        except HTTPError, e:
            return error_json(e.reason)
        except Exception, e:
            return error_json(e.message)

