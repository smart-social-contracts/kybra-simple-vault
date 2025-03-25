FROM ghcr.io/smart-social-contracts/icp-dev-env:latest

COPY ../src /app/src
COPY dfx.json /app/dfx.json
COPY entrypoint.sh /app/entrypoint.sh
COPY src/vault/main.py /app/src/vault/main.py
COPY src/vault/tester.py /app/src/vault/tester.py

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
