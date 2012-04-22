
collection = function(name, onSet) {
    data = {};
    ws = new WebSocket("ws://localhost:9999/" + name);
    ws.onmessage = function(evt) {
        var change = JSON.parse(evt.data);
        if (change[0] == "set") {
            var id = change[1];
            var doc = change[2];
            doc._id = id;
            data[id] = doc;
            if (onSet) {
                onSet(id, doc);
            }
        }
        else {
            data = evt.data;
            if (onSet) {
                onSet(null, data);
            }
        }
    }
    return data;
}


$(document).ready(function() {
    var tpl_users = Handlebars.compile($("#tpl_users").html());
    var users = collection('get_all_users', function(key, value) {
        $("#users").html(tpl_users({users: _.toArray(users)}));
    });
    /*
    var tpl_console = Handlebars.compile($("#tpl_console").html());
    var methods = collection('_zerorpc_list', function(key, value) {
        $("#console").html(tpl_console({methods: value}))
    });
    */
});
