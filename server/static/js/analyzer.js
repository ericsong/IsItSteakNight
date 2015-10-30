function validGenre(genre) {
    var genre_lower = genre.toLowerCase();
    if(
        genre_lower == "entrees" ||
        genre_lower == "nightly promo" ||
        genre_lower == "cook to order bar"
    ) {
        return true;
    }

    return false;
}

function miscFlags(item) {
    var item_lower = item.toLowerCase();

    if(
        item_lower.indexOf("philly") !== -1 ||
        item_lower.indexOf("tuna") !== -1 ||
        item_lower.indexOf("sandwhich") !== -1
    ) {
        return false;
    }

    return true;
}

function isSteakItem(genre, item) {
    var item_lower = item.toLowerCase();

    if(
        item_lower.indexOf("steak") !== -1 &&
        validGenre(genre) &&
        miscFlags(item)
    ) {
        return true;
    }

    return false;
}

//rename this to get steak items from menu
function checkIfMenuHasSteak(menu) {
    var hasSteak = false;
    var items = [];

    for(var i = 0; i < menu.length; i++) {
        var dininghall = menu[i];

        for(var j = 0; j < dininghall.meals.length; j++) {
            var meal = dininghall.meals[j];
            if(!meal.meal_avail) {
                break;
            }

            for(var k = 0; k < meal.genres.length; k++) {
                var genre = meal.genres[k];

                for(var l = 0; l < genre.items.length; l++) {
                    var item = genre.items[l];

                    if(isSteakItem(genre.genre_name, item)) {
                        hasSteak = true;

                        items.push({
                            dininghall: dininghall.location_name,
                            meal: meal.meal_name,
                            genre: genre.genre_name,
                            item: item  
                        })
                    } 
                }
            }
        }
    }

    return items;
}

$.get('/MenuData', function(data) {
    var menu = data.menu;

    console.log(checkIfMenuHasSteak(menu));
})
