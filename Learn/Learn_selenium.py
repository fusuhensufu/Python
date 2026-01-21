#导入 selenium 第三方库
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver import ActionChains
#指定驱动路径
service = Service(r"./chromedriver.exe")        #Service 是一个类


#创建浏览器对象
driver = webdriver.Chrome(service=service)

#打开指定网址
driver.get("https://www.bilibili.com/")
driver.maximize_window()
driver.add_cookie({             #cookie有四个关键属性必须要有, 就是下面这四个       找核心cookie就是看看哪个cookie的过期时间最长, 哪个安全级别最多
    'name': 'SESSDATA',
    'value': '8e65aa00%2C1782049040%2C18faa%2Ac2CjDuPrn9MJXNu_rlpME54SQoKJU2AwHp-VkJwDqH3-XW0BnAtll875CgQDJG9SKL4L8SVmRUZkxRd1FiSnBfVGpKMGdPMTBtTFdGTEk3ajd6b3owNlc4dFVocnV5RmJQYW82TDV6VG9FeWFkVzBTMUg5eDB4Q1Q0Y0NtcVk1eEVsOVRDSzlyamZnIIEC',
    'domain': '.bilibili.com',  # 核心：指定Cookie所属域名  必须是以.开头
    'path': '/',  # 核心：指定Cookie生效的路径（根路径）
    'httpOnly': True,  # 匹配B站SESSDATA的HttpOnly属性
    'secure': True,  # 匹配Secure属性（HTTPS下生效）
})

# 关键3：刷新页面，让B站读取新增的Cookie
driver.refresh()
    
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='nav-searchform']/div[1]/input"))).send_keys("测试")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='nav-searchform']/div[2]"))).click()

# 切换到视频tab     好像是不能用xpath, 只能用css selector, xpath一直在变
video_tab = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='search-tabs i_wrapper']//span[text()='视频']"))
)
ActionChains(driver).move_to_element(video_tab).click().perform()


search_result_container = "//div[contains(@class, 'video-list row') or contains(@class, 'video-list-container')]"
target_xpath = "//h3[@class='bili-video-card__info--tit']"
# 等待搜索结果列表加载完成（确保父容器存在）
WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, search_result_container))
    )


try:
    time.sleep(1)
    # 等待第一个视频元素可点击（延长等待时间到15秒，确保页面加载完成）
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, target_xpath))
    )
    all_videos = driver.find_elements(By.XPATH, target_xpath)
    if not all_videos:
        print("未找到视频元素")
        
    first_video = all_videos[10]
    print(first_video.get_attribute('href'))
    try:
        #这一句还没有理解明白
        ActionChains(driver).move_to_element(first_video).click().perform()
        print("常规点击成功")
    except:
        # 步骤3：常规点击失败，用JS强制点击（绕过交互检查）
        driver.execute_script("arguments[0].click();", first_video)
        print("JS强制点击成功")
    stop = input("按回车键继续...")


except Exception as e:
    print(f"定位/点击视频失败：{e}")

finally:
    # 延迟关闭浏览器，方便查看结果
    time.sleep(1)
    driver.quit()