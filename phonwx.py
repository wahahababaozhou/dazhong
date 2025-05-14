import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
#
# desired_caps = {
#     "platformName": "Android",
#     "deviceName": "127.0.0.1:16384",  # 替换为你模拟器的端口号
#     "appPackage": "com.tencent.mm",
#     "appActivity": ".ui.LauncherUI",
#     "automationName": "UiAutomator2",
#     "noReset": True,
#     "dontStopAppOnReset": True
# }
#
# options = UiAutomator2Options().load_capabilities(desired_caps)
# driver = webdriver.Remote("http://localhost:4723", options=options)
# wait = WebDriverWait(driver, 5)
#
#
# def publish_group_notice(msg):
#     try:
#         print("✅ 点击群公告")
#         notice = wait.until(EC.presence_of_element_located(
#             (AppiumBy.XPATH, "//*[@text='群公告']")
#         ))
#         notice.click()
#
#         print("✅ 点击编辑群公告")
#         edit_btn = wait.until(EC.presence_of_element_located(
#             (AppiumBy.XPATH, "//*[@text='编辑']")
#         ))
#         edit_btn.click()
#
#         print("✅ 输入群公告内容")
#         input_box = wait.until(EC.presence_of_element_located(
#             (AppiumBy.CLASS_NAME, "android.widget.EditText")
#         ))
#         input_box.clear()
#         input_box.send_keys(
#             msg)
#
#         print("✅ 发布群公告")
#         send_btn = wait.until(EC.presence_of_element_located(
#             (AppiumBy.XPATH, "//*[@text='完成']")
#         ))
#         send_btn.click()
#
#         send_btn = wait.until(EC.presence_of_element_located(
#             (AppiumBy.XPATH, "//*[@text='发布']")
#         ))
#         send_btn.click()
#         print("🎉 群公告已成功发布！")
#
#     except Exception as e:
#         print("❌ 出现异常:", e)
#
#     finally:
#         time.sleep(5)
#         driver.quit()
# if __name__ == "__main__":
#     publish_group_notice("@所有人 请注意：今晚 9 点进行系统升级，提前保存好工作内容～")