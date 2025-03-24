import requests
from utils.proxy import get_proxy
from config.settings import Settings

def make_request(url):
    proxy = get_proxy()
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        response = requests.get(url, headers=Settings.HEADERS, proxies=proxies, timeout=Settings.TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None