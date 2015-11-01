import Client from 'pg-native'
import request from 'request'
import getMatchingItems from './analyzer'

let client = new Client()
client.connectSync('postgresql://iisn_admin:abc123@localhost:5432/isitsteaknight')

request('https://rumobile.rutgers.edu/1/rutgers-dining.txt', (error, body, response) => {
    let menu = JSON.parse(body.body)
    let rows = client.querySync('SELECT query, email FROM "Subscription" ORDER BY query');
    
    console.log(rows)
    for(let i = 0; i < rows.length; i++) {
        let query = rows[i].query;
        let emails = [];

        while(rows[i].query.toLowerCase() == query.toLowerCase()) {
            emails.push(rows[i].email)
            i++

            if(i == rows.length) {
                break
            }
        }
        i--

        console.log(query + ": " + emails)
        console.log(getMatchingItems(menu, query))
    }
});
