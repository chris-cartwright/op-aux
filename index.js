
var config = require("./config");
var logger = require("./logger");

var readline = require("readline");
var net = require("net");
var fs = require("fs");

var commands = {
    "light": function(level) {
        if(level == undefined) {
            level = 0;
        }
        
        var ll = parseInt(level);
        if(isNaN(ll)) {
            logger.warn("Unknown value: ", level);
            return;
        }
        
        if(ll < 0) {
            logger.warn("Value too small: ", ll);
            ll = 0;
        }
        
        if(ll > 100) {
            logger.warn("Value too large: ", ll);
            ll = 100;
        }
        
        logger.info("Setting light level to: ", ll);
    },
    "print.start": function() {
        commands.light(config.light.level);
    },
    "print.stop": function() {
        commands.light(0);
    }
};

var server = net.createServer(function(stream) {
    var rl = readline.createInterface(stream, stream);
    
    rl.on("line", function(line) {
        logger.info("Received line: ", line);
        var args = line.split(" ");
        var cmd = commands[args[0]];
        if(cmd == undefined) {
            logger.error("Unknown command: ", args[0]);
            return;
        }
        
        cmd.apply(this, args.slice(1));
    });
    
    stream.on("close", function() {
        logger.info("Connection closed.");
    });
}); 

if(fs.existsSync(config.socket)) {
    fs.unlinkSync(config.socket);
}

server.listen(config.socket);
logger.info("Listening on " + config.socket);

