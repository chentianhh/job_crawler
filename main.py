import csv
from core.crawler import Crawler
from core.parser import parseJob
from config.settings import Settings
from concurrent.futures import ThreadPoolExecutor

print(
    "正式启动")

# 创建岗位信息文件
with open(Settings.JOB_FILE_NAME, "w", encoding="utf-8_sig", newline="") as f_job:
    csv.writer(f_job).writerow(Settings.JOB_FILE_HEADER)

# 创建对应岗位信息的公司文件
with open(Settings.COMPANY_FILE_NAME, "w", encoding="utf-8_sig", newline="") as f_company:
    csv.writer(f_company).writerow(Settings.COMPANY_FILE_HEADER)

if __name__ == '__main__':
    crawler = Crawler()
    with ThreadPoolExecutor() as executor:
        # 访问第一页
        page_content = crawler.get_page_content(Settings.BASE_URLS[0])
        executor.submit(parseJob, crawler, page_content)

        query = ""
        # 访问剩下的九页
        for i in range(2, 8):
            print(f"第{i}页")
            url = Settings.BASE_URLS[1].format(query, i)
            page_content = crawler.get_page_content(url)
            executor.submit(parseJob, crawler, page_content)

    print(
        '结束了')
    # 关闭浏览器
    crawler.close()