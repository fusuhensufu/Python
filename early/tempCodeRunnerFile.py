import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import glob
import re

# -------------------------- 自定义配置 --------------------------
# 1. 指定下载存储位置（替换为你的目标路径）
DOWNLOAD_DIR = os.path.abspath("./sciencedirect_downloads")  # 相对路径（当前目录下）
# DOWNLOAD_DIR = "D:/SciDirect_PDFs"  # Windows 绝对路径示例
# DOWNLOAD_DIR = "/home/user/SciDirect_PDFs"  # Linux/Mac 绝对路径示例

# 2. 自定义下载后的文件名
NEW_FILE_NAME = "ComputerLaw_Volume60.zip"

# -------------------------- Chrome 配置 --------------------------
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--start-maximized")  # 最大化窗口

# 配置下载路径 + 关闭下载弹窗 + 自动下载PDF
prefs = {
    # 指定下载路径
    "download.default_directory": DOWNLOAD_DIR,
    # 关闭下载前的确认弹窗
    "download.prompt_for_download": False,
    # 禁止PDF在浏览器中打开（直接下载）
    "plugins.always_open_pdf_externally": True,
    # 禁用下载进度条弹窗（可选）
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# -------------------------- 工具函数：等待下载完成 + 重命名 --------------------------
def wait_for_download_complete(download_dir, timeout=60):
    """
    等待下载完成，返回最新下载的文件路径
    :param download_dir: 下载目录
    :param timeout: 超时时间（秒）
    :return: 最新下载的文件路径
    """
    # 先清空下载目录中的临时文件（.crdownload 是Chrome未完成的下载文件）
    for temp_file in glob.glob(os.path.join(download_dir, "*.crdownload")):
        os.remove(temp_file)
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 获取下载目录中的所有文件（排除临时文件）
        files = [
            f for f in os.listdir(download_dir)
            if not f.endswith(".crdownload") and os.path.isfile(os.path.join(download_dir, f))
        ]
        if files:
            # 返回最新修改的文件（确保是刚下载的）
            latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))
            return os.path.join(download_dir, latest_file)
        time.sleep(1)  # 每秒检查一次
    raise TimeoutError(f"下载超时！{timeout}秒内未找到下载完成的文件")

def rename_downloaded_file(old_file_path, new_file_path):
    """
    重命名下载的文件（处理同名文件覆盖）
    :param old_file_path: 原文件路径
    :param new_file_path: 新文件路径
    """
    # 如果新文件已存在，先删除（可选：也可以加后缀避免覆盖）
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
    # 重命名
    os.rename(old_file_path, new_file_path)
    print(f"文件已重命名：{new_file_path}")

# -------------------------- 主逻辑 --------------------------
# 创建下载目录（如果不存在）
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 初始化驱动
driver = uc.Chrome(options=chrome_options)
driver.implicitly_wait(10)

try:
    # 访问目标页面
    driver.get("https://www.sciencedirect.com/journal/computer-law-and-security-review/issues")
    time.sleep(2)  # 等待页面加载
    
    # 点击下拉菜单
    dropdown_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="0-accordion-tab-1"]'))
    )
    dropdown_btn.click()
    
    #获取 Volume 列表
    volume_list = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//*[@id="0-accordion-panel-2"]'))
    )
    print(volume_list)
    
    # 点击 Volume 
    volume_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Volume 60"))
    )
    volume_btn.click()
    
    #等待并点击下载按钮
    dwn_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Download full issue")]'))
    )
    dwn_btn.click()
    print("下载按钮已点击，等待下载完成...")
    time.sleep(5)  # 等待下载开始
    
    # 等待下载完成，获取原文件路径
    old_file_path = wait_for_download_complete(DOWNLOAD_DIR)
    print(f"下载完成：{old_file_path}")
    
    #浏览器后退
    driver.back()
    time.sleep(1)
    #浏览器前进
    driver.forward()
    time.sleep(1)
    
    #获取新文件名
    title_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/section[1]/div/div/div/h3'))
    )
    year_match = re.search(r'\d{4}', title_element.text)
    if year_match:
    # 用 str() 转为字符串（其实 .group() 返回的本身就是字符串，str() 是兜底）
        year_str = str(year_match.group())  
    # 构造文件名（建议加前缀，避免仅数字的文件名）
        NEW_FILE_NAME = f"{year_str}.zip"  
    else:
    # 匹配失败时的兜底文件名（避免程序崩溃）
        NEW_FILE_NAME = "SciDirect_Unknown_Year.zip"  
    
    # 构造新文件路径
    new_file_path = os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME)
    
    # 重命名文件
    rename_downloaded_file(old_file_path, new_file_path)

except Exception as e:
    print(f"执行出错：{type(e).__name__} - {e}")
    # 可选：保存页面源码用于排查
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

finally:
    # 延迟关闭（确保下载完成）
    time.sleep(2)
    if driver.service.process and driver.service.process.is_alive():
        driver.quit()
    print("浏览器已关闭")
    
    
    
