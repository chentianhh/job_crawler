from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.settings import Settings

class Crawler:
    def __init__(self):
        chrome_options = Options()
        # 去掉 --headless 选项
        # if Settings.CHROME_OPTIONS['headless']:
        #     chrome_options.add_argument('--headless')
        chrome_options.add_argument(f'user-agent={Settings.CHROME_OPTIONS["user_agent"]}')
        service = Service(Settings.CHROME_DRIVER_PATH)
        self.bro = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.bro, Settings.TIMEOUT)

    def get_page_content(self, url):
        self.bro.get(url)
        return self.bro.page_source

    def close(self):
        self.bro.quit()