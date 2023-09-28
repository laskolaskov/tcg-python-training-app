import unittest
from unittest.mock import MagicMock, Mock
from marshmallow import ValidationError
from validator import validate_signup, validate_auth


class TestValidators(unittest.TestCase):
    def test_validate_signup(self):
        db = Mock()

        # invalid input
        input = [
            {"username": "test_user", "password": "test_user_password"},
            {"username": "new_user", "password": "test_user_password"},
            {"username": "some_user"},
            {"username": "some_user@mail.org"},
            {},
            {"password": "test_user_password"},
        ]

        for i in input:
            self.assertRaises(ValidationError, validate_signup, i, db)

        # valid input
        valid_input = {
            "username": "test_user@mail.com",
            "password": "test_user_password",
        }
        expected = valid_input.copy()
        expected["is_admin"] = False

        db.getUserByName = MagicMock(return_value=False)
        result = validate_signup(valid_input, db)
        self.assertDictEqual(expected, result)

        # valid input but user exists
        db.getUserByName = MagicMock(return_value=True)
        self.assertRaises(ValidationError, validate_signup, valid_input, db)

    def test_validate_auth(self):
        db = Mock()
        db.getUserByName = MagicMock(return_value=False)

        # invalid input
        input = [
            {"username": "test_user", "password": "test_user_password"},
            {"username": "new_user", "password": "test_user_password"},
            {"username": "some_user"},
            {"username": "some_user@mail.org"},
            {},
            {"password": "test_user_password"},
        ]

        for i in input:
            self.assertRaises(ValidationError, validate_auth, i, db)

        # valid input but user not exists
        valid_input = {
            "username": "test_user@mail.com",
            "password": "test_user_password",
        }
        self.assertRaises(ValidationError, validate_auth, valid_input, db)


if __name__ == "__main__":
    unittest.main()
