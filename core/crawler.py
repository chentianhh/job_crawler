from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from config.settings import Settings

class Crawler:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument(f'user-agent={Settings.CHROME_OPTIONS["user_agent"]}')
        service = Service(Settings.CHROME_DRIVER_PATH)
        self.bro = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.bro, Settings.TIMEOUT)

    def get_page_content(self, url):
        self.bro.get(url)
        try:
            # 等待页面上的关键元素加载完成，这里以搜索结果列表为例
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.search-job-result')))
        except Exception as e:
            print(f"等待页面元素加载时出现错误: {e}")
        return self.bro.page_source

    def close(self):
        self.bro.quit()