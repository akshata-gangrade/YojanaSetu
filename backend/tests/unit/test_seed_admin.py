"""Unit tests for scripts/seed_admin.py provisioning logic."""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.auth import verify_password
from app.repositories.fakes import FakeAdminRepository
from app.schemas.admin import AdminUserCreate
from app.schemas.enums import AdminRole
from scripts.seed_admin import seed_first_admin


@pytest.mark.asyncio
async def test_seed_admin_refuses_if_admin_exists():
    """seed_admin refuses to execute and exits with code 1 if any admin exists."""
    fake_repo = FakeAdminRepository()
    # Add an admin
    await fake_repo.create_admin(
        AdminUserCreate(
            email="existing@yojanasetu.gov.in",
            password_hash="$argon2id$v=19$m=65536,t=3,p=4$mock_valid_length_hash_string",
            role=AdminRole.ADMIN,
        )
    )

    with patch("scripts.seed_admin.AdminRepository", return_value=fake_repo):
        with patch("scripts.seed_admin.MongoDBManager.get_database"):
            with pytest.raises(SystemExit) as exc_info:
                await seed_first_admin()
            assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_seed_admin_rejects_password_under_14_chars():
    """seed_admin requires at least 14 characters for password."""
    fake_repo = FakeAdminRepository()

    with patch("scripts.seed_admin.AdminRepository", return_value=fake_repo):
        with patch("scripts.seed_admin.MongoDBManager.get_database"):
            with patch("builtins.input", return_value="admin@yojanasetu.gov.in"):
                with patch("getpass.getpass", return_value="Short123!"):
                    with pytest.raises(SystemExit) as exc_info:
                        await seed_first_admin()
                    assert exc_info.value.code == 1


@pytest.mark.asyncio
async def test_seed_admin_success_with_argon2id():
    """seed_admin successfully seeds the first admin with Argon2id hash."""
    fake_repo = FakeAdminRepository()
    test_email = "newadmin@yojanasetu.gov.in"
    test_password = "ValidAdminPassword2026!#"

    with patch("scripts.seed_admin.AdminRepository", return_value=fake_repo):
        with patch("scripts.seed_admin.MongoDBManager.get_database"):
            with patch("builtins.input", return_value=test_email):
                with patch("getpass.getpass", side_effect=[test_password, test_password]):
                    await seed_first_admin()

    admin = await fake_repo.get_by_email(test_email)
    assert admin is not None
    assert admin.email == test_email
    assert admin.role == AdminRole.ADMIN
    assert verify_password(test_password, admin.password_hash) is True
