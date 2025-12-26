import secrets

def get_random_token():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789')
                   for i in range(16))