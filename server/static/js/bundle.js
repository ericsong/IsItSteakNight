(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
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

},{}],2:[function(require,module,exports){
var getMatchingItems = require('./analyzer');

var MESSAGE_DURATION = 1500;

var IISN_APP = {}

function shake(div) {
    var interval = 100;
    var distance = 5;
    var times = 2;

    $(div).css('position', 'relative');

    for(var i = 0; i < times+1; i++) {
        $(div).animate({ left: ((i%2==0 ? distance : distance*-1))}, interval);
    }

    $(div).animate({ left: 0}, interval);
}      

$(document).ready(function() {
    var menu = null;
    var currentQuery = "steak";

    setInterval(function() {
        var currentTime = new Date().getTime();
        if(currentTime > IISN_APP.removeTime) {
            $('#submit-message').text('');
        }
    }, 500)

    $('#item-desc').bind("keydown", function(e) {
        if(e.keyCode == 13) {
            return false;
        }
    });

    document.getElementById('item-desc').addEventListener("input", function(e) {
        currentQuery = $('#item-desc').text();
        $('.email-query').each(function() {
            $(this).text(currentQuery.toUpperCase())
        });
        setNewItems(currentQuery);
    });

    $('form').submit(function(e) {
        $.ajax({
            url: '/subscribe',
            method: 'POST',
            data: {
                email:  $('#email-input').val(),
                query: currentQuery
            },
            success: function(data) {
                var messageDiv = $('#submit-message');
                var currentMessage = messageDiv.text();

                messageDiv.text(data.message);
                if(currentMessage === data.message) {
                    shake(messageDiv);
                }

                if(data.status === "success") {
                    messageDiv.removeClass().addClass('success');
                } else if(data.status === "failure"){
                    messageDiv.removeClass().addClass('failure');
                }

                IISN_APP.removeTime = new Date().getTime() + data.time*MESSAGE_DURATION;
            }
        });

        return false;
    });

    $('#item-desc').focus();

    $.get('/MenuData', function(data) {
        menu = data.menu;

        setNewItems("steak");
    });

    function setNewItems(query) {
        if(!menu) {
            console.log('menu not downloaded yet');
            return false;
        }

        var items = getMatchingItems(menu, query);
        var container = $($('.items-container')[0]);
        container.empty();

        for(var i = 0; i < items.length; i++) {
            var item = items[i];

            var outputText = item.dininghall + " is serving ... <span>" + item.item +
                             "</span> (" + item.genre + ") for " + item.meal;
            container.append($("<h3></h3").html(outputText));     
        }

        if(items.length == 0) {
            $($('.isSteakNight')[0]).text("\xa0NO\xa0");
            var emojis = $('.emoji');
            for(var i = 0; i < emojis.length; i++) {
                $(emojis[i]).attr('src', '/media/crying-face.png');
            }
        } else {
            $($('.isSteakNight')[0]).text("\xa0YES\xa0");
            var emojis = $('.emoji');
            for(var i = 0; i < emojis.length; i++) {
                $(emojis[i]).attr('src', '/media/fire.png');
            }
        }
    }
});

},{"./analyzer":1}]},{},[2]);
