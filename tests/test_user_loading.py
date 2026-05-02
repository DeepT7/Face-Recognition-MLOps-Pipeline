#!/usr/bin/env python3
"""
Test script to verify all users are loaded from Supabase
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_user_loading():
    """Test that all users are loaded from Supabase"""
    print("🔍 Testing user loading from Supabase...")

    # Initialize Supabase client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials in .env file")
        return

    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        # Test the old method (limited to 1000)
        print("\n📊 Testing old method (limited)...")
        response_limited = supabase_client.table("face_users").select("id, name").execute()
        limited_count = len(response_limited.data)
        print(f"Old method returned: {limited_count} users")

        # Test the new method (paginated)
        print("\n📊 Testing new method (paginated)...")
        all_users = []
        page_size = 1000
        offset = 0

        while True:
            response = supabase_client.table("face_users").select("id, name").range(offset, offset + page_size - 1).execute()
            users = response.data

            if not users:
                break

            all_users.extend(users)
            offset += page_size

            # Safety check to prevent infinite loops
            if len(users) < page_size:
                break

        paginated_count = len(all_users)
        print(f"New method returned: {paginated_count} users")

        # Summary
        print("\n📈 Summary:")
        print(f"  Limited query: {limited_count} users")
        print(f"  Paginated query: {paginated_count} users")

        if paginated_count > limited_count:
            print(f"  ✅ Fixed! Now loading {paginated_count - limited_count} more users")
        elif paginated_count == limited_count:
            print("  ℹ️  Both methods returned the same count (dataset ≤ 1000 users)")
        else:
            print("  ⚠️  Unexpected: paginated count is less than limited count")

        return paginated_count

    except Exception as e:
        print(f"❌ Error testing user loading: {e}")
        return None

if __name__ == "__main__":
    count = test_user_loading()
    if count:
        print(f"\n🎉 Successfully loaded {count} users from Supabase!")
    else:
        print("\n❌ Failed to test user loading")
        sys.exit(1)