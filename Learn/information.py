from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://search.bilibili.com/all?vt=15248847&keyword=%E9%83%A8%E8%90%BD%E5%86%B2%E7%AA%81%20%E4%BC%A0%E5%A5%87%E6%9C%80%E6%96%B0%E7%A7%91%E7%A0%94%E6%B5%81%E6%B4%BE%EF%BC%817891%E7%8C%AE%E7%A5%AD%E6%B5%81%EF%BC%81%E6%AF%8F%E5%A4%A9%E7%A8%B3%E5%AE%9A%E4%B8%8A%E5%88%86")

# 定位你能找到的div容器
container = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[@id='i_cecream']/div/div[2]/div[2]/div/div/div/div[2]"))
)
# 打印div的完整HTML（能看到所有子元素）
print("目标div的完整HTML：\n", container.get_attribute('outerHTML'))