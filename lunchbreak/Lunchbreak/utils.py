from decimal import Decimal


def format_decimal(value):
    return '€ {}'.format(
        value.quantize(
            Decimal(10) ** -2
        )
    ).replace('.', ',')


def format_money(value):
    return '€ {}'.format(
        (
            Decimal(value) / Decimal(100)
        ).quantize(
            Decimal(10) ** -2
        )
    ).replace('.', ',')
