import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from datetime import timedelta

def test_password_hashing_and_verification():
    raw = "supersecret" 
    hashed = hash_password(raw) 
    assert hashed != raw 
    assert verify_password(raw, hashed) 
    assert not verify_password("wrongpass", hashed) 
     
     
def test_jwt_token_generation_and_decoding(): 
    token = create_access_token("user123", expires_delta=timedelta(minutes=5)) 
    decoded = decode_access_token(token) 
    assert decoded["sub"] == "user123" 
    assert "exp" in decoded

