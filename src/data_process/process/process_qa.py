import json

    
def main():
  
    with open('data/raw/answers.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    print(f"Tổng số câu hỏi cần crawl câu trả lời: {len(questions_data)}")
    
    # Lọc ra các câu hỏi mà context links không phải list rỗng
    context_qa = [item for item in questions_data if len(item['context_links']) > 0]
    
    
    # context_qa = [item for item in questions_data if item['context_links'] is not None]
    print(f"Số câu hỏi có context_links: {len(context_qa)}")
    
    with open('data/processed/qa.json', 'w', encoding='utf-8') as f:
        json.dump(context_qa, f, ensure_ascii=False, indent=2)
        
if __name__ == "__main__":
    main()