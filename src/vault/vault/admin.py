from kybra_simple_logging import get_logger

import vault.services as services
from vault.entities import app_data, ledger_canister, stats

logger = get_logger(__name__)


def _only_if_admin(caller: str) -> bool:
    admin = app_data().admin_principal
    if admin and admin != caller:
        raise ValueError(f"Caller {caller} is not the current admin principal {admin}")


def set_admin(caller: str, principal: str) -> str:
    _only_if_admin(caller)
    logger.info(f"Setting admin from {app_data().admin_principal} to {principal}")
    app_data().admin_principal = principal
    return str(stats())


def reset(caller: str) -> str:
    _only_if_admin(caller)
    services.reset()
    return str(stats())


def set_heartbeat_interval_seconds(caller: str, seconds: int) -> int:
    _only_if_admin(caller)
    app_data().heartbeat_interval_seconds = seconds
    return seconds


def set_ledger_canister(caller: str, canister_id: str, principal: str) -> str:
    _only_if_admin(caller)

    canister = ledger_canister()
    canister.principal = principal
    logger.info(f"Setting ledger canister {canister_id}'s principal to {principal}")
    return str(stats())
