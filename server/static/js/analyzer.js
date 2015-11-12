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
        item_lower.indexOf("sandwich") !== -1
    ) {
        return false;
    }

    return true;
}

function isMatchingItem(genre, item, query) {
    var item_lower = item.toLowerCase();
    var query_lower = query.toLowerCase();

    if(query_lower === "steak") {
        if(
            item_lower.indexOf(query_lower) !== -1 &&
            validGenre(genre) &&
            miscFlags(item)
        ) {
            return true;
        }
    } else {
        if(item_lower.indexOf(query_lower) !== -1) {
            return true;
        }
    }

    return false;
}

//rename this to get steak items from menu
function getMatchingItems(menu, query) {
    var hasSteak = false;
    var items = [];

    for(var i = 0; i < menu.length; i++) {
        var dininghall = menu[i];

        for(var j = 0; j < dininghall.meals.length; j++) {
            var meal = dininghall.meals[j];
            if(!meal.meal_avail) {
                continue;
            }

            for(var k = 0; k < meal.genres.length; k++) {
                var genre = meal.genres[k];

                for(var l = 0; l < genre.items.length; l++) {
                    var item = genre.items[l];

                    if(isMatchingItem(genre.genre_name, item, query)) {
                        hasSteak = true;

                        items.push({
                            dininghall: dininghall.location_name,
                            meal: meal.meal_name,
                            genre: genre.genre_name,
                            item: item,
                            query: query
                        })
                    } 
                }
            }
        }
    }

    return items;
}

module.exports = getMatchingItems;
