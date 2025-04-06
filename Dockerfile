FROM ghcr.io/smart-social-contracts/icp-dev-env:latest

# Create ledger directory
RUN mkdir -p /app/ledger_suite_icrc

# Copy application files
WORKDIR /app
COPY src /app/src
COPY tests/dfx.json /app/dfx.json 
COPY tests/entrypoint.sh /app/entrypoint.sh
COPY tests/src/vault/main.py /app/src/vault/main.py
COPY tests/src/vault/tests /app/src/vault/tests
COPY tests/ledger_suite_icrc/* /app/ledger_suite_icrc/
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt
RUN pip install kybra_simple_db kybra_simple_logging

ENTRYPOINT ["/app/entrypoint.sh"]
