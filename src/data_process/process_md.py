import json
import re
from tqdm import tqdm
import pandas as pd

def split_markdown(md_text):
    mapping = {
            'Trình tự thực hiện': 'Steps',
            'Cách thức thực hiện': 'Methods',
            'Thành phần hồ sơ': 'Documents',
            'Cơ quan thực hiện': 'Agency',
            'Yêu cầu, điều kiện thực hiện': 'Conditions'
    }
    sections = {}
    section = ""
    current = None

    for line in md_text.splitlines():
        remove_line = [None,'','.']
        if re.match(r'^# (?!#)', line):   
            sections["Title"] = line[2:].strip()

        elif re.match(r'^## (?!#)', line):
            if current:
                sections[mapping[current]] = section
            current = line[3:].strip()
            section = ""
            
        elif line in remove_line:
            continue
        else:
            section += line + "\n"

    return sections
    

if __name__ == '__main__':
    file_path = '/home/schaffen/Workspace/Project/SMFH/data/processed/qa_context_cleaned.json'
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    samples = []
    for item in tqdm(data, desc="Processing samples"):
        context = item['context'][0]
        context = split_markdown(context)
        context['Question'] = item['question']
        context['Answer'] = item['answer'].removeprefix("Trả lời:\n")
        samples.append(context)
    
    with open("/home/schaffen/Workspace/Project/SMFH/data/processed/sections.json", "w", encoding="utf-8") as f: 
        json.dump(samples, f, indent=2, ensure_ascii=False)
    
    df = pd.DataFrame(samples)

    df.to_parquet(
        "/home/schaffen/Workspace/Project/SMFH/data/processed/samples.parquet",
        engine="pyarrow",
        index=False
    )
