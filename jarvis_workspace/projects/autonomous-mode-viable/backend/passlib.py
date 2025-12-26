from typing import Any, Union

class PassLib:
    @staticmethod
    def hash(password: str) -> str:
        """
        Hash a password using bcrypt.
        :param password: The password to hash.
        :return: The hashed password.
        """
        from passlib.hash import bcrypt
        return bcrypt.hash(password).decode('utf-8')

    @staticmethod
    def verify(hashed_password: str, input_password: str) -> bool:
        """
        Verify a password against a hashed stored password using bcrypt.
        :param hashed_password: The hashed password to compare with the input password.
        :param input_password: The plain text password to check.
        :return: True if the password is correct, False otherwise.
        """
        from passlib.hash import bcrypt
        return bcrypt.verify(input_password, hashed_password)