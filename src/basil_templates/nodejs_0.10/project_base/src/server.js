var http = require('http');
domain = require('domain').create();


/**
 * supervisor will detect your changes within src dir and restart your node app
 * Don't modify this file if you just want to play slightly with node, modify app.js instead
 */
http.createServer(function (req, res) {
    domain.on('error', function(err) {
        console.log(err);
        res.writeHead(500, {'Content-Type': 'text/plain'});
        res.end("Oops... Something went wrong with your app (domain): "+err.stack);
        process.exit(1); //kill the process to avoid memory leaks, supervisor will restart it for us
    });

    /**
     * domain.run will handle all errors for us
     * don't ever do that on production server! see http://nodejs.org/api/domain.html#domain_warning_don_t_ignore_errors
     * For our educational purpose it is actually fine (nothing will leak,
     * because process is killed immediately after catching exception
     */
    domain.run(function(){
        var app = require('./app.js');
        app.run(req,res);
    });

}).listen(1337);
console.log('Server running at port 1337');