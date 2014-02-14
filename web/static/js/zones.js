/**
 * Created by sejo on 2/15/14.
 */


function add_zone() {
    var zone = $('input[name=zone]').val();
    var copy_from = $('input[name=copy_from]').val();
    var result = send_json(
        '/ajax/add_zone',
        {
            zone: zone,
            copy_from: copy_from
        }
    );
    if (result.status == 0) {
        location.href = '/edit/' + zone;
    } else {
        $.bootstrapGrowl(result.msg,
            {
                type: 'danger',
                delay: 10000,
                allow_dismiss: true
            });
    }
}

function remove_zone(zone) {
    var result = send_json(
        '/ajax/remove_zone',
        {
            zone: zone
        }
    );
    if (result.status == 0) {
        location.reload();
    } else {
        $.bootstrapGrowl(result.msg,
            {
                type: "danger",
                delay: 10000,
                allow_dismiss: true
            })
    }
}

function import_zone(zone) {
    var import_type = $('select[name=import_type] :selected').val();
    var data = $('textarea').val();
    var result = send_json(
        '/ajax/import_zone',
        {
            zone: zone,
            data: data,
            import_type: import_type
        }
    );
    if (result.status == 0) {
        location.href = '/edit/' + zone;
    } else {
        $.bootstrapGrowl(result.msg,
            {
                type: "danger",
                delay: 10000,
                allow_dismiss: true
            });
    }
}

function remove_record(id) {
    var label = $('tr#' + id + ' input[name=name]').val();
    var zone = $('input[name=zone]').val();
    var result = send_json(
        '/ajax/remove_record/',
        {
            id: id,
            zone: zone,
            label: label
        }
    );
    if (result.status == 0) {
        location.reload();
    } else {
        $.bootstrapGrowl(result.msg,
            {
                type: "danger",
                delay: 10000,
                allow_dismiss: true
            });
    }
}
function add_record(id) {
    var name = $('tr#' + id + ' input[name=name]').val();
    var type = $('tr#' + id + ' input[name=type]').val();
    var ttl = $('tr#' + id + ' input[name=ttl]').val();
    var rdata = $('tr#' + id + ' input[name=rdata]').val();
    var zone = $('input[name=zone]').val();

    var result = send_json(
        '/ajax/add_record/',
        {
            name: name,
            type: type,
            rdata: rdata,
            ttl: ttl,
            zone: zone
        }
    );
    if (result.status == 0) {
        location.reload();
    } else {
        $.bootstrapGrowl(result.msg,
            {
                type: "danger",
                delay: 10000,
                allow_dismiss: true
            });

    }
}

function change_record(id, field) {
    var val = $('tr#' + id + ' input[name=' + field + ']').val();
    var zone = $('input[name=zone]').val();
    var name = $('tr#' + id + ' input[name=name]').val();
    var result = send_json(
        '/ajax/change_record/',
        {
            id: id,
            name: name,
            value: val,
            zone: zone,
            field: field
        }
    );
    if (result.status == 0) {
        $.bootstrapGrowl(result.msg,
            {
                type: "success",
                delay: 10000,
                allow_dismiss: true
            }

        );
    } else {
        $.bootstrapGrowl(result.msg,
            {
                type: "danger",
                delay: 10000,
                allow_dismiss: true
            }

        );
    }

}