from asyncio.log import logger

from flask import logging
import numpy as np 
import pandas as pd 
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import sys 
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import SYSTEM_DB_PATH, EMBEDDINGS_PATH
# Load environment variables from a .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Supabase credentials (found in Project Settings > API)
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(URL, KEY)

def migrate_data(csv_path):
    df = pd.read_csv(csv_path)
    embeddings_dict = np.load(EMBEDDINGS_PATH, allow_pickle=True).item()

    for _, row in df.iterrows():
        user_id = str(row['person_id']).zfill(6)  # Ensure user_id is a zero-padded string
        user_name = row['person_name']

        embedding = embeddings_dict.get(user_id)
        if embedding is not None:
            embedding_list = embedding['embedding'].tolist()  # Convert numpy array to list
        else:
            logger.warning(f"No embedding found for user_id={user_id}, user_name={user_name}. Skipping embedding migration for this user.")
            embedding_list = None

        relative_gallery_path = f"gallery/{user_name}_{user_id}.jpg"  # Assuming you have a consistent naming convention for images

        data = {
            "id": user_id,
            "name": user_name,
            "embedding": embedding_list,
            "gallery_path": relative_gallery_path
        }

        # Upsert the data into the 'users' table in Supabase
        try:
            response = supabase.table("face_users").upsert(data).execute()
        except Exception as e:
            logger.error(f"Error occurred while migrating user {user_id} - {user_name}: {e}")
            continue

if __name__ == "__main__":
    migrate_data(SYSTEM_DB_PATH)