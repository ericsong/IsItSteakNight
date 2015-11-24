var getMatchingItems = require('./analyzer');

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

    $(document).bind("keydown", function(e) {
        if(e.keyCode == 13) {
            return false;
        }
    });

    document.getElementById('item-desc').addEventListener("input", function(e) {
        currentQuery = $('#item-desc').text()
        $('#email-query').text(currentQuery.toUpperCase());
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

                IISN_APP.removeTime = new Date().getTime() + 5000; // convert to constant
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
