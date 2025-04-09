import requests
from lxml import html
from urllib.parse import urljoin
import csv
import time
import random
from fake_useragent import UserAgent

# 设置请求头池
ua = UserAgent()
headers_pool = [
    {'User-Agent': ua.chrome},
    {'User-Agent': ua.firefox},
    {'User-Agent': ua.safari},
    {'User-Agent': ua.opera}
]

# 设置代理池（可根据需要添加更多代理）
proxies_pool = [
    None  # 直接连接
]


def get_headers():
    return random.choice(headers_pool)


def get_proxy():
    return random.choice(proxies_pool)


def parse_list_page(response):
    """解析列表页，提取职位信息和详情页链接"""
    tree = html.fromstring(response.text)

    # 提取职位标题
    title_elements = tree.xpath("//li[contains(concat(' ', normalize-space(@class), ' '),' ibox-title ')]")
    titles = [elem.text_content().strip() if elem is not None else None for elem in title_elements]

    # 提取职位链接
    link_elements = tree.xpath("//a[@class='ibox']")
    title_links = []
    for elem in link_elements:
        link = elem.xpath("./@href")
        if link:
            title_links.append(urljoin(response.url, link[0]))
        else:
            title_links.append(None)

    # 提取薪资
    salary_elements = tree.xpath("//li[contains(concat(' ', normalize-space(@class), ' '),' ibox-salary ')]")
    salaries = [elem.text_content().strip() if elem is not None else None for elem in salary_elements]

    # 提取公司名
    company_elements = tree.xpath(
        "//li[contains(concat(' ', normalize-space(@class), ' '),' ibox-enterprise ')]/object[1]/a[1]")
    companies = [elem.text_content().strip() if elem is not None else None for elem in company_elements]

    # 提取地区
    address_elements = tree.xpath("//li[contains(concat(' ', normalize-space(@class), ' '),' ibox-address ')]")
    addresses = [elem.text_content().strip() if elem is not None else None for elem in address_elements]

    # 提取福利
    welfare_elements = tree.xpath("//span[contains(concat(' ', normalize-space(@class), ' '),' ibox-icon-item ')]")
    welfares = [elem.text_content().strip() if elem is not None else None for elem in welfare_elements]

    # 组装数据
    items = []
    for i in range(len(titles)):
        item = {
            'title': titles[i],
            'link': title_links[i] if i < len(title_links) else None,
            'salary': salaries[i] if i < len(salaries) else None,
            'company': companies[i] if i < len(companies) else None,
            'address': addresses[i] if i < len(addresses) else None,
            'welfare': welfares[i] if i < len(welfares) else None
        }
        items.append(item)

    return items


def parse_detail_page(response):
    """解析详情页，提取职位描述和公司介绍"""
    tree = html.fromstring(response.text)

    # 提取职位描述
    description = tree.xpath("//p[@class='detail-desc-position']//text()")
    description = ' '.join(description).strip() if description else None

    # 提取公司介绍
    company_intro = tree.xpath("//p[@class='detail-desc-company']//text()")
    company_intro = ' '.join(company_intro).strip() if company_intro else None

    return {
        'description': description,
        'company_intro': company_intro
    }


def crawl_job_details(job):
    """爬取单个职位的详情"""
    if not job['link']:
        return job

    # 随机等待1-3秒，避免频繁请求
    time.sleep(random.uniform(1, 3))

    try:
        # 随机选择请求头和代理
        headers = get_headers()
        proxy = get_proxy()

        # 发送请求
        response = requests.get(job['link'], headers=headers, proxies=proxy, timeout=10)

        # 检查是否被反爬
        if response.status_code != 200 or '验证中心' in response.text:
            print(f"访问 {job['link']} 时遇到反爬机制，尝试更换代理和请求头重试...")
            # 尝试最多3次
            for _ in range(3):
                headers = get_headers()
                proxy = get_proxy()
                try:
                    response = requests.get(job['link'], headers=headers, proxies=proxy, timeout=10)
                    if response.status_code == 200 and '验证中心' not in response.text:
                        break
                except:
                    continue
            else:
                print(f"无法绕过反爬机制，跳过 {job['link']}")
                return job

        # 解析详情页
        detail_data = parse_detail_page(response)
        job.update(detail_data)

    except Exception as e:
        print(f"爬取 {job['link']} 时出错: {e}")

    return job


def crawl_jobs(pages=5):
    """爬取招聘信息"""
    base_url = "https://bj.ganji.com/zpshengchankaifa/"
    current_page = 1
    next_page_url = base_url

    # 创建CSV文件并写入表头
    with open('ganji_jobs.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['title', 'link', 'salary', 'company', 'address', 'welfare', 'description', 'company_intro']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while current_page <= pages and next_page_url:
            print(f"正在爬取第 {current_page} 页...")

            # 随机选择请求头和代理
            headers = get_headers()
            proxy = get_proxy()

            try:
                # 发送请求
                response = requests.get(next_page_url, headers=headers, proxies=proxy, timeout=10)

                # 检查是否被反爬
                if response.status_code != 200 or '验证中心' in response.text:
                    print(f"访问 {next_page_url} 时遇到反爬机制，尝试更换代理和请求头重试...")
                    # 尝试最多3次
                    for _ in range(3):
                        headers = get_headers()
                        proxy = get_proxy()
                        try:
                            response = requests.get(next_page_url, headers=headers, proxies=proxy, timeout=10)
                            if response.status_code == 200 and '验证中心' not in response.text:
                                break
                        except:
                            continue
                    else:
                        print(f"无法绕过反爬机制，跳过第 {current_page} 页")
                        current_page += 1
                        continue

                # 解析列表页
                jobs = parse_list_page(response)

                # 爬取每个职位的详情
                for job in jobs:
                    job = crawl_job_details(job)
                    # 将数据写入CSV文件
                    writer.writerow(job)
                    print(f"已保存: {job['title']}")

                # 提取下一页链接
                tree = html.fromstring(response.text)
                next_page_element = tree.xpath(
                    "/html/body//div[contains(concat(' ', normalize-space(@class), ' '),' pagination ')]/a[5]/@href")
                if next_page_element:
                    next_page_url = urljoin(base_url, next_page_element[0])
                    print(next_page_url)
                else:
                    next_page_url = None
                    print("没有找到下一页链接，爬取结束")

                current_page += 1

            except Exception as e:
                print(f"爬取第 {current_page} 页时出错: {e}")
                current_page += 1
                continue


if __name__ == "__main__":
    crawl_jobs(pages=5)
    print("爬取完成！数据已保存到 ganji_jobs.csv 文件中")

