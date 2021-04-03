'use strict';

const Readline = require('readline');
const rl = Readline.createInterface({
	input: process.stdin,
	output: process.stdout,
	terminal: false
});

var time = 0;
var pkey = "";
var skey = "";
var pid = "";
const matcher = require('./matcher');
var util = require("util");
var {PythonShell} = require("python-shell");

rl.setPrompt ('> ');
rl.prompt();
rl.on('line', reply => {
	
	matcher(reply, cb => {
		if (cb.intent == "default"){
			console.log("Sorry, I couldn't understand your question.");
		}else{
			if (cb.intent == "Exit"){
				console.log("Goodbye!");
				process.exit();
			}else{
				if (cb.intent == "Playlist"){
					console.log("Opening child process...");
					let options = {pythonOptions: ["-u"], args: [pkey, skey, pid, time]};
					PythonShell.run("recom.py", options, function (err, results) {
					  if (err) throw err;
					  console.log('results: %j', results);
					});
				}else{
					if (cb.intent == "Hello"){
						console.log("Hi! How long do you want your playlist to be?");
					}else{
						if (cb.intent == "Author"){
							console.log("Alexandre Autret, Pierre Archambault, and Pierre Le Lay!");
						}else{
							if (cb.intent == "Time"){
								time = cb.entities.time;
								console.log("Now, enter your Spotify public key like this: public key <value>");
							}else{
								if (cb.intent == "Pkey"){
									console.log("Enter your private key like this: private key <value>");
									pkey = cb.entities.pkey;
								}else{
									if (cb.intent == "Skey"){
										console.log("Enter your Spotify playlist ID like this: playlist id <value>");
										skey = cb.entities.skey;
									}else{
										if (cb.intent == "Pid"){
											pid = cb.entities.pid;
											console.log("Now, tell me to make a playlist!");
										}
									}
								}
							}
						}
					}
				}
			}
		}
		rl.setPrompt ('> ');
		rl.prompt();
	});
});
