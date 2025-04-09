import time
import csv
import random
import logging
from typing import List, Dict, Set
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import argparse

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 目标网址
BASE_URL = "https://www.job5156.com/s/search/?industryList=73&searchKeywordFrom=1"

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 代理配置
PROXY = {
    'host': '127.0.0.1',
    'port': 7890
}


def setup_driver():
    """设置Selenium WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # 新增 SSL/TLS 相关配置
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-ssl-errors=yes')

    # 配置代理
    proxy_str = f'socks5://{PROXY["host"]}:{PROXY["port"]}'
    options.add_argument(f'--proxy-server={proxy_str}')

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": HEADERS['User-Agent']})
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def get_unique_key(job: Dict) -> str:
    """生成用于去重的唯一键"""
    return f"{job['公司名称']}_{job['职位名称']}_{job['学历要求']}"


def remove_duplicates(job_list: List[Dict]) -> List[Dict]:
    """去除重复数据"""
    seen = set()
    unique_jobs = []

    for job in job_list:
        key = get_unique_key(job)
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


def scrape_job_data(driver, debug: bool = False) -> List[Dict]:
    """从当前页面抓取工作数据"""
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pageTotalId, div.pos-item')))

        no_data = driver.find_elements(By.CSS_SELECTOR, '#noListDataId:not(.hidden)')
        if no_data:
            if debug:
                logging.info("当前页面没有数据")
            return []

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_data = []
        job_cards = soup.select('div.pos-item, li.pos-item, div[data-posname]')

        if debug:
            logging.info(f"找到 {len(job_cards)} 个职位卡片")

        for job_card in job_cards:
            try:
                company = job_card.get('data-comname', '未知公司').strip()
                job_title = job_card.get('data-posname', '未知职位').strip()
                city = job_card.get('data-cityname', '未知城市').strip()
                province = job_card.get('data-provstr', '未知省份').strip()
                degree = job_card.get('data-reqdegreestr', '学历不限').strip()
                work_year = job_card.get('data-reqworkyear', '经验不限').strip()
                industry = job_card.get('data-comindustry', '行业未知').strip()

                desc = job_card.find(['pre', 'div', 'p'], class_=['pos-card-desc', 'job-desc'])
                description = desc.text.strip() if desc else '无'

                job_data.append({
                    '公司名称': company,
                    '职位名称': job_title,
                    '工作城市': city,
                    '所在省份': province,
                    '学历要求': degree,
                    '工作经验': work_year,
                    '所属行业': industry,
                    '职位描述': description
                })

            except Exception as e:
                if debug:
                    logging.warning(f"处理职位卡片时出错: {str(e)}")
                continue

        return job_data

    except Exception as e:
        if debug:
            logging.error(f"请求或解析页面时出错: {str(e)}")
        return []


def go_to_next_page(driver, target_page=2, debug: bool = False) -> bool:
    """点击指定页数并确保加载完成"""
    try:
        page_info = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pageTotalId'))
        )
        current_page = int(page_info.get_attribute('data-pn'))
        total_pages = int(page_info.get_attribute('data-page'))

        if target_page > total_pages:
            if debug:
                logging.info(f"目标页数 {target_page} 超出总页数 {total_pages}")
            return False

        # 滚动触发懒加载并短暂等待
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 3))

        # 点击下一页按钮
        next_page_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '/html/body//a[contains(concat(" ", normalize-space(@class), " "), " layui-laypage-next ")]/i'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
        time.sleep(1)
        next_page_button.click()

        WebDriverWait(driver, 3).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, 'div.pos-item')) > 0
        )

        if debug:
            logging.info(f"成功跳转到第 {target_page} 页")
        return True

    except TimeoutException:
        if debug:
            logging.error(f"超时错误：第 {target_page} 页未成功加载，可能是页面加载缓慢。")
        return False

    except Exception as e:
        if debug:
            logging.error(f"翻页时发生意外错误: {str(e)}")
        return False


def save_to_csv(data: List[Dict], filename: str = 'job_data.csv') -> bool:
    try:
        unique_data = remove_duplicates(data)

        with open(filename, mode='w', encoding='utf-8-sig', newline='') as file:
            fieldnames = ['公司名称', '职位名称', '工作城市', '所在省份', '学历要求', '工作经验', '所属行业',
                          '职位描述']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_data)

        return True
    except Exception as e:
        logging.error(f"保存文件出错: {str(e)}")
        return False


def main(debug: bool = False, max_pages: int = None):
    logging.info(f"启动爬虫{' (调试模式)' if debug else ''}")
    driver = setup_driver()
    all_data = []
    page = 1
    has_more_data = True

    try:
        # 访问初始页面
        driver.get(BASE_URL)
        time.sleep(3)  # 初始加载等待

        while has_more_data and (max_pages is None or page <= max_pages):
            time.sleep(random.uniform(2, 5))
            start_time = time.time()

            # 抓取当前页数据
            data = scrape_job_data(driver, debug=debug)
            elapsed = time.time() - start_time
            count = len(data)

            if count > 0:
                all_data.extend(data)
                logging.info(f"第 {page} 页: 获取 {count} 条数据 (耗时 {elapsed:.2f}秒)")

                # 尝试翻页
                if not go_to_next_page(driver, page + 1, debug=debug):
                    has_more_data = False
                else:
                    page += 1
                    time.sleep(1 + (0.5 if debug else 0))
            else:
                logging.info(f"第 {page} 页没有获取到数据，停止爬取")
                has_more_data = False

    except Exception as e:
        logging.error(f"爬取过程中发生错误: {str(e)}")
    finally:
        driver.quit()

    if all_data:
        unique_count = len(remove_duplicates(all_data))
        if save_to_csv(all_data):
            logging.info(f"\n爬取完成！共获取 {len(all_data)} 条数据，去重后 {unique_count} 条，已保存到 job_data.csv")
        else:
            logging.error("\n数据保存失败")
    else:
        logging.info("\n没有获取到任何数据，请检查：")
        logging.info("1. 网站结构可能已变化")
        logging.info("2. 尝试手动访问目标URL确认数据是否存在")
        if debug:
            logging.info("3. 请检查页面结构")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='智通招聘数据爬虫(Selenium版)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--pages', type=int, help='指定爬取页数(默认爬取所有可用数据)')
    args = parser.parse_args()
    main(debug=args.debug, max_pages=args.pages)
