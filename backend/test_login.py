#!/usr/bin/env python3
"""Test login flow."""

import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.security import verify_password

# Connect to DB
engine = create_engine("sqlite:///./dev.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get user
result = db.execute(
    text("SELECT email, hashed_password, is_active FROM users WHERE email = :email"),
    {"email": "admin@newsreader.local"}
)
user = result.fetchone()

if not user:
    print("❌ User not found!")
    sys.exit(1)

email, hashed_password, is_active = user
print(f"✅ User found: {email}")
print(f"   Active: {is_active}")
print(f"   Hash: {hashed_password[:20]}...")

# Test password
test_password = "admin123"
print(f"\nTesting password: '{test_password}'")

try:
    result = verify_password(test_password, hashed_password)
    if result:
        print("✅ Password verification PASSED!")
    else:
        print("❌ Password verification FAILED!")
except Exception as e:
    print(f"❌ Error during verification: {e}")

db.close()
