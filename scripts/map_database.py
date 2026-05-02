import pandas as pd
import os

records = []
for i, img_name in enumerate(sorted(os.listdir(gallery_dir))):
    person_name = img_name.replace("_G.jpg", "")
    person_id = f"{i + 1:06d}"
    records.append({
        "person_id": person_id,
        "person_name": person_name,
        "gallery_path": os.path.join('gallery', img_name)
    })

df = pd.DataFrame(records)
df.to_csv(os.path.join(base_dest, 'system_db.csv'), index=False)