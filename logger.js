
var config = require("./config");

var winston = require("winston");

winston.remove(winston.transports.Console);

for(var i = 0; i < config.loggers.length; i++) {
    winston.add(config.loggers[i].transport, config.loggers[i].settings);
}

module.exports = winston;

