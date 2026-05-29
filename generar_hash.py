import bcrypt

password = "Admin123"

hash = bcrypt.hashpw(
    password.encode(),
    bcrypt.gensalt()
)

print(hash.decode())

