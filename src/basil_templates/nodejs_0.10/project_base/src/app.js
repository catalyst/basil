/**
 * Created by andreik on 28/10/14.
 */

var printHello = function(name){
    return "hello "+name+"!";
};

//mysyntaxerr(); //Uncomment this one to see err details


module.exports.run = function(req, res, d) {
//    setTimeout(function(){
//        throw 'error'; //error thrown in callback
//    },300);
    setTimeout(function(){
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.end(printHello("Node"));
    },1000);
};