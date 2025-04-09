import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urljoin


class JobCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.job5156.com/'
        }
        self.data = []
        self.session = requests.Session()

    def fetch_page(self, page_num):
        """带重试机制的页面获取"""
        params = {
            'industryList': '73,182',
            'searchKeywordFrom': '1',
            'pn': page_num,
            'pageSize': '30'
        }
        for _ in range(3):
            try:
                response = self.session.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=15,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"第{page_num}页请求失败，重试中... ({e})")
                time.sleep(random.uniform(1, 3))
        return None

    def parse_job_list(self, html):
        """解析职位列表页"""
        soup = BeautifulSoup(html, 'html.parser')
        job_items = soup.select('.job-item')
        for job in job_items:
            yield {
                '职位链接': urljoin(self.base_url, job.find('a')['href']),
                '职位名称': job.select_one('.name').text.strip(),
                '薪资范围': job.select_one('.salary').text.strip(),
                '工作地点': job.select_one('.location').text.strip(),
                '发布时间': job.select_one('.update-time').text.strip(),
                '公司名称': job.select_one('.company').text.strip(),
                '公司性质': job.select_one('.property').text.strip(),
                '员工规模': job.select_one('.employee').text.strip(),
                '行业领域': job.select_one('.industry').text.strip()
            }

    def parse_detail(self, url):
        """解析职位详情页"""
        time.sleep(random.uniform(0.5, 1.5))
        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            return {
                '工作性质': soup.select_one('.job-type .text').text.strip(),
                '工作年限': soup.select_one('.work-year .text').text.strip(),
                '学历要求': soup.select_one('.degree .text').text.strip(),
                '岗位职责': '\n'.join([li.text.strip() for li in soup.select('.job-requirement .job-desc ul li')]),
                '任职要求': '\n'.join([li.text.strip() for li in soup.select('.job-requirement .job-require ul li')]),
                '公司地址': soup.select_one('.company-address .text').text.strip(),
                '公司简介': soup.select_one('.company-intro .desc').text.strip() if soup.select_one(
                    '.company-intro .desc') else ''
            }
        except Exception as e:
            print(f"详情页解析失败: {e}")
            return {}

    def run(self):
        """主运行逻辑"""
        page_num = 1
        while True:
            print(f"正在抓取第{page_num}页...")
            html = self.fetch_page(page_num)
            if not html:
                break

            for job_info in self.parse_job_list(html):
                detail_info = self.parse_detail(job_info['职位链接'])
                self.data.append({**job_info, **detail_info})

            # 检查是否有下一页
            next_page = BeautifulSoup(html, 'html.parser').select_one('.pagination .next')
            if not next_page or 'disabled' in next_page.get('class', []):
                break
            page_num += 1
            time.sleep(random.uniform(2, 4))

    def save_to_csv(self, filename='jobs.csv'):
        """带数据清洗的CSV保存"""
        if not self.data:
            print("没有数据可保存")
            return

        # 数据清洗
        clean_data = []
        for item in self.data:
            cleaned = {k: v.replace('\n', '').strip() if isinstance(v, str) else v for k, v in item.items()}
            clean_data.append(cleaned)

        # 定义字段顺序
        field_order = [
            '职位名称', '薪资范围', '工作地点', '发布时间', '工作性质', '工作年限',
            '学历要求', '公司名称', '公司性质', '员工规模', '行业领域', '公司地址',
            '公司简介', '岗位职责', '任职要求', '职位链接'
        ]

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=field_order)
            writer.writeheader()
            writer.writerows(clean_data)
        print(f"数据已保存到 {filename}，共{len(clean_data)}条记录")


if __name__ == '__main__':
    crawler = JobCrawler('https://www.job5156.com/s/search/')
    crawler.run()
    crawler.save_to_csv()