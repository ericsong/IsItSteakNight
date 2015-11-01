import Client from 'pg-native'
import request from 'request'
import Sendgrid from 'sendgrid'
import getMatchingItems from './analyzer'

var client = new Client()
client.connectSync('postgresql://iisn_admin:abc123@localhost:5432/isitsteaknight')

var sendgrid = Sendgrid(process.env.SG_USER, process.env.SG_KEY)
var email = new sendgrid.Email()

var payload = {
    to: "regonics@gmail.com",
    from: "me@isitsteaknight.com",
    subject: "Steak is being served at Busch Dining Hall",
    text: "Teriyaki steak is being served at Busch Dining Hall for Dinner"
}
sendgrid.send(payload, (err, json) => {
    if (err) { console.error(err) }
    console.log(json)
})

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

        console.log(query + ": " + emails)
        console.log(matchedItems)
    }
});
