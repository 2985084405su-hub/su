import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smart_locator import SmartLocator, click_interactable, ScrollHandler, IFrameHandler, select_subscribe_title

#单包
def dan_card_subscribe(subscribe_data):
    """卡支付单包订阅流程"""
    chrome_options = Options()

    chrome_options.add_experimental_option(
        "mobileEmulation", 
        {"deviceName": "iPhone 12 Pro"}
    )
    # 创建 driver 实例（带移动端模拟）
    driver = webdriver.Chrome(options=chrome_options)
    # 然后初始化 SmartLocator
    locator = SmartLocator(driver)
    driver.implicitly_wait(5)
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))

    #点击FOR YOU
    profile_btn = locator.find_element("xpath=//span[text()='For You']")
    click_interactable(profile_btn, driver)
    #点击watch now按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
    click_interactable(subscribe_btn, driver)
    #点击屏幕
    trigger = locator.find_element("class=trigger")
    click_interactable(trigger, driver)
    #选择剧集
    episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
    click_interactable(episode_element, driver)
    #点击锁按钮
    lock_btn= locator.find_element("class=lock")
    click_interactable(lock_btn, driver)
    #取消选择订阅类型
    closeIcon_btn = locator.find_element("class=closeIcon")
    click_interactable(closeIcon_btn, driver)
    #点击paynow按钮
    paynow_btn = locator.find_element("xpath=//div[@class='btn' and text()='Pay Now']")
    click_interactable(paynow_btn, driver)
    #选择订阅类型
    # card_payment_btn = locator.find_element("xpath=//div[@class='card-payment-box' and text()='Card Payment']")
    # click_interactable(card_payment_btn, driver)
    #填写支付信息
    card_number_input = locator.find_element("name=card_no")
    card_number_input.clear()
    card_number_input.send_keys("4111111111111111")
    email_input = locator.find_element("name=email")
    email_input.clear()
    email_input.send_keys("2985084405@gmail.com")
    expire_date_input = locator.find_element("name=expire_date")
    expire_date_input.clear()
    expire_date_input.send_keys("03/30")
    cvv_input = locator.find_element("name=cvv")
    cvv_input.clear()
    cvv_input.send_keys("737")
    first_name_input = locator.find_element("css=input[placeholder='FirstName']")
    first_name_input.clear()
    first_name_input.send_keys("John")
    last_name_input = locator.find_element("css=input[placeholder='LastName']")
    last_name_input.clear()
    last_name_input.send_keys("John")
    #提交支付
    paynow_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Pay Now']")
    click_interactable(paynow_btn, driver)
    try:
        driver.implicitly_wait(0.5)
        time.sleep(0.5)
        # 捕获支付失败的错误信息
        error_msg = locator.find_element("xpath=//div[@class='error-msg' and @style='']")
        error_msg_text = error_msg.text
        print(f"错误信息: {error_msg_text}")
        print("支付失败，结束脚本")
    except:
        try:
            driver.implicitly_wait(5)
            # 处理 3D 认证
            cheek_3d_input = locator.find_element("name=challengeDataEntry")
            cheek_3d_input.clear()
            cheek_3d_input.send_keys("1234")
            cheek_3d_btn = locator.find_element("id=submit")
            click_interactable(cheek_3d_btn, driver)
            print("3D认证通过")
        except:
            print("无需3D认证")
    time.sleep(3)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()

#挽留周
def week_card_subscribe(subscribe_data):
    """卡支付单包订阅流程"""
    chrome_options = Options()

    chrome_options.add_experimental_option(
        "mobileEmulation", 
        {"deviceName": "iPhone 12 Pro"}
    )
    # 创建 driver 实例（带移动端模拟）
    driver = webdriver.Chrome(options=chrome_options)
    # 然后初始化 SmartLocator
    locator = SmartLocator(driver)
    driver.implicitly_wait(5)
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))

    #点击FOR YOU
    profile_btn = locator.find_element("xpath=//span[text()='For You']")
    click_interactable(profile_btn, driver)
    #点击watch now按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
    click_interactable(subscribe_btn, driver)
    #点击屏幕
    trigger = locator.find_element("class=trigger")
    click_interactable(trigger, driver)
    #选择剧集
    episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
    click_interactable(episode_element, driver)
    #点击锁按钮
    lock_btn= locator.find_element("class=lock")
    click_interactable(lock_btn, driver)
    #取消选择订阅类型
    closeIcon_btn = locator.find_element("class=closeIcon")
    click_interactable(closeIcon_btn, driver)
    #点击paynow按钮
    gonow_btn = locator.find_element("class=surprese-bottom-box")
    click_interactable(gonow_btn, driver)
    #选择订阅类型
    # card_payment_btn = locator.find_element("xpath=//div[@class='card-payment-box' and text()='Card Payment']")
    # click_interactable(card_payment_btn, driver)
    #填写支付信息
    card_number_input = locator.find_element("name=card_no")
    card_number_input.clear()
    card_number_input.send_keys("4111111111111111")
    email_input = locator.find_element("name=email")
    email_input.clear()
    email_input.send_keys("2985084405@gmail.com")
    expire_date_input = locator.find_element("name=expire_date")
    expire_date_input.clear()
    expire_date_input.send_keys("03/30")
    cvv_input = locator.find_element("name=cvv")
    cvv_input.clear()
    cvv_input.send_keys("737")
    first_name_input = locator.find_element("css=input[placeholder='FirstName']")
    first_name_input.clear()
    first_name_input.send_keys("John")
    last_name_input = locator.find_element("css=input[placeholder='LastName']")
    last_name_input.clear()
    last_name_input.send_keys("John")
    #提交支付
    paynow_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Pay Now']")
    click_interactable(paynow_btn, driver)
    try:
        driver.implicitly_wait(0.5)
        time.sleep(0.5)
        # 捕获支付失败的错误信息
        error_msg = locator.find_element("xpath=//div[@class='error-msg' and @style='']")
        error_msg_text = error_msg.text
        print(f"错误信息: {error_msg_text}")
        print("支付失败，结束脚本")
    except:
        try:
            driver.implicitly_wait(5)
            # 处理 3D 认证
            cheek_3d_input = locator.find_element("name=challengeDataEntry")
            cheek_3d_input.clear()
            cheek_3d_input.send_keys("1234")
            cheek_3d_btn = locator.find_element("id=submit")
            click_interactable(cheek_3d_btn, driver)
            print("3D认证通过")
        except:
            print("无需3D认证")
    time.sleep(3)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()

#体验周
def experience_subscribe(subscribe_data):
    """卡支付单包订阅流程"""
    chrome_options = Options()

    chrome_options.add_experimental_option(
        "mobileEmulation", 
        {"deviceName": "iPhone 12 Pro"}
    )
    # 创建 driver 实例（带移动端模拟）
    driver = webdriver.Chrome(options=chrome_options)
    # 然后初始化 SmartLocator
    locator = SmartLocator(driver)
    driver.implicitly_wait(5)
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))

    #点击FOR YOU
    profile_btn = locator.find_element("xpath=//span[text()='For You']")
    click_interactable(profile_btn, driver)
    #点击watch now按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
    click_interactable(subscribe_btn, driver)
    #点击屏幕
    trigger = locator.find_element("class=trigger")
    click_interactable(trigger, driver)
    #选择剧集
    episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
    click_interactable(episode_element, driver)
    #点击锁按钮
    lock_btn= locator.find_element("class=lock")
    click_interactable(lock_btn, driver)
    #取消选择订阅类型
    closeIcon_btn = locator.find_element("class=closeIcon")
    click_interactable(closeIcon_btn, driver)
    #点击paynow按钮
    sidebar = locator.find_element("class=_retainOnce_1fdak_12")
    btn_box_btn = locator.find_element("class=btn-box", context=sidebar)
    click_interactable(btn_box_btn, driver)

    sidebar = locator.find_element("class=_surpriseButtonList_14kt4_1")
    surprise_btn = locator.find_element("class=card-payment-box", context=sidebar)

    click_interactable(surprise_btn, driver)
    #选择订阅类型
    # card_payment_btn = locator.find_element("xpath=//div[@class='card-payment-box' and text()='Card Payment']")
    # click_interactable(card_payment_btn, driver)
    #填写支付信息
    card_number_input = locator.find_element("name=card_no")
    card_number_input.clear()
    card_number_input.send_keys("4111111111111111")
    email_input = locator.find_element("name=email")
    email_input.clear()
    email_input.send_keys("2985084405@gmail.com")
    expire_date_input = locator.find_element("name=expire_date")
    expire_date_input.clear()
    expire_date_input.send_keys("03/30")
    cvv_input = locator.find_element("name=cvv")
    cvv_input.clear()
    cvv_input.send_keys("737")
    first_name_input = locator.find_element("css=input[placeholder='FirstName']")
    first_name_input.clear()
    first_name_input.send_keys("John")
    last_name_input = locator.find_element("css=input[placeholder='LastName']")
    last_name_input.clear()
    last_name_input.send_keys("John")
    #提交支付
    paynow_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Pay Now']")
    click_interactable(paynow_btn, driver)
    try:
        driver.implicitly_wait(0.5)
        time.sleep(0.5)
        # 捕获支付失败的错误信息
        error_msg = locator.find_element("xpath=//div[@class='error-msg' and @style='']")
        error_msg_text = error_msg.text
        print(f"错误信息: {error_msg_text}")
        print("支付失败，结束脚本")
    except:
        try:
            driver.implicitly_wait(5)
            # 处理 3D 认证
            cheek_3d_input = locator.find_element("name=challengeDataEntry")
            cheek_3d_input.clear()
            cheek_3d_input.send_keys("1234")
            cheek_3d_btn = locator.find_element("id=submit")
            click_interactable(cheek_3d_btn, driver)
            print("3D认证通过")
        except:
            print("无需3D认证")
    time.sleep(3)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()




subscribe_data = select_subscribe_title('VAVA', 2)



if __name__ == "__main__":
    dan_card_subscribe(subscribe_data)