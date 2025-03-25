import ast

from kybra import (
    Async,
    CallResult,
    match,
    Opt,
    Principal,
    Record,
    Service,
    service_query,
    service_update,
    Variant,
    nat,
    nat64,
    update,
    query,
    blob,
    null,
    ic,
    heartbeat,
    void
)




from kybra_simple_db import *  # TODO
db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100_000, max_value_size=1_000_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100_000, max_value_size=1_000_000
)

Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)



# MAINNET_CKBTC_LEDGER_CANISTER = 'mxzaz-hqaaa-aaaar-qaada-cai'

# CKBTC_CANISTER = MAINNET_CKBTC_LEDGER_CANISTER
# # CKBTC_INDEX_CANISTER = 'bkyz2-fmaaa-aaaaa-qaaaq-cai'


# class Account(Record):
#     owner: Principal
#     subaccount: Opt[blob]


# class TransferArg(Record):
#     to: Account
#     fee: Opt[nat]
#     memo: Opt[nat64]
#     from_subaccount: Opt[blob]
#     created_at_time: Opt[nat64]
#     amount: nat


# class BadFeeRecord(Record):
#     expected_fee: nat


# class BadBurnRecord(Record):
#     min_burn_amount: nat


# class InsufficientFundsRecord(Record):
#     balance: nat


# class DuplicateRecord(Record):
#     duplicate_of: nat


# class GenericErrorRecord(Record):
#     error_code: nat
#     message: str


# class TransferError(Variant, total=False):
#     BadFee: BadFeeRecord
#     BadBurn: BadBurnRecord
#     InsufficientFunds: InsufficientFundsRecord
#     TooOld: null
#     CreatedInFuture: null
#     Duplicate: DuplicateRecord
#     TemporarilyUnavailable: null
#     GenericError: GenericErrorRecord


# class TransferResult(Variant, total=False):
#     Ok: nat
#     Err: TransferError


# class ICRCLedger(Service):
#     @service_query
#     def icrc1_balance_of(self, account: Account) -> nat:
#         ...

#     @service_query
#     def icrc1_fee(self) -> nat:
#         ...

#     @service_update
#     def icrc1_transfer(self, args: TransferArg) -> TransferResult:
#         ...


# @query
# def get_canister_id() -> Async[Principal]:
#     return ic.id()


# @query
# def get_canister_balance() -> Async[nat]:
#     # TODO: this one doesn't work but it doesn't matter...
#     ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))
#     account = Account(owner=ic.id(), subaccount=None)

#     result: CallResult[nat] = yield ledger.icrc1_balance_of(account)

#     return match(result, {
#         "Ok": lambda ok: ok,
#         "Err": lambda err: -1  # Return -1 balance on error
#     })


# @update
# def do_transfer(to: Principal, amount: nat) -> Async[nat]:
#     ledger = ICRCLedger(Principal.from_str(CKBTC_CANISTER))

#     args: TransferArg = TransferArg(
#         to=Account(owner=to, subaccount=None),
#         amount=amount,
#         fee=None,  # Optional fee, will use default
#         memo=None,  # Optional memo field
#         from_subaccount=None,  # No subaccount specified
#         created_at_time=None  # System will use current time
#     )

#     result: CallResult[TransferResult] = yield ledger.icrc1_transfer(args)

#     return match(result, {
#         "Ok": lambda ok: 0,
#         "Err": lambda err: -1
#     })



# def parse_candid(i: str) -> str:
#     i = i.strip()
#     i = i.replace('record {', '{')
#     i = i.replace('opt', '')
#     i = i.replace('blob', '')
#     i = i.replace('vec', '')
#     i = i.replace('principal', '')
#     i = i.replace('null', 'None')
#     i = i.replace(': nat64', '')
#     i = i.replace(': nat', '')
#     i = i.replace(';', '')
#     i = i.replace('_', '')
#     i = i.replace(' = ', ': ')
#     i = i.replace('\x00', '')

#     i2 = []
#     is_inside_transactions = False
#     level = 0
#     lines = i.split('\n')
#     for i, l in enumerate(lines):
#         if is_inside_transactions:
#             if '{' in l:
#                 level += 1
#             if '}' in l:
#                 level -= 1
#                 if level < 0:
#                     is_inside_transactions = False
#                     l = ']'

#         if '1349681965' in l:
#             continue
#         if '5094982' in l:
#             continue
#         if l == '}' and is_inside_transaction:
#             l = ']'
#         if '{' not in l and '(' not in l:
#             if ',' not in l and i != len(lines) - 1:
#                 l += ','
#         if '3331539157:  {' in l:
#             l = '3331539157 : ['
#             is_inside_transactions = True
#             level = 0

#         i2.append(l)


#     i2 = '\n'.join(i2)

#     field_map = {
#         "1_779_015_299": "first_index",
#         "2_799_807_105": "log_length",
#         "3_331_539_157": "transactions",
#         "3_650_848_786": "archived_transactions",
#         "2_131_139_013": "callback",
#         "2_215_343_202": "start",
#         "2_668_074_214": "length",
#         "2781795542": "timestamp",
#         "1191829844": "kind",
#         "3573748184": "amount",
#         "3664621355": "transfer",
#         "1136829802": "from",
#         "947296307": "owner",
#         "25979": "to",
#     }

#     for k, v in field_map.items():
#         i2 = i2.replace(k.replace('_', ''), '"%s"' % v)

#     print(i2)
#     d = ast.literal_eval(i2)

#     return d


# @update
# def my_get_transactions(
#     start: nat, length: nat
# ) -> str:
#     # Example: '(record { start = 2_324_900 : nat; length = 2 : nat })'
#     candid_args = '(record { start = %s : nat; length = %s : nat })' % (start, length)

#     call_result: CallResult[blob] = yield ic.call_raw(
#         Principal.from_str(CKBTC_CANISTER),
#         "get_transactions",
#         ic.candid_encode(candid_args),
#         0
#     )

#     response = parse_candid(ic.candid_decode(call_result.Ok))
#     return str(response)



# last_heartbeat_time = 0
# time_period_seconds = 10

# @heartbeat
# def heartbeat_() -> void:
#     # ic.print("this runs ~1 time per second")
#     global last_heartbeat_time
#     now = ic.time()
#     if (now - last_heartbeat_time) / 1e9 > time_period_seconds:
#         last_heartbeat_time = now
#     # ic.print("last_heartbeat_time: %s" % last_heartbeat_time)

# @query
# def get_last_heartbeat_time() -> str:
#     return str(last_heartbeat_time / 1e9)



# @query
# def version() -> str:
#     return '0.6.46'
