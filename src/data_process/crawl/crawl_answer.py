from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime

# Cấu hình Chrome options
chrome_options = Options()
# chrome_options.add_argument('--headless')  # Chạy ẩn browser
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Khởi tạo WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Khởi tạo file log
log_file = open('data/raw/crawl_answers_log.txt', 'w', encoding='utf-8')

def write_log(message):
    """Ghi log vào cả terminal và file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    log_file.write(log_message + '\n')
    log_file.flush()

try:
    # Đọc file data.json
    write_log("Đọc file data.json...")
    with open('data/raw/question.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    write_log(f"Tổng số câu hỏi cần crawl câu trả lời: {len(questions_data)}")
    
    # Danh sách để lưu kết quả
    results = []
    
    # Lặp qua từng câu hỏi
    for index, item in enumerate(questions_data, 1):
        try:
            question = item['question']
            link = item['link']
            page = item['page']
            
            write_log(f"{'='*60}")
            write_log(f"[{index}/{len(questions_data)}] Đang crawl câu hỏi từ trang {page}")
            write_log(f"Link: {link}")
            
            # Truy cập link
            driver.get(link)
            
            # Đợi cho div class="article" xuất hiện
            wait = WebDriverWait(driver, 10)
            article_div = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.article"))
            )
            
            # Đợi thêm một chút để đảm bảo nội dung đã load xong
            time.sleep(1)
            
            # Lấy toàn bộ text trong div.article
            answer_text = article_div.text.strip()
            
            # Lấy các link context từ ul.list-document
            context_links = []
            try:
                # Tìm ul có class="list-document"
                list_document_ul = driver.find_element(By.CSS_SELECTOR, "ul.list-document")
                
                # Lấy tất cả các thẻ <a> bên trong
                links = list_document_ul.find_elements(By.TAG_NAME, "a")
                
                for link_element in links:
                    context_text = link_element.text.strip()
                    context_href = link_element.get_attribute('href')
                    
                    context_links.append({
                        'text': context_text,
                        'link': context_href
                    })
                
                write_log(f"Tìm thấy {len(context_links)} link context")
                
            except Exception as e:
                write_log(f"Không tìm thấy context links (có thể không có): {e}")
                context_links = []
            
            # Lưu vào kết quả
            results.append({
                'question': question,
                'link': link,
                'page': page,
                'answer': answer_text,
                'context_links': context_links
            })
            
            write_log(f"✓ Đã lấy câu trả lời (độ dài: {len(answer_text)} ký tự)")
            
            # Lưu vào file JSON sau mỗi câu hỏi (để tránh mất dữ liệu nếu có lỗi)
            with open('data/raw/answers.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Nghỉ một chút giữa các request để tránh quá tải server
            time.sleep(1)
            
        except Exception as e:
            write_log(f"✗ LỖI khi crawl câu hỏi {index}: {e}")
            # Vẫn lưu item nhưng để answer và context_links là rỗng
            results.append({
                'question': question,
                'link': link,
                'page': page,
                'answer': '',
                'context_links': []
            })
            continue
    
    # Tổng kết
    write_log(f"{'='*60}")
    write_log("TỔNG KẾT")
    write_log(f"{'='*60}")
    write_log(f"Tổng số câu hỏi: {len(questions_data)}")
    write_log(f"Số câu hỏi crawl thành công: {len([r for r in results if r['answer']])}")
    write_log(f"Số câu hỏi bị lỗi: {len([r for r in results if not r['answer']])}")
    
    # Thống kê context links
    total_context_links = sum(len(r['context_links']) for r in results)
    questions_with_context = len([r for r in results if r['context_links']])
    write_log(f"Tổng số context links: {total_context_links}")
    write_log(f"Số câu hỏi có context links: {questions_with_context}")
    
    write_log(f"Dữ liệu đã được lưu vào file: data_with_answers.json")
    write_log(f"Log đã được lưu vào file: crawl_answers_log.txt")

except Exception as e:
    write_log(f"LỖI NGHIÊM TRỌNG: {e}")
    import traceback
    error_trace = traceback.format_exc()
    write_log(error_trace)

finally:
    # Đóng browser và file log
    driver.quit()
    log_file.close()