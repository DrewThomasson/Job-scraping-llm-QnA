from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
import urllib.parse
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

def extract_category(text, category, regex_terms):
    for term in regex_terms:
        match = re.search(term, text, re.IGNORECASE)
        if match:
            start_index = match.start()
            end_index = text.find('\n', start_index)
            if end_index == -1:
                end_index = len(text)
            return text[start_index:end_index].strip()
    return None

def classify_job_description(job_description):
    categories = {
        'job_title': [r'\b(job title|position|role)\b', r'\b(we are looking for|we are seeking|seeking|looking for)\b'],
        'company': [r'\b(company|organization|employer)\b', r'\b(about us|who we are)\b'],
        'location': [r'\b(location|city|state|place)\b', r'\b(where)\b'],
        'salary': [r'\b(salary|pay|compensation|wage)\b', r'\b(\$\d+(\.\d+)?(\s+|-)\$\d+(\.\d+)?)\b'],
        'job_type': [r'\b(job type|employment type)\b', r'\b(full[-\s]time|part[-\s]time|contract|temporary|permanent)\b'],
        'benefits': [r'\b(benefits|perks)\b', r'\b(health insurance|dental insurance|401k|vacation|paid time off)\b'],
        'required_skills': [r'\b(required skills|must have|requirements|qualifications)\b', r'\b(proficiency|experience|familiarity) with\b'],
        'preferred_skills': [r'\b(preferred skills|nice to have|bonus|additional qualifications)\b', r'\b(knowledge of|experience with|familiarity with)\b'],
        'education': [r'\b(education|degree|diploma)\b', r'\b(bachelor''s|master''s|phd|high school|college)\b'],
        'experience': [r'\b(experience|years of experience)\b', r'\b(\d+(\+)?\s+years)\b']
    }

    classified_data = {}
    raw_text = []

    for category, regex_terms in categories.items():
        extracted_text = extract_category(job_description, category, regex_terms)
        if extracted_text:
            classified_data[category] = extracted_text
        else:
            raw_text.append(job_description)

    if raw_text:
        classified_data['raw'] = ' '.join(raw_text)

    return classified_data

def get_job_text(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        job_text = driver.find_element(By.TAG_NAME, "body").text.strip()
        return job_text if job_text else None
    except:
        return None
        
class ScraperThread(QThread):
    data_scraped = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, search_terms, location, num_results):
        super().__init__()
        self.search_terms = search_terms
        self.location = location
        self.num_results = num_results
        self.stop_flag = False
        self.next_search_term_flag = False
        

            
    def run(self):
        job_posts = {}

        driver = webdriver.Firefox()

        for search_term in self.search_terms:
            if self.stop_flag:
                break

            encoded_search_term = urllib.parse.quote(search_term)
            encoded_location = urllib.parse.quote(self.location)
            search_url = f"https://www.indeed.com/jobs?q={encoded_search_term}&l={encoded_location}"

            driver.get(search_url)

            while True:
                if self.stop_flag or self.next_search_term_flag:
                    break

                link_elements = driver.find_elements(By.XPATH, "//a")
                hrefs = []

                for link in link_elements:
                    try:
                        href = link.get_attribute("href")
                        if href and href.startswith("https://www.indeed.com/rc/clk") and href not in job_posts:
                            hrefs.append(href)
                    except StaleElementReferenceException:
                        continue

                for href in hrefs:
                    if self.stop_flag or self.next_search_term_flag:
                        break
    
                    driver.execute_script(f"window.open('{href}', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
    
                    job_text = None
                    while job_text is None:
                        job_text = get_job_text(driver)
    
                    classified_data = classify_job_description(job_text)
                    job_posts[href] = classified_data
    
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    self.data_scraped.emit(job_posts)



                if len(job_posts) >= self.num_results:
                    break

                try:
                    next_page_button = driver.find_element(By.XPATH, "//a[@data-testid='pagination-page-next']")
                    if next_page_button:
                        next_page_url = next_page_button.get_attribute("href")
                        driver.get(next_page_url)
                    else:
                        break
                except NoSuchElementException:
                    break

                with open("job_posts.json", "w") as file:
                    json.dump(job_posts, file, indent=4)

            self.next_search_term_flag = False

        driver.quit()

        with open("job_posts.json", "w") as file:
            json.dump(job_posts, file, indent=4)

        self.finished.emit()

class JobScraper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Scraper")
        self.setGeometry(100, 100, 800, 600)

        self.search_terms = ['software', 'developer', 'computer science', 'programmer']
        self.search_terms_field = QLineEdit(", ".join(self.search_terms))
        self.update_search_terms_button = QPushButton("Update Search Terms")
        self.update_search_terms_button.clicked.connect(self.update_search_terms)

        self.location_label = QLabel("Location:")
        self.location_field = QLineEdit("Atlanta, GA")
        self.num_results_label = QLabel("Number of Results:")
        self.num_results_field = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.start_scraper)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_scraper)
        self.next_search_term_button = QPushButton("Next Search Term")
        self.next_search_term_button.clicked.connect(self.next_search_term)

        self.status_label = QLabel()

        self.json_preview_area = QTextEdit()
        self.json_preview_area.setReadOnly(True)

        grid_layout = QVBoxLayout()
        grid_layout.addWidget(QLabel("Search Terms (comma-separated):"))
        grid_layout.addWidget(self.search_terms_field)
        grid_layout.addWidget(self.update_search_terms_button)
        grid_layout.addWidget(self.location_label)
        grid_layout.addWidget(self.location_field)
        grid_layout.addWidget(self.num_results_label)
        grid_layout.addWidget(self.num_results_field)
        grid_layout.addWidget(self.search_button)
        grid_layout.addWidget(self.stop_button)
        grid_layout.addWidget(self.next_search_term_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.json_preview_area)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        central_layout = QVBoxLayout()
        central_layout.addLayout(main_layout)
        central_layout.addLayout(status_layout)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.scraper_thread = None

    def update_search_terms(self):
        self.search_terms = [term.strip() for term in self.search_terms_field.text().split(",")]

    def start_scraper(self):
        location = self.location_field.text()
        num_results = int(self.num_results_field.text())

        self.scraper_thread = ScraperThread(self.search_terms, location, num_results)
        self.scraper_thread.data_scraped.connect(self.update_json_preview)
        self.scraper_thread.finished.connect(self.scraper_finished)
        self.scraper_thread.start()

        self.status_label.setText("Scraper started")

    def stop_scraper(self):
        if self.scraper_thread and self.scraper_thread.isRunning():
            self.scraper_thread.stop_flag = True
            self.status_label.setText("Scraper stopped")


    
    def next_search_term(self):
        if self.scraper_thread and self.scraper_thread.isRunning():
            self.scraper_thread.next_search_term_flag = True
            self.status_label.setText("Moving to next search term")

    def update_json_preview(self, job_posts):
        self.json_preview_area.setText(json.dumps(job_posts, indent=4))

    def scraper_finished(self):
        self.status_label.setText("Scraper finished")

if __name__ == "__main__":
    app = QApplication([])
    scraper = JobScraper()
    scraper.show()
    app.exec_()
