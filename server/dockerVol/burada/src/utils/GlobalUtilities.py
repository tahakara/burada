@staticmethod
def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ('true', '1', 't', 'yes', 'y')