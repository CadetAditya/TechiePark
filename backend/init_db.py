"""
Techie Park Database Initialization CLI Script.
Run this script to verify your MySQL connection and initialize all tables.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.config import settings
from backend.app.database import init_db, get_connection

def main():
    print("=" * 60)
    print(" TECHIE PARK - MySQL Database Setup")
    print("=" * 60)
    print(f"Host:     {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"User:     {settings.DB_USER}")
    print(f"Database: {settings.DB_NAME}")
    print("-" * 60)

    try:
        print("Testing MySQL connection...")
        conn = get_connection(include_db=False)
        print("✓ Connected to MySQL server successfully!")
        conn.close()

        print("\nCreating/verifying database & tables...")
        success = init_db()
        if success:
            print("\n✓ SUCCESS: Database & tables are ready!")
        else:
            print("\n✗ Failed to create tables. Check logs above.")
    except Exception as e:
        print(f"\n✗ Error: Could not connect to MySQL server: {e}")
        print("\nTip: Please update DB_PASSWORD in your .env file with your MySQL root password.")
        sys.exit(1)

if __name__ == "__main__":
    main()

