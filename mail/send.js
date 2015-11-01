import Client from 'pg-native'
import request from 'request'
import Sendgrid from 'sendgrid'
import getMatchingItems from './analyzer'

var client = new Client()
client.connectSync('postgresql://iisn_admin:abc123@localhost:5432/isitsteaknight')

var sendgrid = Sendgrid(process.env.SG_USER, process.env.SG_KEY)

function bold(str) {
    return "<b>" + str + "</b>"
}

function sendEmails(items, emails, query) {
    let capitalizedQuery = query.toLowerCase().charAt(0).toUpperCase() + query.slice(1)
    capitalizedQuery = capitalizedQuery.trim()
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
        html += bold(item.item) + " is being served at " + bold(item.dininghall) + " for " + bold(item.meal)
    }

    let email = new sendgrid.Email({
        from: "admin@isitsteaknight.com",
        subject: subject,
        html: html
    })
    email.setTos(emails)
    email.setFrom('IsItSteakNight')

    sendgrid.send(email, function(err, json) {
        if (err) { return console.error(err) }

        console.log(json)
    });
}

request('https://rumobile.rutgers.edu/1/rutgers-dining.txt', (error, body, response) => {
    let menu = JSON.parse(body.body)
    let rows = client.querySync('SELECT query, email FROM "Subscription" ORDER BY query');
    
    console.log(rows)
    for(let i = 0; i < rows.length; i++) {
        let query = rows[i].query;
        let emails = [];

        let matchedItems = getMatchingItems(menu, query)
        while(rows[i].query.toLowerCase() == query.toLowerCase()) {
            emails.push(rows[i].email)
            i++

            if(i == rows.length) {
                break
            }
        }
        i--

        if(query === "Wild Rice") {
            sendEmails(matchedItems, emails, query)
        }
    }
});
