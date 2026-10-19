import math
from typing import Tuple


def js_number(value: float) -> str:
    if value == 0:
        return "0"
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"

    digits, point = _decimal_digits(abs(value))
    count = len(digits)
    if count <= point <= 21:
        text = digits + "0" * (point - count)
    elif 0 < point <= 21:
        text = f"{digits[:point]}.{digits[point:]}"
    elif -6 < point <= 0:
        text = "0." + "0" * (-point) + digits
    else:
        power = point - 1
        sign = "-" if power < 0 else "+"
        mantissa = digits if count == 1 else f"{digits[0]}.{digits[1:]}"
        text = f"{mantissa}e{sign}{abs(power)}"

    return f"-{text}" if value < 0 else text


def _decimal_digits(magnitude: float) -> Tuple[str, int]:
    mantissa, _, exponent = repr(magnitude).partition("e")
    integer_part, _, fraction_part = mantissa.partition(".")
    digits = integer_part + fraction_part.rstrip("0")
    leading_zeros = len(digits) - len(digits.lstrip("0"))
    return digits[leading_zeros:], len(integer_part) + int(
        exponent or 0
    ) - leading_zeros
