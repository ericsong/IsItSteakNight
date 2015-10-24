/*
 * Deletes all duplicate menus in database
 *
 */

var mongoose = require('mongoose');
var request = require('request');

mongoose.connect('mongodb://localhost/isitsteaknight');

var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));

var menuSchema = mongoose.Schema({
    data: Object,
    time : { type : Date, default: Date.now } 
});

var Menu = mongoose.model('menu', menuSchema);

function deepCompare () {
  var i, l, leftChain, rightChain;

  function compare2Objects (x, y) {
    var p;

    // remember that NaN === NaN returns false
    // and isNaN(undefined) returns true
    if (isNaN(x) && isNaN(y) && typeof x === 'number' && typeof y === 'number') {
         return true;
    }

    // Compare primitives and functions.     
    // Check if both arguments link to the same object.
    // Especially useful on step when comparing prototypes
    if (x === y) {
        return true;
    }

    // Works in case when functions are created in constructor.
    // Comparing dates is a common scenario. Another built-ins?
    // We can even handle functions passed across iframes
    if ((typeof x === 'function' && typeof y === 'function') ||
       (x instanceof Date && y instanceof Date) ||
       (x instanceof RegExp && y instanceof RegExp) ||
       (x instanceof String && y instanceof String) ||
       (x instanceof Number && y instanceof Number)) {
        return x.toString() === y.toString();
    }

    // At last checking prototypes as good a we can
    if (!(x instanceof Object && y instanceof Object)) {
        return false;
    }

    if (x.isPrototypeOf(y) || y.isPrototypeOf(x)) {
        return false;
    }

    if (x.constructor !== y.constructor) {
        return false;
    }

    if (x.prototype !== y.prototype) {
        return false;
    }

    // Check for infinitive linking loops
    if (leftChain.indexOf(x) > -1 || rightChain.indexOf(y) > -1) {
         return false;
    }

    // Quick checking of one object beeing a subset of another.
    // todo: cache the structure of arguments[0] for performance
    for (p in y) {
        if (y.hasOwnProperty(p) !== x.hasOwnProperty(p)) {
            return false;
        }
        else if (typeof y[p] !== typeof x[p]) {
            return false;
        }
    }

    for (p in x) {
        if (y.hasOwnProperty(p) !== x.hasOwnProperty(p)) {
            return false;
        }
        else if (typeof y[p] !== typeof x[p]) {
            return false;
        }

        switch (typeof (x[p])) {
            case 'object':
            case 'function':

                leftChain.push(x);
                rightChain.push(y);

                if (!compare2Objects (x[p], y[p])) {
                    return false;
                }

                leftChain.pop();
                rightChain.pop();
                break;

            default:
                if (x[p] !== y[p]) {
                    return false;
                }
                break;
        }
    }

    return true;
  }

  if (arguments.length < 1) {
    return true; //Die silently? Don't know how to handle such case, please help...
    // throw "Need two or more arguments to compare";
  }

  for (i = 1, l = arguments.length; i < l; i++) {

      leftChain = []; //Todo: this can be cached
      rightChain = [];

      if (!compare2Objects(arguments[0], arguments[i])) {
          return false;
      }
  }

  return true;
}

function menuDeepCompare(menu1, menu2) {
    var menu1copy = JSON.parse(JSON.stringify(menu1))
    var menu2copy = JSON.parse(JSON.stringify(menu2))

    for(var i = 0; i < menu1copy.length; i++) {
        delete menu1copy[i].date;
    }

    for(var i = 0; i < menu2copy.length; i++) {
        delete menu2copy[i].date;
    }

    return deepCompare(menu1copy, menu2copy);
}

Menu.find(function(err, docs) {
    var dups = [];
    var uniques = [];

    for(var i = 0; i < docs.length; i++) {
        if(dups.indexOf(docs[i]._id) != -1) {
            continue;
        }
        uniques.push(docs[i]._id);

        var menu1 = docs[i].data;
        for(var j = i+1; j < docs.length; j++) {
            var menu2 = docs[j].data;
            if(menuDeepCompare(menu1, menu2)) {
                dups.push(docs[j]._id);
            } 
        }
    }

    console.log(dups)
    console.log(uniques)
    console.log(dups.length + uniques.length)

    Menu.remove({_id: {$in: dups}}, function() {
        console.log('done removing');  
        mongoose.connection.close()
    });
})
