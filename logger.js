
var fs = require("fs");
var path = require("path");
var winston = require("winston");

winston.add(winston.transports.File, {
	stream: fs.createWriteStream(path.resolve(__dirname, "op-aux.log"), {
		flags: "a",
		mode: 0666
	}),
	timestamp: true,
	json: false,
	handleExceptions: true,
	level: 'debug'
});

winston.remove(winston.transports.Console);

module.exports = winston;

