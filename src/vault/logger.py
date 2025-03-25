from utils import running_on_ic


def get_logger():
    if running_on_ic():
        from kybra import ic

        return lambda *args: ic.print(", ".join(map(str, args)))
    else:
        return print
