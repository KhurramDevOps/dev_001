from passlib.hash import bcrypt_sha256
hashed = bcrypt_sha256.hash("khurram123")
print(bcrypt_sha256.verify("khurram123", hashed))
