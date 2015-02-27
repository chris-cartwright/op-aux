
var fs = require("fs");
var winston = require("winston");
var path = require("path");

var config = {
    socket: "/tmp/op-aux.sock",
    light: {
        level: 50,
        pin: 9
    },
    photoresistor: {
        level: 500,
        pin: "A0"
    },
    loggers: [
        {
            transport: winston.transports.File,
            settings: {
	            stream: fs.createWriteStream(path.resolve(__dirname, "op-aux.log"), {
		            flags: "a",
		            mode: 0666
	            }),
	            timestamp: true,
	            json: false,
	            handleExceptions: true,
	            level: 'debug'
            }
        }
    ]
};

module.exports = config;
