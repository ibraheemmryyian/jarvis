#!/usr/bin/env python3
"""
Test suite for email validator module.
"""

import unittest
from email_validator import is_valid_email, validate_email_detailed, validate_email_list


class TestEmailValidator(unittest.TestCase):
    
    def test_is_valid_email(self):
        # Valid emails
        valid_emails = [
            'user@example.com',
            'test@domain.co.uk',
            'user.name@example.com',
            'user+tag@example.org',
            'user123@test-domain.com'
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(is_valid_email(email))
        
        # Invalid emails
        invalid_emails = [
            '',
            'invalid.email',
            '@example.com',
            'user@',
            'user@@example.com',
            'user@domain',
            'user@domain.',
            '.user@example.com',
            'user.@example.com'
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(is_valid_email(email))
    
    def test_validate_email_detailed(self):
        # Test valid email
        is_valid, errors = validate_email_detailed('user@example.com')
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
        
        # Test invalid email
        is_valid, errors = validate_email_detailed('invalid.email')
        self.assertFalse(is_valid)
        self.assertIn('Email format is invalid', errors)
        
        # Test empty email
        is_valid, errors = validate_email_detailed('')
        self.assertFalse(is_valid)
        self.assertIn('Email cannot be empty', errors)
        
        # Test email with multiple @ symbols
        is_valid, errors = validate_email_detailed('user@@example.com')
        self.assertFalse(is_valid)
        self.assertIn('Email must contain exactly one @ symbol', errors)
    
    def test_validate_email_list(self):
        emails = [
            'user@example.com',
            'invalid.email',
            'test@domain.co.uk'
        ]
        
        results = validate_email_list(emails)
        
        self.assertEqual(len(results), 3)
        
        # Check first result
        self.assertEqual(results[0][0], 'user@example.com')
        self.assertTrue(results[0][1])
        self.assertEqual(results[0][2], [])
        
        # Check second result
        self.assertEqual(results[1][0], 'invalid.email')
        self.assertFalse(results[1][1])
        
        # Check third result
        self.assertEqual(results[2][0], 'test@domain.co.uk')
        self.assertTrue(results[2][1])
        self.assertEqual(results[2][2], [])


if __name__ == '__main__':
    unittest.main()