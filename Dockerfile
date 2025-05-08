FROM ghcr.io/smart-social-contracts/icp-dev-env:latest

RUN mkdir -p /app/artifacts/ledger_suite_icrc

WORKDIR /app
COPY src /app/src
COPY tests /app/tests
COPY dfx.json /app/dfx.json
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
RUN pip install kybra_simple_db kybra_simple_logging

ENTRYPOINT ["/app/tests/entrypoint.sh"]
