def load_pem_private_key(
    pem_private_key: str, password: Optional[str] = None
):
    return cryptography.load_pem_private_key(pem_private_key, password)

# Rest of the code...