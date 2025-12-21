#!/usr/bin/env python3
"""
Email address validation module.

This module provides functions to validate email addresses using regular expressions
and additional checks for common email format issues.
"""

import re
from typing import Tuple, List


def is_valid_email(email: str) -> bool:
    """
    Validate an email address using regex pattern matching.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.

    Examples:
        >>> is_valid_email('user@example.com')
        True
        >>> is_valid_email('invalid.email')
        False
    """
    # Basic regex pattern for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return bool(re.match(pattern, email))


def validate_email_detailed(email: str) -> Tuple[bool, List[str]]:
    """
    Validate an email address with detailed feedback.

    Args:
        email (str): The email address to validate.

    Returns:
        Tuple[bool, List[str]]: A tuple containing a boolean indicating validity
        and a list of error messages if invalid.

    Examples:
        >>> validate_email_detailed('user@example.com')
        (True, [])
        >>> validate_email_detailed('invalid.email')
        (False, ['Email must contain @ symbol'])
    """
    errors = []
    
    # Check if email is empty
    if not email:
        errors.append('Email cannot be empty')
        return False, errors
    
    # Check for @ symbol
    if '@' not in email:
        errors.append('Email must contain @ symbol')
        return False, errors
    
    # Split into local and domain parts
    parts = email.split('@')
    if len(parts) != 2:
        errors.append('Email must contain exactly one @ symbol')
        return False, errors
    
    local_part, domain_part = parts
    
    # Check local part (before @)
    if not local_part:
        errors.append('Local part cannot be empty')
    
    if len(local_part) > 64:
        errors.append('Local part must be less than 64 characters')
    
    # Check domain part (after @)
    if not domain_part:
        errors.append('Domain part cannot be empty')
    
    if len(domain_part) > 255:
        errors.append('Domain part must be less than 255 characters')
    
    # Check for valid domain format
    if '.' not in domain_part:
        errors.append('Domain must contain at least one dot')
    
    # Check TLD (top-level domain)
    tld = domain_part.split('.')[-1]
    if len(tld) < 2:
        errors.append('Top-level domain must be at least 2 characters long')
    
    # Use regex for final validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        errors.append('Email format is invalid')
    
    return len(errors) == 0, errors


def validate_email_list(emails: List[str]) -> List[Tuple[str, bool, List[str]]]:
    """
    Validate a list of email addresses.

    Args:
        emails (List[str]): A list of email addresses to validate.

    Returns:
        List[Tuple[str, bool, List[str]]]: A list of tuples containing the email,
        validity status, and error messages.

    Examples:
        >>> validate_email_list(['user@example.com', 'invalid.email'])
        [('user@example.com', True, []), ('invalid.email', False, ['Email format is invalid'])]
    """
    results = []
    
    for email in emails:
        is_valid, errors = validate_email_detailed(email)
        results.append((email, is_valid, errors))
    
    return results


if __name__ == '__main__':
    # Example usage
    test_emails = [
        'user@example.com',
        'invalid.email',
        'test@domain.co.uk',
        '',
        '@example.com',
        'user@',
        'user..name@example.com',
        'user@domain',
        'valid.email+tag@example.org'
    ]
    
    print('Email Validation Results:')
    print('-' * 50)
    
    for email in test_emails:
        is_valid, errors = validate_email_detailed(email)
        status = '✓ Valid' if is_valid else '✗ Invalid'
        print(f'{email:<30} {status}')
        
        if errors:
            for error in errors:
                print(f'  - {error}')
        print()
