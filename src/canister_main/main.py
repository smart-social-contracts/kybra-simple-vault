import traceback
from typing import List, Dict, Optional
from kybra import (
    Async,
    CallResult,
    init,
    heartbeat,
    blob,
    Func,
    match,
    nat,
    nat16,
    nat64,
    Opt,
    Principal,
    query,
    Query,
    Record,
    Tuple,
    Variant,
    Vec,
    ic,
    update,
    void,
)

from datetime import datetime

from ggg.base import universe, initialize
from core.token_icrc1 import TokenICRC1
from core.icrcledger import ICRCLedger, Account #, get_canister_balance_2

from core.logger import json_dumps, log
# from core.db import init_db, create_user, get_user, get_all_users, create_organization, get_organization, get_all_organizations
# from core.transaction import Transaction
import api

# Token Transfer Types


class TokenTransferArgs(Record):
    to_principal: Principal
    amount: nat  # Amount in e8s (8 decimal places)
    memo: Opt[nat64]


class InsufficientBalanceRecord(Record):
    balance: nat


class MessageRecord(Record):
    message: str


class TokenTransferError(Variant, total=False):
    InsufficientBalance: InsufficientBalanceRecord
    TransferFailed: MessageRecord
    InvalidAmount: MessageRecord


class TokenTransferResponse(Variant, total=False):
    Ok: nat  # Transaction index
    Err: TokenTransferError

# Token Manager Implementation


class HttpRequest(Record):
    method: str
    url: str
    headers: Vec["Header"]
    body: blob


class HttpResponse(Record):
    status_code: nat16
    headers: Vec["Header"]
    body: blob
    streaming_strategy: Opt["StreamingStrategy"]
    upgrade: Opt[bool]


Header = Tuple[str, str]


class StreamingStrategy(Variant):
    Callback: "CallbackStrategy"


class CallbackStrategy(Record):
    callback: "Callback"
    token: "Token"


Callback = Func(Query[["Token"], "StreamingCallbackHttpResponse"])


class StreamingCallbackHttpResponse(Record):
    body: blob
    token: Opt["Token"]


class Token(Record):
    key: str


# API functions

@query
def get_universe() -> str:
    return json_dumps(universe())


@update
def destroy_universe() -> str:
    # from core.db_storage import db 
    # TODO: broken
    db.clear()  # TODO: not supported when running on ICP
    return 'OK'


@query
def get_stats() -> str:
    return json_dumps([i.to_dict() for i in Snapshot.instances()])  # TODO


@query
def get_organization_list() -> str:
    """Get a list of all organizations"""
    return json_dumps(api.get_organization_list())


@query
def get_organization_data(organization_id: str) -> str:
    """Get details of a specific organization"""
    data = api.get_organization_data(organization_id)
    if data is None:
        return json_dumps({"error": "Organization not found"})
    return json_dumps(data)


@update
def create_user_endpoint() -> str:
    """Create a new user"""
    try:
        user = api.create_user()
        return json_dumps(user)
    except Exception as e:
        return json_dumps({"error": str(e)})


@query
def get_user_data(user_id: str) -> str:
    """Get details of a specific user"""
    data = api.get_user_data(user_id)
    if data is None:
        return json_dumps({"error": "User not found"})
    return json_dumps(data)


@query
def get_user_list() -> str:
    """Get a list of all users"""
    return json_dumps(api.get_user_list())


@query
def get_token_list() -> str:
    """Get a list of all tokens"""
    return json_dumps(api.get_token_list())


@query
def get_token_data(token_id: str) -> str:
    """Get details of a specific token"""
    data = api.get_token_data(token_id)
    if data is None:
        return json_dumps({"error": "Token not found"})
    return json_dumps(data)


@query
def get_token_transactions(token_id: str, address: str = None, limit: int = 100) -> str:
    """Get transaction history for a specific token"""
    data = api.get_token_transactions(token_id, address, limit)
    if data is None:
        return json_dumps({"error": "Token not found"})
    return json_dumps(data)


@query
def get_proposal_data(proposal_id: str) -> str:
    """Get details of a specific proposal"""
    try:
        result = api.get_proposal_data(proposal_id)
        return json_dumps(result) if result else ""
    except Exception as e:
        print(f"Error in get_proposal_data: {e}")
        traceback.print_exc()
        return ""


@update
def user_join_organization_endpoint(user_id: str) -> str:
    """User joins an organization"""
    try:
        result = api.user_join_organization(user_id)
        return json_dumps({"success": result})
    except Exception as e:
        return json_dumps({"error": str(e)})


@update
def run_code(source_code: str) -> str:
    # TODO: every object needs to have permissions and use ic.caller() for that...
    # log("source_code = %s" % source_code)
    from core.execution import run_code
    result = run_code(source_code)
    # log("result = %s" % result)
    return json_dumps(result)  # {"result": result})


@query
def create_user(name: str) -> str:
    user = User(id, ic_identity=ic.caller()).commit()
    return f"Hello, user {user.id} with Internet Identity {user.ic_identity}!"


# other functions


@heartbeat
def heartbeat_() -> Async[void]:
    # runs hooks, refreshes balances/transactions and sends transactions
    from core.execution import execute_heartbeat
    execute_heartbeat()

    # TODO:
    # # iterates through all tokens and refreshes balances/transactions
    # for token in TokenICRC1.instances():
    #     total_supply = yield get_canister_balance_2()
    #     if total_supply != token.total_supply:
    #         ic.print("%s: total_supply changed from %s to %s" % (token.symbol, token.total_supply, total_supply))
    #         token.total_supply = total_supply
    #         token.save()

@init
def init_() -> void:
    ic.print("Initializing canister...")
    initialize()
    ic.print("Canister initialized !")


@query
def http_request(req: HttpRequest) -> HttpResponse:
    url = req["url"]
    if url == "/api/v1/get_universe":
        return http_request_core(universe())
    elif url == "/api/v1/tokens":
        return http_request_core(get_token_list())
    elif url.startswith("/api/v1/tokens/"):
        token_id = url.split("/")[-1]
        data = get_token_data(token_id)
        if data is None:
            return {
                "status_code": 404,
                "headers": [],
                "body": bytes(json_dumps({"error": "Token not found"}), "ascii"),
                "streaming_strategy": None,
                "upgrade": False
            }
        return http_request_core(data)
    return {"status_code": 404,
            "headers": [],
            "body": bytes("Not found", "ascii"),
            "streaming_strategy": None,
            "upgrade": False}


def http_request_core(data):
    try:
        d = json_dumps(data)
        return {
            "status_code": 200,
            "headers": [],
            "body": bytes(d + "\n", "ascii"),
            "streaming_strategy": None,
            "upgrade": False,
        }
    except Exception as e:
        return {
            "status_code": 500,
            "headers": [],
            "body": bytes(traceback.format_exc(), "ascii"),
            "streaming_strategy": None,
            "upgrade": False,
        }


@query
def do_request(url: str) -> str:
    return request(url)


@query
def greet(name: str) -> str:
    return f"Hello, {name} from identity {ic.caller()}!"


# returns the principal of the identity that called this function
@query
def caller() -> Principal:
    return ic.caller()


# Token Management Endpoints

@query
def get_canister_balance() -> Async[nat]:
    return get_canister_balance_2()

    # ic.print('get_canister_balance')
    # ck_btc = TokenICRC1['ckBTC']
    # ic.print("ck_btc = %s" % ck_btc)
    # ledger = ICRCLedger(Principal.from_str(ck_btc.principal))
    # account = Account(owner=ic.id(), subaccount=None)
    # result: CallResult[nat] = yield ledger.icrc1_balance_of(account)
    # return match(result, {
    #     "Ok": lambda ok: ok,
    #     "Err": lambda err: 0  # Return 0 balance on error
    # })


# @query
# def get_receiving_principal() -> Principal:
#     """Get the principal ID where users can send tokens to this canister"""
#     return TokenManager.get_canister_principal()


# @update
# def send_tokens(args: TokenTransferArgs) -> Async[TokenTransferResponse]:
#     """Send tokens from the canister to a specified principal"""
#     return TokenManager.send_tokens(args)
