"""Initialize database and create demo users for mobile backend"""
import sys
import os

# Set minimal environment to avoid Streamlit warnings
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database, create_demo_data

def main():
    print("=" * 60)
    print("🔧 Initializing FarmTwin360 Database")
    print("=" * 60)
    
    try:
        print("\n[1/2] Creating database tables...")
        init_database()
        print("✅ Database tables created successfully")
        
        print("\n[2/2] Creating demo users and sample data...")
        create_demo_data()
        print("✅ Demo data created successfully")
        
        print("\n" + "=" * 60)
        print("🎉 Database initialization complete!")
        print("=" * 60)
        print("\n📋 Demo User Credentials:")
        print("-" * 60)
        print("Admin:   admin@farmtwin.com   / admin123")
        print("Manager: manager@farmtwin.com / manager123")
        print("Worker:  worker@farmtwin.com  / worker123")
        print("Visitor: visitor@farmtwin.com / visitor123")
        print("Vet:     vet@farmtwin.com     / vet123")
        print("Auditor: auditor@farmtwin.com / auditor123")
        print("-" * 60)
        print("\n✨ You can now start the mobile backend server!")
        print("   Run: python start_server.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
