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
log_file = open('crawl_log.txt', 'w', encoding='utf-8')

def write_log(message):
    """Ghi log vào cả terminal và file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    log_file.write(log_message + '\n')
    log_file.flush()

try:
    # Truy cập trang web
    url = "https://dichvucong.gov.vn/p/home/dvc-cau-hoi-pho-bien.html"
    driver.get(url)
    
    write_log("Bắt đầu crawl dữ liệu...")
    write_log(f"URL: {url}")
    
    wait = WebDriverWait(driver, 10)
    all_questions = []
    current_page = 1
    
    while True:
        write_log(f"{'='*50}")
        write_log(f"Đang crawl trang {current_page}")
        
        # Đợi cho đến khi div với class="list-document -question" xuất hiện
        list_document_div = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-document.-question"))
        )
        
        # Đợi thêm một chút để đảm bảo trang đã load xong
        time.sleep(1)
        
        # Lấy tất cả các thẻ <a> với class="item" bên trong div
        questions = list_document_div.find_elements(By.CSS_SELECTOR, "a.item")
        
        write_log(f"Số câu hỏi trong trang {current_page}: {len(questions)}")
        
        # Lặp qua từng câu hỏi và lấy text + link
        for question in questions:
            question_text = question.text.strip()
            question_link = question.get_attribute('href')
            
            # Lưu vào list
            all_questions.append({
                'question': question_text,
                'link': question_link,
                'page': current_page
            })
        
        # Lưu vào file JSON sau mỗi trang
        with open('question.json', 'w', encoding='utf-8') as f:
            json.dump(all_questions, f, ensure_ascii=False, indent=2)
        
        write_log(f"Đã lưu {len(all_questions)} câu hỏi vào question.json")
        
        # Tìm nút "Next" (trang tiếp theo)
        try:
            # Tìm li có class="next" và jp-role="next"
            next_button = driver.find_element(By.CSS_SELECTOR, 'li.next[jp-role="next"]')
            
            # Kiểm tra xem nút next có bị disable không
            if 'disabled' in next_button.get_attribute('class'):
                write_log("Đã crawl hết tất cả các trang!")
                break
            
            # Click vào thẻ <a> bên trong li.next
            next_link = next_button.find_element(By.TAG_NAME, 'a')
            
            # Scroll đến nút next để đảm bảo nó visible
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(0.5)
            
            # Click vào nút next
            next_link.click()
            write_log(f"Chuyển sang trang {current_page + 1}...")
            
            current_page += 1
            
            # Đợi trang mới load
            time.sleep(2)
            
        except Exception as e:
            write_log("Đã crawl hết tất cả các trang (không tìm thấy nút Next)")
            break
    
    # Tổng kết
    write_log(f"{'='*50}")
    write_log("TỔNG KẾT")
    write_log(f"{'='*50}")
    write_log(f"Tổng số trang đã crawl: {current_page}")
    write_log(f"Tổng số câu hỏi: {len(all_questions)}")
    write_log(f"Dữ liệu đã được lưu vào file: data.json")
    write_log(f"Log đã được lưu vào file: crawl_log.txt")

except Exception as e:
    write_log(f"LỖI: {e}")
    import traceback
    error_trace = traceback.format_exc()
    write_log(error_trace)

finally:
    # Đóng browser và file log
    driver.quit()
    log_file.close()