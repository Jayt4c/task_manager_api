import secrets

jwt_secret_key = secrets.token_hex(32)  # 32 bytes // hex characters
print(jwt_secret_key)
