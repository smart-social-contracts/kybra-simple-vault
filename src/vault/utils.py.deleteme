_running_on_ic = None


def running_on_ic() -> bool:
    global _running_on_ic
    if _running_on_ic is not None:
        return _running_on_ic

    try:
        from kybra import ic

        ic.print("")
        return True
    except Exception:
        pass
    return False
