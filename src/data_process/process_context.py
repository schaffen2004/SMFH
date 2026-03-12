import json

def main():
    with open('data/raw/qa_context.json', 'r') as f:
        data = json.load(f)
    
    print(len(data))
    
    qa_context = []
    
    for item in data:
        question = item['question']
        answer = item['answer']
        contexts = [context['markdown'] for context in item['context_data']]
        qa_context.append({
            'question': question,
            'answer': answer,
            'context': contexts
        })
    with open('data/processed/qa_with_context.json', 'w', encoding='utf-8') as f:
        json.dump(qa_context, f, ensure_ascii=False, indent=2)
    
    
if __name__ == "__main__":
    main()