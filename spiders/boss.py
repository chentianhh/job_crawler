import base64
import random
# from PIL import Image
from lxml import etree
import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# 指定 url
urls = ['https://www.zhipin.com/web/geek/job?city=100010000&degree=208,206,202&industry=100901',
        'https://www.zhipin.com/web/geek/job?city=100010000&degree=208,206,202&industry=100901&query={}&page={}']
prefix = 'https://www.zhipin.com'
print(
    "正式启动")

chrome_path = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument('--headless')  # 使用 Headless 模式

# 设置 Clash 代理
proxy = "127.0.0.1:7890"
chrome_options.add_argument(f'--proxy-server=http://{proxy}')

# 随机请求头
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]
chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')

# 将 executable_path 作为 options 的一部分传递
bro = webdriver.Chrome(options=chrome_options)

# 设置显式等待，替代隐式等待
wait = WebDriverWait(bro, 5)

# 岗位信息文件创建
f_job = open("岗位.csv", "w", encoding="utf-8_sig", newline="")
csv.writer(f_job).writerow(
    ["企业名称", "招聘类型", "职位类型", "职位名称", "招聘人数", "到岗时间", "年龄要求", "语言要求", "岗位描述/详情",
     "区域地址", "工作地址", "经纬度", "薪酬范围", "学历要求", "工作经验要求"])

# 对应岗位信息的文件创建
f_company = open("公司.csv", "w", encoding="utf-8_sig", newline="")
csv.writer(f_company).writerow(["企业名称", "企业logo", "从事行业", "企业规模", "详细地址", "公司介绍", "经纬度"])


# 爬取工作职位信息
def parseJob(page_content):
    # 临时存放获取到的信息
    jobList = []
    # 将从互联网上获取的源码数据加载到 tree 对象中
    tree = etree.HTML(page_content)
    job = tree.xpath('//div[@class="search-job-result"]/ul/li')

    for i in job:
        # 岗位详情页面
        detail_url = i.xpath(".//div[@class='job-card-body clearfix']/a/@href")[0]

        # 公司详情页面
        company_url = i.xpath(".//div[@class='company-logo']/a/@href")[0]

        # 企业名称
        company = i.xpath(".//h3[@class='company-name']/a/text()")[0]
        # 招聘类型
        recruit_type = "全职"
        # 职位类型
        condition_type = "机械设备/机电/重工"
        # 职位名称
        job_name = i.xpath(".//span[@class='job-name']/text()")[0]
        # 招聘人数 5 以内随机数
        recruit_num = random.randint(1, 4)
        # 到岗时间
        coming_time = "2周内"
        # 年龄要求
        age = "18岁以上"
        # 语言要求
        language = "无要求"
        # 区域地址
        jobArea = i.xpath(".//span[@class='job-area']/text()")[0]

        treeAdress = parseNewURL(detail_url)

        try:
            job_desc = ''
            list_job_desc = treeAdress.xpath(".//div[@class='job-sec-text']/text()")
            for m in list_job_desc:
                job_desc = job_desc + str(m)
            print('-----------------岗位描述：---------------' + job_desc)
        except:
            job_desc = ""
        # 工作地址
        try:
            jobAdress = treeAdress.xpath('//div[@class="job-location-map js-open-map"]/@data-content')[0]
        except:
            jobAdress = ""
        # 经纬度
        data_lat = treeAdress.xpath('//div[@class="job-location-map js-open-map"]/@data-lat')[0]
        # 薪资
        salary = i.xpath(".//span[@class='salary']/text()")[0]
        # 学历
        education = "中专/中技"
        # 工作经验
        job_lable_list = i.xpath(".//ul[@class='tag-list']//text()")[0]
        job_lables = " ".join(job_lable_list)

        # 将数据写入 csv
        csv.writer(f_job).writerow(
            [company, recruit_type, condition_type, job_name, recruit_num, coming_time, age, language, job_desc,
             jobArea, jobAdress, data_lat, salary, education, job_lables])
        print('---------------------------岗位插入成功-----------------:' + job_name)
        treeCompany = parseNewURL(company_url)
        parseCompany(treeCompany)


# 根据 url 地址跳转新链接并获得页面数据
def parseNewURL(url):
    new_url = prefix + str(url)
    bro.get(new_url)
    # 随机延迟时间
    sleep(random.uniform(1, 3))
    page_text1 = bro.page_source
    tree1 = etree.HTML(page_text1)
    return tree1


# 爬取公司信息
def parseCompany(treeCompany):
    # 企业名称
    company_name = treeCompany.xpath(".//h1[@class='name']/text()")[0]
    # 企业 logo
    company_logo = treeCompany.xpath(".//img[@class='fl']/@src")[0]

    # 从事行业
    industry = treeCompany.xpath(".//div[@class='info']/p/a/text()")[0]
    # 企业规模
    if len(treeCompany.xpath(".//div[@class='info']/p/text()")) > 1:
        company_scale = treeCompany.xpath(".//div[@class='info']/p/text()")[1]
    else:
        company_scale = treeCompany.xpath(".//div[@class='info']/p/text()")[0]
    # 详细地址
    company_adress = treeCompany.xpath(".//div[@class='map-container js-open-detail']/@data-content")[0]
    # 公司介绍
    if len(treeCompany.xpath(".//div[@class='text fold-text']/text()")) > 0:
        company_desc = treeCompany.xpath(".//div[@class='text fold-text']/text()")[0]
    else:
        company_desc = '无'
    # 经纬度
    company_data_lat = treeCompany.xpath(".//div[@class='map-container js-open-detail']/@data-lat")[0]
    # 随机延迟时间
    sleep(random.uniform(1, 3))
    # 将数据写入 csv
    csv.writer(f_company).writerow(
        [company_name, company_logo, industry, company_scale, company_adress, company_desc, company_data_lat])
    print('---------------------------公司数据插入成功-----------------:' + company_name)


if __name__ == '__main__':
    with ThreadPoolExecutor() as executor:
        # 访问第一页
        bro.get(urls[0])
        sleep(random.uniform(3, 5))
        page_content = bro.page_source
        executor.submit(parseJob, page_content)

        query = ""
        # 访问剩下的九页
        for i in range(2, 8):
            print(f"第{i}页")
            url = urls[1].format(query, i)
            bro.get(url)
            sleep(random.uniform(1, 3))
            page_content = bro.page_source
            executor.submit(parseJob, page_content)

    print(
        '结束了')
    # 关闭浏览器
    bro.quit()
    f_job.close()
    f_company.close()

