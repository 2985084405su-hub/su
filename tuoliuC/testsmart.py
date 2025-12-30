import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smart_locator import SmartLocator, click_interactable, ScrollHandler, IFrameHandler, select_subscribe_title
import os
import sys


def setup_browser():
    # 读取无头模式设置
    headless_mode = os.environ.get('HEADLESS', 'True').lower() == 'true'
    
    # 立即打印调试信息，确保输出被看到
    print(f"DEBUG: 无头模式设置: {headless_mode}")
    print(f"DEBUG: HEADLESS环境变量: {os.environ.get('HEADLESS')}")
    sys.stdout.flush()  # 强制刷新输出
    
    # 配置浏览器选项
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "mobileEmulation", 
        {"deviceName": "iPhone 12 Pro"}
    )
    
    # 需要在创建 driver 实例之前添加无头模式参数
    if headless_mode:
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 创建 driver 实例（带移动端模拟）
    print(f"DEBUG: 创建浏览器驱动，无头模式: {headless_mode}")
    sys.stdout.flush()
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 然后初始化 SmartLocator
    locator = SmartLocator(driver)
    iframe_handler = IFrameHandler(driver)
    scroll_handler = ScrollHandler(driver)
    
    return driver, locator, iframe_handler ,scroll_handler


# 从环境变量获取参数，支持空值
def get_env_variable(name, default=None):
    """从环境变量获取参数"""
    value = os.environ.get(name)
    
    # 调试输出，查看实际接收到的值
    print(f"DEBUG: 获取环境变量 {name} = '{value}' (原始), 默认值 = '{default}'")
    sys.stdout.flush()
    
    if value is None:
        # 环境变量不存在
        print(f"DEBUG: 环境变量 {name} 不存在，使用默认值: {default}")
        sys.stdout.flush()
        return default
    elif value == '':
        # 环境变量存在但为空字符串
        print(f"DEBUG: 环境变量 {name} 为空字符串，使用默认值: {default}")
        sys.stdout.flush()
        return default
    else:
        # 环境变量有值
        print(f"DEBUG: 环境变量 {name} 有值: {value}")
        sys.stdout.flush()
        return value



# 卡支付个人中心订阅流程
def profile_card_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """卡支付个人中心订阅流程"""
    # chrome_options = Options()
    # chrome_options.add_experimental_option(
    #     "mobileEmulation", 
    #     {"deviceName": "iPhone 12 Pro"}
    # )
    # # 创建 driver 实例（带移动端模拟）
    # driver = webdriver.Chrome(options=chrome_options)
    # # 然后初始化 SmartLocator
    # locator = SmartLocator(driver)
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
    driver.implicitly_wait(5)
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))
    #点击个人中心
    profile_btn = locator.find_element("xpath=//span[text()='Profile']")
    click_interactable(profile_btn, driver)
    #点击订阅按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
    click_interactable(subscribe_btn, driver)
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付方式
    card_payment_btn = locator.find_element("xpath=//button[contains(@class, 'pay-btn') and not(@style)]")
    click_interactable(card_payment_btn, driver)
    #填写支付信息
    card_number_input = locator.find_element("name=card_no")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    email_input = locator.find_element("name=email")
    email_input.clear()
    email_input.send_keys(user_email)
    expire_date_input = locator.find_element("name=expire_date")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("name=cvv")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
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
        driver.implicitly_wait(2)
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
    time.sleep(10)
    driver.refresh()
    time.sleep(0.5)
    uuid_test = locator.find_element("class=userId")
    full_text = uuid_test.text
    print(f"完整文本: {full_text}")
    print("等待 30 秒后关闭...")
    time.sleep(10)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# 卡支付FOR YOU 订阅流程
def foryou_card_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """卡支付FOR YOU 订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
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
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付方式
    card_payment_btn = locator.find_element("xpath=//div[@class='card-payment-box' and text()='Card Payment']")
    click_interactable(card_payment_btn, driver)
    #填写支付信息
    card_number_input = locator.find_element("name=card_no")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    email_input = locator.find_element("name=email")
    email_input.clear()
    email_input.send_keys(user_email)
    expire_date_input = locator.find_element("name=expire_date")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("name=cvv")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
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
        driver.implicitly_wait(2)
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
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)


# PayPal支付个人中心订阅流程
def profile_paypal_subscribe(subscribe_data, user_email):
    """PayPal支付个人中心订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
    driver.implicitly_wait(5)
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))
    #点击个人中心
    profile_btn = locator.find_element("xpath=//span[text()='Profile']")
    click_interactable(profile_btn, driver)
    #点击订阅按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
    click_interactable(subscribe_btn, driver)
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付方式
    paypal_payment_btn = locator.find_element("class=paypal-btn")
    click_interactable(paypal_payment_btn, driver)
    #paypal支付页面输入账号
    paypal_email_input = locator.find_element("id=email")
    paypal_email_input.clear()
    paypal_email_input.send_keys(user_email)
    #点击下一步
    paypal_btnNext = locator.find_element("id=btnNext")
    click_interactable(paypal_btnNext, driver)
    #输入密码
    paypal_password_input = locator.find_element("id=password")
    paypal_password_input.clear()
    paypal_password_input.send_keys("Ye123456")
    #点击登录
    paypal_btnLogin = locator.find_element("id=btnLogin")
    click_interactable(paypal_btnLogin, driver)
    #同意支付
    paypal_consentButton = locator.find_element("id=consentButton")
    click_interactable(paypal_consentButton, driver)
    time.sleep(10)
    driver.refresh()
    time.sleep(0.5)
    uuid_test = locator.find_element("class=userId")
    full_text = uuid_test.text
    print(f"完整文本: {full_text}")
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# PayPal支付FOR YOU 订阅流程
def foryou_paypal_subscribe(subscribe_data, user_email):
    """ PayPal支付FOR YOU 订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
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
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付方式
    paypal_payment_btn = locator.find_element("class=paypal-btn")
    click_interactable(paypal_payment_btn, driver)
    #paypal支付页面输入账号
    paypal_email_input = locator.find_element("id=email")
    paypal_email_input.clear()
    paypal_email_input.send_keys(user_email)
    #点击下一步
    paypal_btnNext = locator.find_element("id=btnNext")
    click_interactable(paypal_btnNext, driver)
    #输入密码
    paypal_password_input = locator.find_element("id=password")
    paypal_password_input.clear()
    paypal_password_input.send_keys("Ye123456")
    #点击登录
    paypal_btnLogin = locator.find_element("id=btnLogin")
    click_interactable(paypal_btnLogin, driver)
    #同意支付
    paypal_consentButton = locator.find_element("id=consentButton")
    click_interactable(paypal_consentButton, driver)
    time.sleep(10)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)





# 老aw_more支付个人中心订阅流程
def profile_awoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """ 老aw_more支付个人中心订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
    driver.implicitly_wait(5)
    
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))
    #点击个人中心
    profile_btn = locator.find_element("xpath=//span[text()='Profile']")
    click_interactable(profile_btn, driver)
    #点击订阅按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
    click_interactable(subscribe_btn, driver)
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    time.sleep(2)
    #输入聚合支付邮箱
    sidebar = locator.find_element("class=van-field__body")
    eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
    eamil_more_input.clear()
    eamil_more_input.send_keys(user_email)
    #提交邮箱
    more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
    click_interactable(more_contirm_btn, driver)
    #填写支付信息
    us_flag = locator.find_element("css=img[alt='US']")
    click_interactable(us_flag, driver)
    time.sleep(1)
    card_number_input = locator.find_element("id=cardNumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("id=cardExpiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("id=cardCvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("id=billingName")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    time.sleep(1)
    scroll_handler.scroll_to_bottom()
    pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
    click_interactable(pay_more_btn, driver)
    # try:
    #     # 处理 3D 认证
    #     cheek_3d_input = locator.find_element("name=challengeDataEntry")
    #     cheek_3d_input.clear()
    #     cheek_3d_input.send_keys("1234")
    #     cheek_3d_btn = locator.find_element("id=submit")
    #     click_interactable(cheek_3d_btn, driver)
    #     print("3D认证通过")
    # except:
    #     print("无需3D认证")
    time.sleep(10)
    driver.refresh()
    time.sleep(0.5)
    uuid_test = locator.find_element("class=userId")
    full_text = uuid_test.text
    print(f"完整文本: {full_text}")
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# 老aw_more支付FOR YOU 订阅流程
def foryou_awoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """ 老aw_more支付FOR YOU 订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
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
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    time.sleep(2)
    #输入聚合支付邮箱
    sidebar = locator.find_element("class=van-field__body")
    eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
    eamil_more_input.clear()
    eamil_more_input.send_keys(user_email)
    #提交邮箱
    more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
    click_interactable(more_contirm_btn, driver)
    #填写支付信息
    us_flag = locator.find_element("css=img[alt='US']")
    click_interactable(us_flag, driver)
    time.sleep(1)
    card_number_input = locator.find_element("id=cardNumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("id=cardExpiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("id=cardCvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("id=billingName")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    scroll_handler.scroll_to_bottom()
    pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
    click_interactable(pay_more_btn, driver)
    # try:
    #     # 处理 3D 认证
    #     cheek_3d_input = locator.find_element("name=challengeDataEntry")
    #     cheek_3d_input.clear()
    #     cheek_3d_input.send_keys("1234")
    #     cheek_3d_btn = locator.find_element("id=submit")
    #     click_interactable(cheek_3d_btn, driver)
    #     print("3D认证通过")
    # except:
    #     print("无需3D认证")
    time.sleep(10)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# 老st_more支付个人中心订阅流程
def profile_stoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """老st_more支付个人中心订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
    driver.implicitly_wait(5)
    
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))
    #点击个人中心
    profile_btn = locator.find_element("xpath=//span[text()='Profile']")
    click_interactable(profile_btn, driver)
    #点击订阅按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
    click_interactable(subscribe_btn, driver)
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    time.sleep(2)
    #填写支付信息
    us_flag = locator.find_element("css=img[alt='US']")
    click_interactable(us_flag, driver)
    time.sleep(1)
    eaml_more_input = locator.find_element("id=email")
    eaml_more_input.clear()
    eaml_more_input.send_keys(user_email)
    card_number_input = locator.find_element("id=cardNumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("id=cardExpiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("id=cardCvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("id=billingName")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    scroll_handler.scroll_to_bottom()
    pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
    click_interactable(pay_more_btn, driver)
    # try:
    #     # 处理 3D 认证
    #     cheek_3d_input = locator.find_element("name=challengeDataEntry")
    #     cheek_3d_input.clear()
    #     cheek_3d_input.send_keys("1234")
    #     cheek_3d_btn = locator.find_element("id=submit")
    #     click_interactable(cheek_3d_btn, driver)
    #     print("3D认证通过")
    # except:
    #     print("无需3D认证")
    time.sleep(10)
    driver.refresh()
    time.sleep(0.5)
    uuid_test = locator.find_element("class=userId")
    full_text = uuid_test.text
    print(f"完整文本: {full_text}")
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)


# 老st_more支付FOR YOU 订阅流程
def foryou_stoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """ 老st_more支付FOR YOU 订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
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
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    time.sleep(2)
    #填写支付信息
    us_flag = locator.find_element("css=img[alt='US']")
    click_interactable(us_flag, driver)
    time.sleep(1)
    eaml_more_input = locator.find_element("id=email")
    eaml_more_input.clear()
    eaml_more_input.send_keys(user_email)
    card_number_input = locator.find_element("id=cardNumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("id=cardExpiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("id=cardCvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("id=billingName")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    scroll_handler.scroll_to_bottom()
    pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
    click_interactable(pay_more_btn, driver)
    # try:
    #     # 处理 3D 认证
    #     cheek_3d_input = locator.find_element("name=challengeDataEntry")
    #     cheek_3d_input.clear()
    #     cheek_3d_input.send_keys("1234")
    #     cheek_3d_btn = locator.find_element("id=submit")
    #     click_interactable(cheek_3d_btn, driver)
    #     print("3D认证通过")
    # except:
    #     print("无需3D认证")
    time.sleep(10)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# 新aw_more支付个人中心订阅流程
def profile_awnewmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """新aw_more支付个人中心订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
    driver.implicitly_wait(5)
    
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))
    #点击个人中心
    profile_btn = locator.find_element("xpath=//span[text()='Profile']")
    click_interactable(profile_btn, driver)
    #点击订阅按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
    click_interactable(subscribe_btn, driver)
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    time.sleep(2)
    #输入聚合支付邮箱
    sidebar = locator.find_element("class=van-field__body")
    eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
    eamil_more_input.clear()
    eamil_more_input.send_keys(user_email)
    #提交邮箱
    more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
    click_interactable(more_contirm_btn, driver)
    #填写支付信息
    time.sleep(1)
    card_number_input = locator.find_element("name=cardnumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("name=expiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("name=cvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("name=name")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    pay_more_btn = locator.find_element("class=css-yen4e3")
    click_interactable(pay_more_btn, driver)
    try:
        # 处理 3D 认证
        iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
        # 现在在 iframe 内，可以操作 iframe 内的元素
        code_input = locator.find_element("id=challengeDataEntry")
        code_input.clear()
        code_input.send_keys("1234")
        submit_btn = locator.find_element("id=submit")
        click_interactable(submit_btn, driver)
        # 切回主文档
        # iframe_handler.switch_to.default_content()
        print("3D认证通过")
    except:
        print("无需3D认证")
    time.sleep(5)
    driver.refresh()
    time.sleep(0.5)
    uuid_test = locator.find_element("class=userId")
    full_text = uuid_test.text
    print(f"完整文本: {full_text}")
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# 新aw_more支付FOR YOU 订阅流程
def foryou_awnewmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    """ 新aw_more支付FOR YOU 订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
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
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    time.sleep(2)
    #输入聚合支付邮箱
    sidebar = locator.find_element("class=van-field__body")
    eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
    eamil_more_input.clear()
    eamil_more_input.send_keys(user_email)
    #提交邮箱
    more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
    click_interactable(more_contirm_btn, driver)
    #填写支付信息
    time.sleep(1)
    card_number_input = locator.find_element("name=cardnumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("name=expiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("name=cvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("name=name")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    pay_more_btn = locator.find_element("class=css-yen4e3")
    click_interactable(pay_more_btn, driver)
    try:
        # 处理 3D 认证
        iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
        # 现在在 iframe 内，可以操作 iframe 内的元素
        code_input = locator.find_element("id=challengeDataEntry")
        code_input.clear()
        code_input.send_keys("1234")
        submit_btn = locator.find_element("id=submit")
        click_interactable(submit_btn, driver)
        # 切回主文档
        # iframe_handler.switch_to.default_content()
        print("3D认证通过")
    except:
        print("无需3D认证")
    time.sleep(5)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# 新st_more支付个人中心订阅流程
def profile_stnewmore_subscribe(subscribe_data, card_no, card_expire, card_cvv):
    """新st_more支付个人中心订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
    driver.implicitly_wait(5)
    
    # 访问网站
    driver.get("https://{}".format(subscribe_data[0]))
    #点击个人中心
    profile_btn = locator.find_element("xpath=//span[text()='Profile']")
    click_interactable(profile_btn, driver)
    #点击订阅按钮
    subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
    click_interactable(subscribe_btn, driver)
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    #填写支付信息
    time.sleep(1)
    card_number_input = locator.find_element("name=cardnumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("name=expiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("name=cvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("name=name")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    pay_more_btn = locator.find_element("class=css-yen4e3")
    click_interactable(pay_more_btn, driver)
    try:
        # 处理 3D 认证
        iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
        # 现在在 iframe 内，可以操作 iframe 内的元素
        code_input = locator.find_element("id=challengeDataEntry")
        code_input.clear()
        code_input.send_keys("1234")
        submit_btn = locator.find_element("id=submit")
        click_interactable(submit_btn, driver)
        # 切回主文档
        # iframe_handler.switch_to.default_content()
        print("3D认证通过")
    except:
        print("无需3D认证")
    time.sleep(5)
    driver.refresh()
    time.sleep(0.5)
    uuid_test = locator.find_element("class=userId")
    full_text = uuid_test.text
    print(f"完整文本: {full_text}")
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)

# 新st_more支付FOR YOU 订阅流程
def foryou_stnewmore_subscribe(subscribe_data, card_no, card_expire, card_cvv):
    """新st_more支付FOR YOU 订阅流程"""
    driver, locator, iframe_handler ,scroll_handler= setup_browser()
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
    #选择订阅类型
    subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
    click_interactable(subscribe_type_btn, driver)
    #选择支付类型
    subscribe_type_btn = locator.find_element("class=stripe-btn")
    click_interactable(subscribe_type_btn, driver)
    #填写支付信息
    time.sleep(1)
    card_number_input = locator.find_element("name=cardnumber")
    card_number_input.clear()
    card_number_input.send_keys(card_no)
    expire_date_input = locator.find_element("name=expiry")
    expire_date_input.clear()
    expire_date_input.send_keys(card_expire)
    cvv_input = locator.find_element("name=cvc")
    cvv_input.clear()
    cvv_input.send_keys(card_cvv)
    name_input = locator.find_element("name=name")
    name_input.clear()
    name_input.send_keys("sxy sxy")
    #提交支付
    pay_more_btn = locator.find_element("class=css-yen4e3")
    click_interactable(pay_more_btn, driver)
    try:
        # 处理 3D 认证
        iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
        # 现在在 iframe 内，可以操作 iframe 内的元素
        code_input = locator.find_element("id=challengeDataEntry")
        code_input.clear()
        code_input.send_keys("1234")
        submit_btn = locator.find_element("id=submit")
        click_interactable(submit_btn, driver)
        # 切回主文档
        # iframe_handler.switch_to.default_content()
        print("3D认证通过")
    except:
        print("无需3D认证")
    time.sleep(5)
    driver.refresh()
    print("等待 30 秒后关闭...")
    time.sleep(30)
    driver.quit()
    print("=" * 50)
    print("测试执行完成")
    print("=" * 50)


def subscribe_test(site_name='VAVA',
                   subscribe_type=2,
                   pay_type=1,
                   user_email='2985084405su@gmail.com',
                   card_no='4111111111111111',
                   card_expire='03/30',
                   card_cvv='737'
                   ):
    """订阅测试主函数"""
    subscribe_data = select_subscribe_title(site_name, subscribe_type)
    match pay_type:
        case 1:
            profile_card_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 2:
            foryou_card_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 3:
            # 注意：PayPal测试使用特定的测试邮箱
            profile_paypal_subscribe(subscribe_data, "sx-duanjuceshi@personal.example.com")
        case 4:
            foryou_paypal_subscribe(subscribe_data, "sx-duanjuceshi@personal.example.com")
        case 5:
            profile_awoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 6:
            foryou_awoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 7:
            profile_stoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 8:
            foryou_stoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 9:
            profile_awnewmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 10:
            foryou_awnewmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv)
        case 11:
            profile_stnewmore_subscribe(subscribe_data, card_no, card_expire, card_cvv)
        case 12:
            foryou_stnewmore_subscribe(subscribe_data, card_no, card_expire, card_cvv)
        case _:
            print("无效的支付类型")

def subscribe_test_from_env():
    """从环境变量运行测试"""
    # 获取参数，正确处理空值
    site_name = get_env_variable('site_name', 'VAVA')
    subscribe_type = int(get_env_variable('subscribe_type', '2'))
    pay_type = int(get_env_variable('pay_type', '1'))
    
    # 获取支付相关参数
    user_email = get_env_variable('user_email', '2985084405su@gmail.com')
    card_no = get_env_variable('card_no', '4111111111111111')
    card_expire = get_env_variable('card_expire', '03/30')
    card_cvv = get_env_variable('card_cvv', '737')
    
    # 打印实际使用的值
    print("=" * 50)
    print("实际使用的参数值:")
    print(f"站点名称: {site_name}")
    print(f"订阅类型: {subscribe_type}")
    print(f"支付类型: {pay_type}")
    print(f"用户邮箱: {user_email}")
    print(f"信用卡号: {card_no}")
    print(f"信用卡有效期: {card_expire}")
    print(f"CVV安全码: {card_cvv}")
    print("=" * 50)
    
    # 运行测试
    subscribe_test(site_name, subscribe_type, pay_type, user_email, card_no, card_expire, card_cvv)

if __name__ == "__main__":
    # 修改为调用从环境变量运行的函数
    subscribe_test_from_env()














# if __name__ == "__main__":
#     #1-个人中心信用卡支付 2-For You信用卡支付 3-个人中心PayPal支付 4-For You PayPal支付
#     #5-个人中心老aw_more支付 6-For You老aw_more支付 7-个人中心老st_more支付 8-For You老st_more支付
#     #9-个人中心新aw_more支付 10-For You新aw_more支付 11-个人中心新st_more支付 12-For You新st_more支付
#     subscribe_test('VIVI',3,5)