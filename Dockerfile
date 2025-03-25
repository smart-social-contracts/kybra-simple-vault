FROM ghcr.io/smart-social-contracts/icp-dev-env:latest

COPY src /app/src
COPY tests/dfx.json /app/dfx.json
COPY tests/entrypoint.sh /app/entrypoint.sh
COPY tests/src/vault/main.py /app/src/vault/main.py
COPY tests/src/vault/tester.py /app/src/vault/tester.py
COPY tests/src/vault/tests /app/src/vault/tests

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
