import os
import shutil

import argparse

# Sử dụng argparse để nhận đường dẫn từ dòng lệnh
parser = argparse.ArgumentParser(description="Lọc những người có ít nhất 2 ảnh từ tập dữ liệu.")
parser.add_argument("--input_path", type=str, default='data\lfw\lfw-deepfunneled\lfw-deepfunneled', help="Đường dẫn đến thư mục dữ liệu gốc (ví dụ: lfw)")
parser.add_argument("--output_path", type=str, default='data/demo_data', help="Đường dẫn đến thư mục lưu kết quả")
args = parser.parse_args()

lfw_path = args.input_path
work_dir = args.output_path
os.makedirs(work_dir, exist_ok=True)


# Tạo thư mục làm việc nếu chưa có
os.makedirs(work_dir, exist_ok=True)

# Lấy danh sách tất cả các thư mục con (tên người)
people = [d for d in os.listdir(lfw_path) if os.path.isdir(os.path.join(lfw_path, d))]

count = 0
for person in people:
    person_path = os.path.join(lfw_path, person)
    images = os.listdir(person_path)
    
    # Chỉ lấy những người có ít nhất 2 ảnh
    if len(images) >= 2:
        # Copy cả folder của người đó sang thư mục làm việc
        shutil.copytree(person_path, os.path.join(work_dir, person))
        count += 1

print(f"Filter completed! There are {count} people having at least 2 images to demo.")