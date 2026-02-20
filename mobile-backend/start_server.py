import uvicorn
import os

if __name__ == "__main__":
    # Ensure database URL is set (fallback to SQLite)
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///farmtwin.db"
    
    print("=" * 60)
    print("🚀 Starting FarmTwin360 Mobile Backend API")
    print("=" * 60)
    print(f"📡 Server will be available at:")
    print(f"   - Local:   http://127.0.0.1:8000")
    print(f"   - Network: http://0.0.0.0:8000")
    print("=" * 60)
    print("📱 Mobile App Configuration:")
    print("   Update services/api.js with your local IP:")
    print("   const API_URL = 'http://YOUR_IP:8000/api';")
    print("=" * 60)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
