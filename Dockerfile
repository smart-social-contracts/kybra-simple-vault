FROM ghcr.io/smart-social-contracts/icp-dev-env:latest

# Create ledger directory
RUN mkdir -p /app/artifacts/ledger_suite_icrc

# Copy application files
WORKDIR /app
COPY src /app/src
COPY tests/dfx.json /app/dfx.json 
COPY tests/entrypoint.sh /app/entrypoint.sh
COPY tests/*.py /app/
COPY tests/artifacts/ledger_suite_icrc/* /app/artifacts/ledger_suite_icrc
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt
RUN pip install kybra_simple_db kybra_simple_logging

ENTRYPOINT ["/app/entrypoint.sh"]
