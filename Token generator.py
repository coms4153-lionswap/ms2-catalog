import jwt

SECRET_KEY = "LION_SWAP_GOAT_IS_THE_KEY"   # 必须跟 main.py 保持一致
ALGORITHM = "HS256"

token = jwt.encode({"user_id": 88}, SECRET_KEY, algorithm=ALGORITHM)
print(token)