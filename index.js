
var config = require("./config");
var logger = require("./logger");

var readline = require("readline");
var net = require("net");
var fs = require("fs");
var jf = require("johnny-five");

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
        led.brightness(parseInt((ll / 100) * 255));
    },
    "print.start": function() {
        if(photoresistor.value <= config.photoresistor.level) {
            commands.light(config.light.level);
        }
    },
    "print.stop": function() {
        commands.light(0);
    }
};

var logTypes = jf.Board.prototype.log.types;
jf.Board.prototype.log = function(/* type, module, message [, long description] */) {
    var args = [].slice.call(arguments);
    var type = args.shift();
    var module = args.shift();
    var message = args.shift();
    var color = jf.Board.prototype.log.types[type];
        
    logger[type](String(message)[color], module, args);
}

jf.Board.prototype.log.types = logTypes;

var board = new jf.Board({ repl: false });
var led = null;
var photoresistor = null;

logger.info("Waiting for board to connect...");
board.on("ready", function() {
    logger.info("Board connected.");
    
    led = new jf.Led(config.light.pin);
    photoresistor = new jf.Sensor({
        pin:config.photoresistor.pin, frequency: 1000
    }).on("data", function() {
        logger.debug("Photoresistor: ", this.value);
    });
    
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
            logger.debug("Connection closed.");
        });
    }); 

    if(fs.existsSync(config.socket)) {
        logger.debug("Deleting existing socket...");
        fs.unlinkSync(config.socket);
    }

    server.listen(config.socket);
    logger.info("Listening on " + config.socket);
});
