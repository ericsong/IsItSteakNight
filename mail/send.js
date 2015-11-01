import Client from 'pg-native'

let client = new Client()
client.connectSync('postgresql://iisn_admin:abc123@localhost:5432/isitsteaknight')

var rows = client.querySync('SELECT * FROM "Subscription"');
console.log(rows)
