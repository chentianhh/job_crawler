from lxml import etree
import csv
import random
from config.settings import Settings

def parseJob(crawler, page_content):
    jobList = []
    tree = etree.HTML(page_content)
    job = tree.xpath('//div[@class="search-job-result"]/ul/li')
    with open(Settings.JOB_FILE_NAME, "a", encoding="utf-8_sig", newline="") as f_job:
        writer = csv.writer(f_job)
        for i in job:
            detail_url = i.xpath(".//div[@class='job-card-body clearfix']/a/@href")[0]
            company_url = i.xpath(".//div[@class='company-logo']/a/@href")[0]
            company = i.xpath(".//h3[@class='company-name']/a/text()")[0]
            recruit_type = "全职"
            condition_type = "机械设备/机电/重工"
            job_name = i.xpath(".//span[@class='job-name']/text()")[0]
            recruit_num = random.randint(1, 4)
            coming_time = "2周内"
            age = "18岁以上"
            language = "无要求"
            jobArea = i.xpath(".//span[@class='job-area']/text()")[0]

            treeAdress = parseNewURL(crawler, detail_url)

            try:
                job_desc = ''
                list_job_desc = treeAdress.xpath(".//div[@class='job-sec-text']/text()")
                for m in list_job_desc:
                    job_desc = job_desc + str(m)
            except:
                job_desc = ""

            try:
                jobAdress = treeAdress.xpath('//div[@class="job-location-map js-open-map"]/@data-content')[0]
            except:
                jobAdress = ""

            data_lat = treeAdress.xpath('//div[@class="job-location-map js-open-map"]/@data-lat')[0]
            salary = i.xpath(".//span[@class='salary']/text()")[0]
            education = "中专/中技"
            job_lable_list = i.xpath(".//ul[@class='tag-list']//text()")[0]
            job_lables = " ".join(job_lable_list)

            writer.writerow(
                [company, recruit_type, condition_type, job_name, recruit_num, coming_time, age, language, job_desc,
                 jobArea, jobAdress, data_lat, salary, education, job_lables])
            print('---------------------------岗位插入成功-----------------:' + job_name)

            treeCompany = parseNewURL(crawler, company_url)
            parseCompany(treeCompany)

def parseNewURL(crawler, url):
    new_url = Settings.PREFIX_URL + str(url)
    page_text1 = crawler.get_page_content(new_url)
    tree1 = etree.HTML(page_text1)
    return tree1

def parseCompany(treeCompany):
    with open(Settings.COMPANY_FILE_NAME, "a", encoding="utf-8_sig", newline="") as f_company:
        writer = csv.writer(f_company)
        company_name = treeCompany.xpath(".//h1[@class='name']/text()")[0]
        company_logo = treeCompany.xpath(".//img[@class='fl']/@src")[0]
        industry = treeCompany.xpath(".//div[@class='info']/p/a/text()")[0]
        if len(treeCompany.xpath(".//div[@class='info']/p/text()")) > 1:
            company_scale = treeCompany.xpath(".//div[@class='info']/p/text()")[1]
        else:
            company_scale = treeCompany.xpath(".//div[@class='info']/p/text()")[0]
        company_adress = treeCompany.xpath(".//div[@class='map-container js-open-detail']/@data-content")[0]
        if len(treeCompany.xpath(".//div[@class='text fold-text']/text()")) > 0:
            company_desc = treeCompany.xpath(".//div[@class='text fold-text']/text()")[0]
        else:
            company_desc = '无'
        company_data_lat = treeCompany.xpath(".//div[@class='map-container js-open-detail']/@data-lat")[0]
        writer.writerow(
            [company_name, company_logo, industry, company_scale, company_adress, company_desc, company_data_lat])
        print('---------------------------公司数据插入成功-----------------:' + company_name)