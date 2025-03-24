import os

# 定义项目根目录
project_root = r'D:/code/job_crawler'

# 定义需要创建的文件夹及其包含的文件
directories = {
    'config': ['__init__.py', 'settings.py', 'log_config.yaml'],
    'core': ['__init__.py', 'crawler.py', 'parser.py', 'storage.py'],
    'spiders': ['__init__.py', 'lagou.py'],
    'utils': ['__init__.py', 'logger.py', 'proxy.py', 'request.py'],
}

# 创建文件夹和文件
for folder, files in directories.items():
    folder_path = os.path.join(project_root, folder)
    os.makedirs(folder_path, exist_ok=True)
    for file in files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'w') as f:
            pass  # 创建空文件

# 创建根目录下的文件
root_files = ['requirements.txt', 'main.py', 'README.md']
for file in root_files:
    file_path = os.path.join(project_root, file)
    with open(file_path, 'w') as f:
        pass  # 创建空文件

print(f"项目框架已成功创建在 {project_root}")
