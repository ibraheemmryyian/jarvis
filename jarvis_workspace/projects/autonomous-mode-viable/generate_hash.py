from passlib.hash import bcrypt

def generate_hash(password: str):
    return bcrypt.hash(password)

def main():
    password = "hello123"
    hashed_password = generate_hash(password)
    print(hashed_password)

if __name__ == "__main__":
    main()