import os


class Settings:
    # 请求配置
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    TIMEOUT = 10
    RETRY_TIMES = 3

    # 存储配置
    SAVE_TO = "csv"  # csv/mysql/mongodb
    # MYSQL_CONFIG = {
    #     'host': 'localhost',
    #     'port': 3306,
    #     'user': 'root',
    #     'password': 'root',
    #     'database': 'jobs'
    # }

    # 代理配置
    PROXY_ENABLED = False
    PROXY_API = "http://api.proxy.com/get"

    # 浏览器配置
    CHROME_DRIVER_PATH = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    CHROME_OPTIONS = {
        'headless': True,
        'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # URL配置
    BASE_URLS = [
        'https://www.zhipin.com/web/geek/job?city=100010000&degree=208&industry=100901',
        'https://www.zhipin.com/web/geek/job?city=100010000&degree=208&industry=100901&query={}&page={}'
    ]
    PREFIX_URL = 'https://www.zhipin.com'

    # 文件配置
    JOB_FILE_NAME = r"D:\code\job_crawler\data\岗位+地址V100901.csv"
    COMPANY_FILE_NAME = r"D:\code\job_crawler\data\岗位对应公司的信息V100901.csv"
    JOB_FILE_HEADER = [
        "企业名称", "招聘类型", "职位类型", "职位名称", "招聘人数", "到岗时间", "年龄要求", "语言要求", "岗位描述/详情",
        "区域地址", "工作地址", "经纬度", "薪酬范围", "学历要求", "工作经验要求"
    ]
    COMPANY_FILE_HEADER = [
        "企业名称", "企业logo", "从事行业", "企业规模", "详细地址", "公司介绍", "经纬度"
    ]