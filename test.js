
collection = function(name, onSet) {
    var data = {};
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
            data = change;
            if (onSet) {
                onSet(null, data);
            }
        }
    }
    return data;
}

call = function(name, args, cb) {
    ws = new WebSocket(
            "ws://localhost:9999/"
            + name + "?"
            + _.map(args, function(arg) { return "a=" + arg; }).join("&")
    );
    ws.onmessage = function(evt) {
        if (cb) {
            cb(evt.data);
        }
    }
}

$(document).ready(function() {
    var tpl_users = Handlebars.compile($("#tpl_users").html());
    var users = collection('subscribe_all_users', function(key, value) {
        $("#users").html(tpl_users({users: _.toArray(users)}));
    });
    var tpl_console = Handlebars.compile($("#tpl_console").html());
    var methods = collection('_zerorpc_list', function(key, value) {
        $("#console").html(tpl_console({methods: value.sort()}));
        $("#console").submit(function() {
            method = $("#console .rpc_method_input").val()
            args = $("#console .rpc_arg_input").val().split(/ +/);
            $("#console .rpc_arg_input").val("");
            $("#console .rpc_result").html("");
            call(method, args, function(result) {
                $("#console .rpc_result").html(result);
            });
            return false;
        });
    });
});
