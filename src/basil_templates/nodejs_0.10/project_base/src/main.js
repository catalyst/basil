var http = require('http');

http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello Node!\n');
    /**
     * supervisor will detect your changes within src dir and restart your node app
     */
}).listen(1337);
console.log('Server running at port 1337');