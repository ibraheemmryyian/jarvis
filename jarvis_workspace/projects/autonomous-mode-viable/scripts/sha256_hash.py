import hashlib

def sha256_hash(data: str) -> str:
    """
    Generate a SHA-256 hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        str: The SHA-256 hash value as hexadecimal string.
    """
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()

def md5_hash(data: str) -> str:
    """
    Generate an MD5 hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        str: The MD5 hash value as hexadecimal string.
    """
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()

def sha1_hash(data: str) -> str:
    """
    Generate a SHA-1 hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        str: The SHA-1 hash value as hexadecimal string.
    """
    sha1 = hashlib.sha1()
    sha1.update(data.encode('utf-8'))
    return sha1.hexdigest()

def blake2s_hash(data: str) -> str:
    """
    Generate a BLAKE2s hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        str: The BLAKE2s hash value as hexadecimal string.
    """
    blake2s = hashlib.blake2s()
    blake2s.update(data.encode('utf-8'))
    return blake2s.hexdigest()

def sha3_256_hash(data: str) -> str:
    """
    Generate a SHA-3 256-bit hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        str: The SHA-3 256-bit hash value as hexadecimal string.
    """
    sha3_256 = hashlib.sha3_256()
    sha3_256.update(data.encode('utf-8'))
    return sha3_256.hexdigest()

def sha3_512_hash(data: str) -> str:
    """
    Generate a SHA-3 512-bit hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        str: The SHA-3 512-bit hash value as hexadecimal string.
    """
    sha3_512 = hashlib.sha3_512()
    sha3_512.update(data.encode('utf-8'))
    return sha3_512.hexdigest()

def shake_128_hash(data: str) -> tuple[str, str]:
    """
    Generate a SHAKE-128 hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        tuple[str, str]: A tuple containing the SHAKE-128 256-bit and 512-bit hash values as hexadecimal strings.
    """
    shake_128 = hashlib.shake_128()
    shake_128.update(data.encode('utf-8'))
    return (shake_128.hexdigest(32), shake_128.hexdigest(64))

def shake_256_hash(data: str) -> tuple[str, str]:
    """
    Generate a SHAKE-256 hash of the provided data.
    
    Args:
        data (str): The input data to generate a hash for.
        
    Returns:
        tuple[str, str]: A tuple containing the SHAKE-256 160-bit and 320-bit hash values as hexadecimal strings.
    """
    shake_256 = hashlib.shake_256()
    shake_256.update(data.encode('utf-8'))
    return (shake_256.hexdigest(20), shake_256.hexdigest(40))