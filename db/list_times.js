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

Menu.find({}, function(err, docs) {
    for(var i = 0; i < docs.length; i++) {
        console.log(docs[i].time);
    }
});
