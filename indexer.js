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

Menu.find(function(err, docs) {
    for(var i = 0; i < docs.length; i++) {
        for(var j = 0; j < docs[i].data.length; j++) {
            var busch_menu;

            if(docs[i].data[j].location_name = 'Busch Dining Hall') {
                busch_menu = docs[i].data[j].meals;
            }

            for(let meal of busch_menu) {
                if(meal.genres) {
                    for(let genre of meal.genres) {
                        for(let item of genre.items) {
                            console.log(genre.genre_name + ': ' + item)
                        }
                    }
                }
            }
        }
    }
})
