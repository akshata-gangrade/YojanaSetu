"""Interactive CLI script to seed the initial administrator account.

Invariants:
- Asks for email and password at run time using getpass.
- Strictly requires password length >= 14 characters.
- Uses Argon2id (argon2-cffi) for cryptographic hashing.
- Refuses to execute if any administrator account already exists.
- Contains ZERO hardcoded default credentials.
- Never prints or logs plain passwords.
"""

import asyncio
import getpass
import re
import sys

from app.core.auth import hash_password
from app.db.mongo import MongoDBManager
from app.repositories.admin_repo import AdminRepository
from app.schemas.admin import AdminUserCreate
from app.schemas.enums import AdminRole

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


async def seed_first_admin() -> None:
    """Interactively provision the initial administrative account."""
    db = MongoDBManager.get_database()
    admin_repo = AdminRepository(db)

    # 1. Refuse to run if an administrator already exists
    existing_count = await admin_repo.count_admins()
    if existing_count > 0:
        print(
            "ERROR: Administrator account(s) already exist. "
            "seed_admin.py can only be run once for initial provisioning.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("=== YojanaSetu Initial Administrator Provisioning ===")

    # 2. Prompt for administrative email
    email = input("Enter admin email address: ").strip().lower()
    if not EMAIL_REGEX.match(email):
        print("ERROR: Invalid email address format.", file=sys.stderr)
        sys.exit(1)

    # 3. Prompt for password with getpass (at least 14 characters)
    password = getpass.getpass("Enter admin password (min 14 characters): ")
    if len(password) < 14:
        print(
            "ERROR: Password must be at least 14 characters in length.",
            file=sys.stderr,
        )
        sys.exit(1)

    confirm_password = getpass.getpass("Confirm admin password: ")
    if password != confirm_password:
        print("ERROR: Passwords do not match.", file=sys.stderr)
        sys.exit(1)

    # 4. Hash using Argon2id directly
    hashed = hash_password(password)

    # 5. Provision the administrator record with role=admin
    admin_create = AdminUserCreate(
        email=email,
        password_hash=hashed,
        role=AdminRole.ADMIN,
    )
    created = await admin_repo.create_admin(admin_create)

    print(
        f"SUCCESS: Initial administrator account created successfully: {created.email} (Role: {created.role.value})"
    )


async def _async_main() -> None:
    """Run initial admin seeding and close client inside one event loop with try/finally."""
    try:
        await seed_first_admin()
    finally:
        await MongoDBManager.close_client()


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
