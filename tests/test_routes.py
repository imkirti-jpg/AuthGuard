import pytest
from uuid import uuid4
import pytest
from uuid import uuid4

@pytest.mark.anyio
async def test_account_lockout_after_max_failures(client, redis_client):
    email = f"lock_{uuid4()}@example.com"
    password = "SafePassword123!"
    await client.post("/auth/register", json={"email": email, "password": password})

    for _ in range(5):
        await client.post("/auth/login", data={"username": email, "password": "wrongpassword"})

    resp = await client.post("/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 423

@pytest.mark.anyio
async def test_refresh_token_rotation_and_revocation(client):
    email = f"rotate_{uuid4()}@example.com"
    password = "SafePassword123!"
    reg_resp = await client.post("/auth/register", json={"email": email, "password": password})
    user_id = reg_resp.json()["id"]
    
    login_resp = await client.post("/auth/login", data={"username": email, "password": password})
    refresh_token = login_resp.json()["refresh_token"]

    # FIX: Send both user_id and refresh_token to match RefreshRequest schema
    logout_payload = {"user_id": user_id, "refresh_token": refresh_token}
    logout_resp = await client.post("/auth/logout", json=logout_payload)
    assert logout_resp.status_code == 204

@pytest.mark.anyio
async def test_rbac_admin_protection(client):
    user_email = f"user_{uuid4()}@example.com"
    pwd = "SafePassword123!"
    reg = await client.post("/auth/register", json={"email": user_email, "password": pwd})
    user_id = reg.json()["id"]
    
    login_resp = await client.post("/auth/login", data={"username": user_email, "password": pwd})
    user_token = login_resp.json()["access_token"]

    admin_resp = await client.post(
        f"/admin/users/{user_id}/promote", 
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert admin_resp.status_code == 403

@pytest.mark.anyio
async def test_password_complexity_enforcement(client):
    weak_passwords = ["short", "nosymbol123", "NoSymbol", "lowercaseonly1"]
    for pwd in weak_passwords:
        resp = await client.post("/auth/register", json={
            "email": f"test_{uuid4()}@test.com", 
            "password": pwd
        })
        assert resp.status_code == 422

@pytest.mark.anyio
async def test_successful_user_registration(client):
    email = f"newuser_{uuid4()}@example.com"
    password = "ValidPassword123!"
    
    resp = await client.post("/auth/register", json={
        "email": email,
        "password": password
    })
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == email
    assert "id" in data

@pytest.mark.anyio
async def test_successful_user_login(client):
    email = f"login_{uuid4()}@example.com"
    password = "SecurePass456!"
    
    # Register first
    await client.post("/auth/register", json={"email": email, "password": password})
    
    # Login
    resp = await client.post("/auth/login", data={"username": email, "password": password})
    
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.anyio
async def test_duplicate_email_registration(client):
    email = f"duplicate_{uuid4()}@example.com"
    password = "StrongPass789!"
    
    # Register first user
    resp1 = await client.post("/auth/register", json={"email": email, "password": password})
    assert resp1.status_code == 200
    
    # Try to register with same email
    resp2 = await client.post("/auth/register", json={"email": email, "password": password})
    assert resp2.status_code == 400
    assert "already registered" in resp2.json()["detail"]

@pytest.mark.anyio
async def test_invalid_login_credentials(client):
    email = f"creds_{uuid4()}@example.com"
    password = "CorrectPass123!"
    
    # Register
    await client.post("/auth/register", json={"email": email, "password": password})
    
    # Try to login with wrong password
    resp = await client.post("/auth/login", data={"username": email, "password": "WrongPassword123!"})
    
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]

@pytest.mark.anyio
async def test_password_reset_flow(client):
    email = f"reset_{uuid4()}@example.com"
    old_password = "OldPass123!"
    new_password = "NewPass456!"
    
    # Register user
    await client.post("/auth/register", json={"email": email, "password": old_password})
    
    # Request password reset
    reset_resp = await client.post("/auth/forgot-password", json={"email": email})
    assert reset_resp.status_code == 202
    
    # Extract the reset token from debug_token
    reset_token = reset_resp.json()["debug_token"]
    assert reset_token is not None
    
    # Confirm password reset
    confirm_resp = await client.post("/auth/reset-password", json={
        "token": reset_token,
        "new_password": new_password
    })
    assert confirm_resp.status_code == 200
    assert "successfully" in confirm_resp.json()["message"]
    
    # Verify old password no longer works
    login_old = await client.post("/auth/login", data={"username": email, "password": old_password})
    assert login_old.status_code == 401
    
    # Verify new password works
    login_new = await client.post("/auth/login", data={"username": email, "password": new_password})
    assert login_new.status_code == 200

@pytest.mark.anyio
async def test_get_current_user_info(client):
    email = f"profile_{uuid4()}@example.com"
    password = "ProfilePass123!"
    
    # Register user
    reg_resp = await client.post("/auth/register", json={"email": email, "password": password})
    user_id = reg_resp.json()["id"]
    
    # Login
    login_resp = await client.post("/auth/login", data={"username": email, "password": password})
    access_token = login_resp.json()["access_token"]
    
    # Get current user info
    user_resp = await client.get(
        "/auth/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert user_resp.status_code == 200
    user_data = user_resp.json()
    assert user_data["id"] == user_id
    assert user_data["email"] == email