import os

import pytest
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def test_user_loading():
    """Verify paginated Supabase loading when credentials are available."""

    if os.getenv("RUN_SUPABASE_TESTS") != "1":
        pytest.skip("Set RUN_SUPABASE_TESTS=1 to run the live Supabase integration test")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        pytest.skip("SUPABASE_URL and SUPABASE_KEY are not configured")

    supabase_client = create_client(supabase_url, supabase_key)

    response_limited = supabase_client.table("face_users").select("id, name").execute()
    limited_count = len(response_limited.data)

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

        if len(users) < page_size:
            break

    assert len(all_users) >= limited_count
