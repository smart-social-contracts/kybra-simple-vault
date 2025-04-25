FROM ghcr.io/smart-social-contracts/icp-dev-env:latest

# Create ledger directory
RUN mkdir -p /app/ledger_suite_icrc

# Copy application files
WORKDIR /app
COPY src /app/src
COPY dfx.json /app/dfx.json 
COPY tests /app/tests
# COPY tests/entrypoint.sh /app/entrypoint.sh
# COPY tests/test_ic_integration.py /app/test_ic_integration.py
# COPY tests/artifacts* /app/ledger_suite_icrc/
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

