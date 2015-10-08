var mongoose = require('mongoose');
var request = require('request');

mongoose.connect('mongodb://localhost/isitsteaknight');

var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));

var menuSchema = mongoose.Schema({
    data: Object,
    time : { type : Date, default: Date.now } 
});

var itemSchema = mongoose.Schema({
    hall: String,
    category: String,
    item: String
});

var Menu = mongoose.model('menu', menuSchema);
var Item = mongoose.model('item', itemSchema);

Menu.find(function(err, docs) {
    for(var i = 0; i < docs.length; i++) {
        for(var j = 0; j < docs[i].data.length; j++) {
            var location_name = docs[i].data[j].location_name;
            var menu = docs[i].data[j].meals

            for(let meal of menu) {
                if(meal.genres) {
                    for(let genre of meal.genres) {
                        for(let item of genre.items) {
                            Item.findOne({
                                hall: location_name,
                                category: genre.genre_name,
                                item: item
                            }, function(err, doc) {
                                console.log(doc)
                                if(!doc) {
                                    console.log(genre.genre_name + ': ' + item)
                                    var newItem = new Item({
                                        hall: location_name,
                                        category: genre.genre_name,
                                        item: item
                                    }).save()
                                } 
                            })
                        }
                    }
                }
            }

        }
    }
})
