# How to write tests

Tests are written in Python using the `pytest` framework.

When running tests using the Docker container, the tests need to be run against a local canister network. This is done by starting the network using `dfx start --background` and running the tests using `pytest`.

However, when running tests locally, the tests can be run against the app running as a web server.

In one terminal, start the server running the following command:
```
PYTHONPATH=src/canister_main python src/local/main.py
```

In the other terminal, run the tests:
```
ggg --http run_code <PATH_TO_THE_TEST>
```


# Types of tests

extensions       test that `run_code` works
ggg_coverage     tests all ggg functionalities via extensions
demo             deploys a realistic demo with thousands of users, transactions, etc. (stress test)
rpc              test rpc
api              test api
ui               test frontend
