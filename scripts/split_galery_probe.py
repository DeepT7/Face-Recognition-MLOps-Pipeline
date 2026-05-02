import os
import shutil
import pandas as pd
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sử dụng argparse để nhận đường dẫn từ dòng lệnh   
parser = argparse.ArgumentParser(description="Filter people having more than 1 images.")
parser.add_argument("--demo_dir", type=str, default='data/demo_data', help="Path to the source directory.")
parser.add_argument("--base_dest", type=str, default='data/final_setup', help="Path to the destination directory.")
args = parser.parse_args()

# Đường dẫn thư mục sau khi đã lọc (chứa các sub-folders của từng người)
demo_dir = args.demo_dir
base_dest = args.base_dest

gallery_dir = os.path.join(base_dest, 'gallery')
probe_dir = os.path.join(base_dest, 'probe')
person_names = os.listdir(demo_dir)

os.makedirs(gallery_dir, exist_ok=True)
os.makedirs(probe_dir, exist_ok=True)

# This list will hold the records for our database CSV
db_records = []

# Duyệt qua từng người trong thư mục đã lọc
for i, person_name in enumerate(sorted(person_names)):
    person_path = os.path.join(demo_dir, person_name)
    if not os.path.isdir(person_path):
        continue
    
    # Lấy danh sách ảnh và sắp xếp để đảm bảo tính nhất quán
    images = sorted(os.listdir(person_path))
    if not images:
        logger.warning(f"Warning: Skipping empty directory: {person_path}")
        # Clean up the empty directory
        os.rmdir(person_path)
        continue

    try:
        # Generate a new 6-digit person ID
        person_id = f"{i + 1:06d}"

        # 1. Chuyển ảnh đầu tiên vào Gallery
        # Rename the file to the person's ID for a unique, stable identifier
        gallery_img_name = f"{person_name}_{person_id}.jpg"
        shutil.move(os.path.join(person_path, images[0]), 
                    os.path.join(gallery_dir, gallery_img_name))
        
        # 2. Chuyển tất cả các ảnh còn lại vào Probe
        os.makedirs(os.path.join(probe_dir, person_name), exist_ok=True)
        for i in range(1, len(images)):
            # probe_img_name = f"{person_name}_P_{i}.jpg"
            shutil.move(os.path.join(person_path, images[i]), 
                        os.path.join(probe_dir, person_name, images[i]))
            
        # Remove empty folder after moving
        os.rmdir(person_path)

        # Add the new person's info to our records list
        db_records.append({
            "person_id": person_id,
            "person_name": person_name,
            "gallery_path": os.path.join('gallery', gallery_img_name)
        })
    except (IndexError, FileNotFoundError) as e:
        logger.error(f"Error processing {person_path}: {e}. Skipping.")

logger.info(f"Finished and splitted images into {gallery_dir} and {probe_dir}")

logger.info("Creating system database...")
df = pd.DataFrame(db_records)
df.to_csv(os.path.join(base_dest, 'system_db.csv'), index=False)
logger.info(f"Database saved to {os.path.join(base_dest, 'system_db.csv')}")