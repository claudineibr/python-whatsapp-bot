from decimal import (
    Decimal,
    ROUND_HALF_UP,
)


def format_currency(value: str) -> str:
    return f"R$ {Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"
