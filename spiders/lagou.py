from core.crawler import BaseCrawler
from core.storage import Storage
from config.settings import Settings


class LagouSpider(BaseCrawler):
    def __init__(self):
        super().__init__("拉勾网")
        self.start_urls = ["https://www.lagou.com/zhaopin/Python/"]
        self.storage = Storage(Settings.SAVE_TO)

    def parse_list(self, html):
        # 使用BeautifulSoup解析列表页
        jobs = []
        # ...解析逻辑...
        return jobs

    def parse_detail(self, html):
        # 解析详情页
        job_data = {}
        # ...解析逻辑...
        return job_data

    def store(self, data):
        self.storage.save(data)