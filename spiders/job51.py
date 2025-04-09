import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback


def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def print_page_data(driver):
    """打印当前页面的数据"""
    items = driver.find_elements(By.CSS_SELECTOR, 'div.pos-item')
    if items:
        print(f"当前页面数据：")
        for index, item in enumerate(items, start=1):
            # 你可以根据页面结构提取具体的数据项，例如职位名称、公司等
            job_title = item.find_element(By.CSS_SELECTOR, '.job-title').text if item.find_elements(By.CSS_SELECTOR,
                                                                                                    '.job-title') else "无职位名称"
            company_name = item.find_element(By.CSS_SELECTOR, '.company-name').text if item.find_elements(
                By.CSS_SELECTOR, '.company-name') else "无公司名称"
            print(f"第 {index} 个职位 - 职位名称: {job_title}, 公司名称: {company_name}")
    else:
        print("当前页面没有数据")


def go_to_next_page(driver, max_pages=5, debug: bool = True) -> bool:
    """点击翻页，直到没有数据或翻到最大页数"""
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pageTotalId'))
        )

        current_page = 1
        while current_page <= max_pages:
            # 检查当前页是否显示“没有数据”的提示框
            no_data = driver.find_elements(By.CSS_SELECTOR, '#noListDataId:not(.hidden)')
            if no_data:
                print(f"第 {current_page} 页没有数据，结束翻页")
                return False

            # 打印当前页面的数据
            print_page_data(driver)

            # 尝试点击翻页按钮
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))

                page_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-page="{current_page + 1}"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", page_button)
                time.sleep(1)
                page_button.click()

                WebDriverWait(driver, 30).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, 'div.pos-item')) > 0
                )

                print(f"成功跳转到第 {current_page + 1} 页")
                current_page += 1

            except TimeoutException:
                print(f"第 {current_page} 页点击失败，重试中...")
                continue

        print(f"达到最大翻页数 {max_pages}，结束翻页")
        return True

    except Exception as e:
        print(f"翻页异常详情: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    driver = setup_driver()
    driver.get("https://www.job5156.com/s/search/?industryList=73&searchKeywordFrom=1")
    time.sleep(3)

    # 调用函数，设置最大翻页数
    go_to_next_page(driver, max_pages=5)

    driver.quit()

