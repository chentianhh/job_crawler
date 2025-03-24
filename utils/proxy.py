import requests
from config.settings import Settings

def get_proxy():
    if Settings.PROXY_ENABLED:
        try:
            response = requests.get(Settings.PROXY_API)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"获取代理失败: {e}")
    return None