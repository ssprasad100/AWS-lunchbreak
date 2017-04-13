import payconiq


def get_api_base():
    return payconiq.api_base \
        if payconiq.environment == 'production' else payconiq.api_base_test
