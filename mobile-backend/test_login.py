"""Test script to diagnose login issues"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import User
import bcrypt

def test_database():
    """Test database connection and user data"""
    print("=" * 60)
    print("Testing Database Connection and Users")
    print("=" * 60)
    
    try:
        db = get_db()
        
        # Get all users
        users = db.query(User).all()
        print(f"\n✅ Database connected successfully")
        print(f"📊 Found {len(users)} users in database\n")
        
        if len(users) == 0:
            print("⚠️  No users found! Database needs initialization.")
            print("Run the Streamlit app first to create demo data.")
            return
        
        # Display all users
        print("-" * 60)
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Role':<10}")
        print("-" * 60)
        for user in users:
            print(f"{user.id:<5} {user.name:<20} {user.email:<30} {user.role:<10}")
        print("-" * 60)
        
        # Test password verification
        print("\n" + "=" * 60)
        print("Testing Password Verification")
        print("=" * 60)
        
        test_credentials = [
            ("admin@farmtwin.com", "admin123"),
            ("manager@farmtwin.com", "manager123"),
            ("worker@farmtwin.com", "worker123"),
        ]
        
        for email, password in test_credentials:
            user = db.query(User).filter(User.email == email).first()
            if user:
                try:
                    password_valid = bcrypt.checkpw(
                        password.encode('utf-8'),
                        user.password_hash.encode('utf-8')
                    )
                    status = "✅ VALID" if password_valid else "❌ INVALID"
                    print(f"\n{email}")
                    print(f"  Password: {password}")
                    print(f"  Status: {status}")
                    print(f"  Hash (first 50 chars): {user.password_hash[:50]}...")
                except Exception as e:
                    print(f"\n{email}")
                    print(f"  ❌ ERROR: {str(e)}")
            else:
                print(f"\n{email}")
                print(f"  ❌ User not found in database")
        
        db.close()
        
        print("\n" + "=" * 60)
        print("Testing Complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Database Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()
