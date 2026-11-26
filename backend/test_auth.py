
from app.auth.token import (
    create_access_token,
    decode_access_token,
)

token = create_access_token(user_id=1)

print("Token generated:", bool(token))

payload = decode_access_token(token)

print("User ID:", payload["sub"])
print("Token has expiration:", "exp" in payload)
