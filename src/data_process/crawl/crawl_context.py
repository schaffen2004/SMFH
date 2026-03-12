from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
import re

# Cấu hình Chrome options
chrome_options = Options()
# chrome_options.add_argument('--headless')  # Chạy ẩn browser
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Khởi tạo WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Khởi tạo file log
log_file = open('logs/crawl_context_log.txt', 'w', encoding='utf-8')

def write_log(message):
    """Ghi log vào cả terminal và file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    log_file.write(log_message + '\n')
    log_file.flush()

def convert_table_to_markdown(table_element):
    """Chuyển đổi bảng HTML sang Markdown"""
    md_table = "\n"
    
    try:
        # Lấy header
        try:
            thead = table_element.find_element(By.TAG_NAME, "thead")
            header_cells = thead.find_elements(By.TAG_NAME, "th")
            
            # Tạo header row
            headers = [cell.text.strip() for cell in header_cells]
            if headers and any(headers):  # Chỉ tạo header nếu có nội dung
                md_table += "| " + " | ".join(headers) + " |\n"
                md_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        except:
            pass
        
        # Lấy body
        tbody = table_element.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_texts = [cell.text.strip().replace("\n", " ") for cell in cells]
            if cell_texts and any(cell_texts):  # Chỉ thêm row nếu có nội dung
                md_table += "| " + " | ".join(cell_texts) + " |\n"
        
        md_table += "\n"
    except Exception as e:
        write_log(f"⚠ Lỗi khi chuyển đổi bảng: {e}")
    
    return md_table

def process_element_content(element):
    """Xử lý nội dung của một element và chuyển sang markdown"""
    markdown = ""
    
    try:
        # Xử lý paragraphs
        paragraphs = element.find_elements(By.TAG_NAME, "p")
        for p in paragraphs:
            text = p.text.strip()
            if text:
                markdown += f"{text}\n\n"
        
        # Xử lý tables
        tables = element.find_elements(By.TAG_NAME, "table")
        for table in tables:
            markdown += convert_table_to_markdown(table)
        
        # Xử lý unordered lists
        ul_lists = element.find_elements(By.TAG_NAME, "ul")
        for ul in ul_lists:
            items = ul.find_elements(By.TAG_NAME, "li")
            for item in items:
                text = item.text.strip()
                if text:
                    markdown += f"- {text}\n"
            markdown += "\n"
        
        # Xử lý ordered lists
        ol_lists = element.find_elements(By.TAG_NAME, "ol")
        for ol in ol_lists:
            items = ol.find_elements(By.TAG_NAME, "li")
            for idx, item in enumerate(items, 1):
                text = item.text.strip()
                if text:
                    markdown += f"{idx}. {text}\n"
            markdown += "\n"
    
    except Exception as e:
        write_log(f"⚠ Lỗi khi xử lý nội dung element: {e}")
    
    return markdown

def crawl_context_page(url):
    """Crawl một trang context và chuyển sang markdown"""
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        time.sleep(1)
        
        markdown_content = ""
        
        # Lấy tiêu đề chính
        try:
            main_title = driver.find_element(By.CSS_SELECTOR, "h1.main-title")
            title_text = main_title.text.strip()
            markdown_content += f"# {title_text}\n\n"
        except:
            pass
        
        # Lấy container chính
        try:
            main_container = driver.find_element(By.CSS_SELECTOR, "div.col-sm-8.col-xs-12")
        except:
            write_log("⚠ Không tìm thấy container chính")
            return markdown_content
        
        # Lấy tất cả các h2 sections (động)
        h2_elements = main_container.find_elements(By.CSS_SELECTOR, "h2.main-title-sub")
        
        write_log(f"  Tìm thấy {len(h2_elements)} sections")
        
        for h2_index, h2 in enumerate(h2_elements):
            section_title = h2.text.strip()
            if not section_title:
                continue
                
            markdown_content += f"\n## {section_title}\n\n"
            write_log(f"    - Processing section: {section_title}")
            
            # Tìm tất cả các elements giữa h2 hiện tại và h2 tiếp theo (hoặc cuối trang)
            try:
                # Lấy tất cả siblings sau h2
                next_siblings = driver.execute_script("""
                    var element = arguments[0];
                    var siblings = [];
                    var next = element.nextElementSibling;
                    
                    while (next) {
                        // Dừng nếu gặp h2 tiếp theo
                        if (next.tagName.toLowerCase() === 'h2' && 
                            next.classList.contains('main-title-sub')) {
                            break;
                        }
                        siblings.push(next);
                        next = next.nextElementSibling;
                    }
                    
                    return siblings;
                """, h2)
                
                # Xử lý từng element
                for sibling in next_siblings:
                    element = driver.execute_script("return arguments[0];", sibling)
                    tag_name = element.tag_name.lower()
                    class_name = element.get_attribute("class") or ""
                    
                    # Xử lý div.list-expand
                    if "list-expand" in class_name:
                        items = element.find_elements(By.CSS_SELECTOR, ".item")
                        for item in items:
                            try:
                                # Lấy title của item
                                title_elem = item.find_element(By.CSS_SELECTOR, ".title")
                                item_title = title_elem.text.strip()
                                if item_title:
                                    markdown_content += f"\n### {item_title}\n\n"
                                
                                # Lấy content của item
                                content_elem = item.find_element(By.CSS_SELECTOR, ".content")
                                markdown_content += process_element_content(content_elem)
                            except:
                                pass
                    
                    # Xử lý div.article
                    elif "article" in class_name:
                        markdown_content += process_element_content(element)
                    
                    # Xử lý table trực tiếp
                    elif tag_name == "table":
                        markdown_content += convert_table_to_markdown(element)
                    
                    # Xử lý div.divider-gray (bỏ qua)
                    elif "divider-gray" in class_name:
                        continue
                    
                    # Xử lý br
                    elif tag_name == "br":
                        continue
                    
                    # Các element khác - cố gắng lấy text
                    else:
                        text = element.text.strip()
                        if text and len(text) > 0:
                            # Kiểm tra xem có phải là element chứa nội dung không
                            if tag_name in ['div', 'p', 'span']:
                                markdown_content += f"{text}\n\n"
            
            except Exception as e:
                write_log(f"⚠ Lỗi khi xử lý section '{section_title}': {e}")
        
        return markdown_content
        
    except Exception as e:
        write_log(f"✗ Lỗi khi crawl trang: {e}")
        import traceback
        write_log(traceback.format_exc())
        return ""

try:
    # Đọc file data_with_answers.json
    write_log("Đọc file data_with_answers.json...")
    with open('data/processed/qa.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_context_links = sum(len(item.get('context_links', [])) for item in data)
    write_log(f"Tổng số context links cần crawl: {total_context_links}")
    
    # Danh sách để lưu kết quả
    results = []
    context_count = 0
    
    # Lặp qua từng câu hỏi
    for q_index, item in enumerate(data, 1):
        context_links = item.get('context_links', [])
        
        if not context_links:
            results.append(item)
            continue
        
        write_log(f"\n{'='*60}")
        write_log(f"[Câu hỏi {q_index}/{len(data)}] {item['question']}")
        write_log(f"Số context links: {len(context_links)}")
        
        # Crawl từng context link
        context_data = []
        for c_index, context in enumerate(context_links, 1):
            context_count += 1
            
            write_log(f"  [{context_count}/{total_context_links}] Crawling: {context['text']}")
            
            # Crawl và chuyển sang markdown
            markdown = crawl_context_page(context['link'])
            
            context_data.append({
                'text': context['text'],
                'link': context['link'],
                'markdown': markdown
            })
            
            write_log(f"  ✓ Đã crawl (độ dài: {len(markdown)} ký tự)")
            
            # Nghỉ giữa các request
            time.sleep(1)
        
        # Lưu kết quả
        item['context_data'] = context_data
        results.append(item)
        
        # Lưu file sau mỗi câu hỏi
        with open('data/raw/qa_with_context.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Xuất từng context thành file .md riêng
    write_log(f"\n{'='*60}")
    write_log("Đang xuất các file markdown riêng lẻ...")
    
    import os
    os.makedirs('markdown_files', exist_ok=True)
    
    file_count = 0
    for item in results:
        for context in item.get('context_data', []):
            if context['markdown']:
                file_count += 1
                # Tạo tên file an toàn
                safe_filename = re.sub(r'[^\w\s-]', '', context['text'])
                safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
                safe_filename = safe_filename[:50]  # Giới hạn độ dài tên file
                
                filepath = f"markdown_files/{file_count}_{safe_filename}.md"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(context['markdown'])
    
    write_log(f"✓ Đã xuất {file_count} file markdown")
    
    # Tổng kết
    write_log(f"\n{'='*60}")
    write_log("TỔNG KẾT")
    write_log(f"{'='*60}")
    write_log(f"Tổng số câu hỏi: {len(data)}")
    write_log(f"Tổng số context links đã crawl: {context_count}")
    write_log(f"Dữ liệu đầy đủ: data_full.json")
    write_log(f"Thư mục markdown: markdown_files/")
    write_log(f"Log: crawl_context_log.txt")

except Exception as e:
    write_log(f"LỖI NGHIÊM TRỌNG: {e}")
    import traceback
    error_trace = traceback.format_exc()
    write_log(error_trace)

finally:
    driver.quit()
    log_file.close()