#!/usr/bin/ic-repl -r ic

import main = "$CANISTER_ID";


call main.greet("Tester");

// let _ = call main.extension_run();
// assert _ == "hello";



/*
call main.set_message("message = 'hello'");


call main.get_message();
let result = _;
assert _ == "hello";


identity temp1;
call main.get_message();
identity temp2;
call main.get_message();
*/


// create states
// add users - governors and citizens
// schedule task
// hooks: new user
// query objects from frontend
// add tax module - run it
// admin users can change code / data
