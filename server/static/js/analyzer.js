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
        item_lower.indexOf("philly") > 0 ||
        item_lower.indexOf("tuna") > 0 ||
        item_lower.indexOf("sandwhich") > 0
    ) {
        return false;
    }

    return true;
}

function isSteakItem(genre, item) {
    var item_lower = item.toLowerCase();

    if(
        item_lower.indexOf("steakk") > 0 &&
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

    for(var dininghall of menu) {
        for(var meal of dininghall.meals) {
            if(!meal.meal_avail) {
                return items;
            }

            for(var genre of meal.genres) {
                for(var item of genre.items) {
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
