import Client from 'pg-native'
import request from 'request'
import Sendgrid from 'sendgrid'
import getMatchingItems from '../server/static/js/analyzer'

var client = new Client()
client.connectSync('postgresql://iisn_admin:abc123@localhost:5432/isitsteaknight')

var sendgrid = Sendgrid(process.env.SG_USER, process.env.SG_KEY)

var cache = {}

function bold(str) {
    return "<b>" + str + "</b>"
}

function color(str) {
    return '<span style="color: #C21400;">' + str + "</span>"
}

String.prototype.capitalize = function() {
      return this.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
};

function cacheMatch(menu, query) {
    query = query.toLowerCase()

    if(cache.query) {
        return cache.query
    } else {
        let matches = getMatchingItems(menu, query)
        cache[query] = matches

        return matches
    }
}

function sendEmails(items, emails, query) {
    //let capitalizedQuery = query.charAt(0).toUpperCase() + query.toLowerCase().slice(1)
    let capitalizedQuery = query.toLowerCase().capitalize().trim()
    let halls = []

    for(let item of items) {
        let hall = item.dininghall
        if(hall.includes('Livingston')) {
            hall = 'Livingston'
        } else if(hall.includes('Brower')) {
            hall = 'Brower'
        } else if(hall.includes('Busch')) {
            hall = 'Busch'
        } else if(hall.includes('Neilson')) {
            hall = 'Neilson'
        }

        if(halls.indexOf(hall) === -1) {
            halls.push(hall)
        }
    }
    let hallString = halls.join(', ') + " Dining Hall"
    let subject = capitalizedQuery + " is being served at " + hallString

    let html = ""
    for(let item of items) {
        html += color(bold(item.item)) + " is being served at " + bold(item.dininghall) + " for " + bold(item.meal)
        html += "<br>"
    }

    let email = new sendgrid.Email({
        from: "admin@isitsteaknight.com",
        subject: subject,
        html: html
    })
    email.setTos(emails)
    email.setFrom('IsItSteakNight')

    sendgrid.send(email, function(err, json) {
        if (err) {
            console.error(email)
            console.error(subject)
            return console.error(err)
        }

        console.log(json)
    });
}

function sendMultiQueryEmail(email, items, queries) {
    let capitalizedQueries = []

    let buckets = []
    for(let query of queries) {
        let bucket = {
            query: query,
            items: []
        }

        for(let item of items) {
            if(query.toLowerCase() === item.query.toLowerCase()) {
                bucket.items.push(item)
            }
        }

        if(bucket.items.length > 0) {
            buckets.push(bucket)
            capitalizedQueries.push(query.toLowerCase().capitalize().trim())
        }
    }
    let subject = capitalizedQueries.join(', ') + " is being served at Rutgers Dining Halls"

    let html = ""
    for(let bucket of buckets) {
        html += "<h2>"
        html += bucket.query.toLowerCase().capitalize().trim()
        html += "</h2>"

        for(let item of bucket.items) {
            html += color(bold(item.item)) + " is being served at " + bold(item.dininghall) + " for " + bold(item.meal)
            html += "<br>"  
        }
        
        html += "<br>"       
        html += "<br>"
    }

    let sg_email = new sendgrid.Email({
        from: "admin@isitsteaknight.com",
        subject: subject,
        html: html
    })
    sg_email.setTos(email)
    sg_email.setFrom('IsItSteakNight')

    sendgrid.send(sg_email, function(err, json) {
        if (err) {
            console.error(email)
            console.error(subject)
            return console.error(err)
        }

        console.log(json)
    });
}

request('https://rumobile.rutgers.edu/1/rutgers-dining.txt', (error, body, response) => {
    let menu = JSON.parse(body.body)
    let rows = client.querySync('SELECT query, subscriber FROM "Subscription" ORDER BY subscriber');

    for(let i = 0; i < rows.length; i++) {
        let email = rows[i].subscriber;
        let queries = []

        //keep iterating to get all of current user's queries
        while(rows[i].subscriber.toLowerCase() == email.toLowerCase()) {
            queries.push(rows[i].query)
            i++

            if(i == rows.length) {
                break;
            }
        }
        i--

        let matches = []
        let matchCount = 0
        let onlyQuery
        for(let query of queries) {
            let newMatches = cacheMatch(menu, query)
            matches = matches.concat(newMatches)

            if(newMatches.length > 0) {
                matchCount++
                onlyQuery = query
            }
        }

        if(matchCount == 1) {
            /*
            console.log('single mail')
            console.log(email)
            console.log(matches.length)
            console.log([onlyQuery])
            console.log('***************')
            */

            sendEmails(matches, [email], onlyQuery)
        } else if(matchCount > 1) {
            //sendMultiQueryEmail(email, matches, queries)
            /*
            console.log('multi mail')
            console.log(email)
            console.log(matches.length)
            console.log(queries)
            console.log('***************')
            */

            sendMultiQueryEmail(email, matches, queries)
        }
    }
});
