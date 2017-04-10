
def get_api_base():
    return payconiq.api_base \
            if payconiq.environment == 'production' else payconiq.api_base_test

def is_signature_valid(signature, timestamp, key, algorithm, body):
    if algorithm == 'SHA256WithRSA':
        signature_before = '{merchant_id}|{timestamp}|{crc32}'.format(
            merchant_id=merchant_id,
            timestamp=timestamp,
            crc32=crc32
        )
    return False
