var mongoose = require('mongoose');
var request = require('request');

mongoose.connect('mongodb://localhost/isitsteaknight');

var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));

var menuSchema = mongoose.Schema({
    data: Object
});

var Menu = mongoose.model('menu', menuSchema);

request('https://rumobile.rutgers.edu/1/rutgers-dining.txt', function(error, response, body) {
    var newMenu = new Menu({data: JSON.parse(body)});

    newMenu.save()
});
