import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import glob
import re
from pathlib import Path 
import sys
# -------------------------- 自定义配置 --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(sys.executable) if getattr(sys, 'frozen', False) else __file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "one")  # 下载目录在exe同目录下的one文件夹
NEW_FILE_NAME = ""

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

#判断是否下载完成
def is_file_downloaded(download_dir, target_filename, timeout=60):
    """
    判断文件是否下载完成
    """
    start_time = time.time()
    temp_suffixes = [".crdownload", ".part", ".tmp"]  # 浏览器临时文件后缀
    
    while time.time() - start_time < timeout:
        # 遍历下载目录下的所有文件
        for filename in os.listdir(download_dir):
            # 情况1：找到最终文件（无临时后缀）
            if filename == target_filename:
                time.sleep(1)  # 保险：等待文件写入完成
                return True
            # 情况2：找到临时文件（还在下载中）
            elif filename.startswith(target_filename) and any(filename.endswith(suf) for suf in temp_suffixes):
                time.sleep(0.5)  # 下载中，继续等待
                break
        else:
            # 既没找到最终文件，也没找到临时文件 → 可能还没开始下载
            time.sleep(0.5)
    # 超时
    return False

# -------------------------- 工具函数：等待下载完成 + 重命名 --------------------------
def wait_for_download_complete(download_dir, timeout=60):
    """
    等待本次下载完成，返回最新下载的文件路径（仅识别本次新增的文件）
    :param download_dir: 下载目录（绝对路径，建议用r前缀）
    :param timeout: 超时时间（秒）
    :return: 本次下载的文件路径
    """
    # 步骤1：记录「下载开始前」的基准文件列表（区分旧文件）
    download_dir = Path(download_dir)  # 用Path简化路径操作
    # 基准列表：下载前已存在的非临时文件（排除所有下载临时后缀）
    temp_suffixes = (".crdownload", ".part", ".tmp")  # 覆盖主流浏览器临时文件
    baseline_files = set()
    for file in download_dir.iterdir():
        if file.is_file() and not file.name.lower().endswith(temp_suffixes):
            baseline_files.add(file.name)

    start_time = time.time()
    latest_new_file = None  # 存储本次下载的新文件
    
    while time.time() - start_time < timeout:
        # 步骤2：遍历目录，筛选「本次新增的文件」（不在基准列表+非临时文件）
        current_files = []
        for file in download_dir.iterdir():
            # 排除临时文件、文件夹、旧文件
            if (file.is_file() 
                and not file.name.lower().endswith(temp_suffixes)
                and file.name not in baseline_files):
                current_files.append(file)
        
        if current_files:
            # 取本次新增文件中「最新修改」的（确保是刚下载完成的）
            latest_new_file = max(current_files, key=lambda x: x.stat().st_mtime)
            # 额外保险：等待文件大小稳定（避免文件还在写入）
            prev_size = -1
            stable_count = 0
            while stable_count < 2:  # 连续2次检查大小不变
                current_size = latest_new_file.stat().st_size
                if current_size == prev_size:
                    stable_count += 1
                else:
                    prev_size = current_size
                    stable_count = 0
                time.sleep(0.5)
            return str(latest_new_file)  # 返回绝对路径
        
        # 步骤3：如果还没新文件，等待1秒再检查（不着急返回）
        time.sleep(1)
    
    # 超时抛出异常
    raise TimeoutError(
        f"下载超时！{timeout}秒内未找到本次下载的新文件\n"
        f"下载目录已有旧文件：{list(baseline_files)[:5]}（最多显示5个）"
    )

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
uc.TARGET_VERSION = 143 
driver = uc.Chrome(options=chrome_options)
driver.implicitly_wait(5)



try:
    # 访问目标页面
    u = ""
    print("输入URL地址：")
    u = input()
    driver.get(u)
    year = 0
    time.sleep(2)  # 等待页面加载
    print("手动登录后，按回车继续")
    input()

    #18年之后的需要下拉
    #driver.execute_script("window.scrollBy(0, 100);")
    a = 9
    # 依次点击 Volume 
    b = 3
    print("输入起始年份（如18代表2018年）：")
    b = 26 - int(input()) 
    for j in range(b, 17):  # 年份
        print(f"处理第 {26 - j} 年份")
        year = 26 - j
        

        #处理年份
        if 26 - j == 17:
            a = 8
        elif 26 - j == 13:
            a = 4
        elif 26 - j >= 14 and 26 - j <=16:
            a = 6
        for i in range(1, a):  # Volume  20年-18年 改成7, 17年改成8, 16 - 14 改成6, 13年改成4
            
            time.sleep(3)
            #等待并点击下载按钮            
            dwn_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Download full issue")]'))
            )
            dwn_btn.click()
            print("下载按钮已点击，等待下载完成...")
            


            old_file_path = wait_for_download_complete(DOWNLOAD_DIR)
            print(f"下载完成：{old_file_path}")
            
            while(not is_file_downloaded(DOWNLOAD_DIR, os.path.basename(old_file_path), timeout=120)):
                print("文件尚未下载完成，继续等待...")
                time.sleep(7)


            
             #获取新文件名
            try:
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/section[1]/div/div/div/h3'))
                )
                title_text = title_element.text.strip()  # 转为字符串
            except:
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/section[1]/div/div/div/div[1]/span/h3'))
                )
                title_text = title_element.text.strip()  # 转为字符串
                
            first_char = title_text[0]
            all_four_digits = re.findall(r'\d{4}', title_element.text)
            
            if all_four_digits:
                year_str = all_four_digits[-1] # 取列表最后一个元素
                NEW_FILE_NAME = f"{year_str}_{i}.zip"  
            else:
                NEW_FILE_NAME = "SciDirect_Unknown_Year.zip" 
            print(f"新文件名设定为：{NEW_FILE_NAME}")
        

            # 构造新文件路径
            new_file_path = os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME)
            
            # 重命名文件
            rename_downloaded_file(old_file_path, new_file_path)
            
            #刷新页面
            driver.refresh()
            time.sleep(2)
            
            #点击下一篇
            next_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/section[1]/div/div/nav/div[1]/a/span'))
            )
            next_btn.click()

            

except Exception as e:
    print(f"执行出错：{type(e).__name__} - {e}")
    # 可选：保存页面源码用于排查
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"已下载到{year}年")

finally:
    # 延迟关闭（确保下载完成）
    time.sleep(2)
    driver.quit()
    print("浏览器已关闭")
    
    
    
