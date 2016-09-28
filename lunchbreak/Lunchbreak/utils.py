from decimal import Decimal


def format_decimal(value):
    return '€ {}'.format(
        value.quantize(
            Decimal(10) ** -2
        )
    ).replace('.', ',')
