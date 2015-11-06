var getMatchingItems = require('./analyzer');

$(document).ready(function() {
    var menu = null;
    var currentQuery = "steak";

    $("#item-desc").keypress(
        function(e){
            if(e.which == 13) {
                currentQuery = $('#item-desc').text();
                $('#email-query').text(currentQuery.toUpperCase());
                setNewItems(currentQuery);

                return false;
            } else {
                return true;
            }
        }
    );

    $('form').submit(function(e) {
        $.ajax({
            url: '/subscribe',
            method: 'POST',
            data: {
                email:  $('#email-input').val(),
                query: currentQuery
            },
            success: function(data) {
                $('#submit-message').text(data.message);
                if(data.status === "success") {
                    $('#submit-message').removeClass().addClass('success');
                } else if(data.status === "failure"){
                    $('#submit-message').removeClass().addClass('failure');
                }
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
