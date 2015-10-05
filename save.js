var mongoose = require('mongoose');
var request = require('request');

mongoose.connect('mongodb://localhost/isitsteaknight');

var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));

var menuSchema = mongoose.Schema({
    data: Object,
    time : { type : Date, default: Date.now } 
});

var Menu = mongoose.model('menu', menuSchema);

request('https://rumobile.rutgers.edu/1/rutgers-dining.txt', function(error, response, body) {
    var menudata = JSON.parse(body);
    Menu.findOne({}, {}, {sort: {'time': -1} }, function(err, doc) {
        if(!doc) {
            var newMenu = new Menu({data: JSON.parse(body)});

            newMenu.save()
            console.log('saved menu');
            return;
        }

        var isSame = true;

        for(var i = 0; i < doc.data.length; i++) {
            var hall = doc.data[i].location_name;
            var time = doc.data[i].date;

            for(var j = 0; j < menudata.length; j++) {
                if(menudata[j].location_name == hall) {
                    if(time != menudata[j].date) {
                        isSame = false;
                    }
                }
            }
        }

        if(!isSame) {
            var newMenu = new Menu({data: JSON.parse(body)});

            newMenu.save()
            console.log('saved menu');
        }
    })
});
