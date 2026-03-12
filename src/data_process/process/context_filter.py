import json

# Đọc file
with open("data/processed/qa_with_context.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Duyệt qua tất cả sample
for sample in data:
    if "context" in sample and isinstance(sample["context"], list):
        # Lọc bỏ phần tử "# \n\n"
        sample["context"] = [
            c for c in sample["context"]
            if c != "# \n\n"
        ]

for sample in data:
    if "" in sample['context']:
        sample["context"].remove("")
        
# Ghi lại file sau khi xử lý
with open("data/processed/qa_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done cleaning!")
