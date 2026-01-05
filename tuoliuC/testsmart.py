import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smart_locator import SmartLocator, click_interactable, ScrollHandler, IFrameHandler, select_subscribe_title
import os
import sys

# Constants for API Capture
TARGET_APIS = ['api/subscribe/create', 'api/subscribe/check-payment-url']

def get_env_variable(name, default=None):
    """从环境变量获取参数"""
    value = os.environ.get(name)
    print(f"DEBUG: 获取环境变量 {name} = '{value}' (原始), 默认值 = '{default}'")
    if value is None:
        return default
    elif value == '':
        return default
    else:
        return value

def init_driver_with_logging():
    """初始化带有性能日志记录的Driver"""
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "mobileEmulation", 
        {"deviceName": "iPhone 12 Pro"}
    )
    # 开启性能日志
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def capture_and_print_api_traffic(driver):
    """捕获并打印API流量信息"""
    try:
        # 获取性能日志
        logs = driver.get_log('performance')
        
        for entry in logs:
            try:
                message = json.loads(entry['message'])['message']
                method = message.get('method')
                params = message.get('params', {})
                request_id = params.get('requestId')
                
                # 检查是否是我们关注的请求
                if method == 'Network.responseReceived':
                    response = params.get('response', {})
                    url = response.get('url', '')
                    
                    if any(api in url for api in TARGET_APIS):
                        # 获取响应体
                        response_body = "无法获取或为空"
                        try:
                            res_body_data = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                            response_body = res_body_data.get('body', '')
                        except Exception as e:
                            response_body = f"获取失败: {str(e)}"

                        # 构造输出数据
                        api_data = {
                            "url": url,
                            "requestId": request_id,
                            "status": response.get('status'),
                            "response_headers": response.get('headers'),
                            "response_body": response_body,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # 尝试查找对应的请求信息 (注意：这里简化处理，实际请求信息通常在 requestWillBeSent 中)
                        # 为了演示，我们标记一下，前端可以据此展示
                        print(f"__API_CAPTURE__|{json.dumps(api_data)}")
                        
                elif method == 'Network.requestWillBeSent':
                    request = params.get('request', {})
                    url = request.get('url', '')
                    
                    if any(api in url for api in TARGET_APIS):
                        request_body = request.get('postData', '无请求体或非文本格式')
                        
                        api_data = {
                            "url": url,
                            "requestId": request_id,
                            "type": "request",
                            "request_headers": request.get('headers'),
                            "request_body": request_body,
                            "method": request.get('method')
                        }
                        print(f"__API_CAPTURE__|{json.dumps(api_data)}")
                        
            except Exception as e:
                pass
                
    except Exception as e:
        print(f"日志捕获错误: {str(e)}")

def wait_and_capture(driver, seconds):
    """等待指定时间并持续捕获日志"""
    end_time = time.time() + seconds
    while time.time() < end_time:
        capture_and_print_api_traffic(driver)
        time.sleep(0.5)

# 卡支付个人中心订阅流程
def profile_card_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        
        # 流程操作...
        profile_btn = locator.find_element("xpath=//span[text()='Profile']")
        click_interactable(profile_btn, driver)
        
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
        click_interactable(subscribe_btn, driver)
        
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        card_payment_btn = locator.find_element("xpath=//button[contains(@class, 'pay-btn') and not(@style)]")
        click_interactable(card_payment_btn, driver)
        
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
        
        # 提交支付
        paynow_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Pay Now']")
        click_interactable(paynow_btn, driver)
        
        # 关键点：在支付后持续捕获日志
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 5) # 捕获5秒
        
        try:
            driver.implicitly_wait(2)
            time.sleep(0.5)
            error_msg = locator.find_element("xpath=//div[@class='error-msg' and @style='']")
            error_msg_text = error_msg.text
            print(f"错误信息: {error_msg_text}")
            print("支付失败，结束脚本")
        except:
            try:
                driver.implicitly_wait(5)
                cheek_3d_input = locator.find_element("name=challengeDataEntry")
                cheek_3d_input.clear()
                cheek_3d_input.send_keys("1234")
                cheek_3d_btn = locator.find_element("id=submit")
                click_interactable(cheek_3d_btn, driver)
                print("3D认证通过")
            except:
                print("无需3D认证")
        
        # 刷新前再捕获一波
        wait_and_capture(driver, 5)
        
        time.sleep(0.5)
        uuid_test = locator.find_element("class=userId")
        full_text = uuid_test.text
        print(f"完整文本: {full_text}")
        
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
        
    finally:
        driver.quit()

# 卡支付FOR YOU 订阅流程
def foryou_card_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))

        profile_btn = locator.find_element("xpath=//span[text()='For You']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
        click_interactable(subscribe_btn, driver)
        trigger = locator.find_element("class=trigger")
        click_interactable(trigger, driver)
        episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
        click_interactable(episode_element, driver)
        lock_btn= locator.find_element("class=lock")
        click_interactable(lock_btn, driver)
        
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        card_payment_btn = locator.find_element("xpath=//div[@class='card-payment-box' and text()='Card Payment']")
        click_interactable(card_payment_btn, driver)
        
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
        
        paynow_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Pay Now']")
        click_interactable(paynow_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 5)
        
        try:
            driver.implicitly_wait(2)
            time.sleep(0.5)
            error_msg = locator.find_element("xpath=//div[@class='error-msg' and @style='']")
            error_msg_text = error_msg.text
            print(f"错误信息: {error_msg_text}")
            print("支付失败，结束脚本")
        except:
            try:
                driver.implicitly_wait(5)
                cheek_3d_input = locator.find_element("name=challengeDataEntry")
                cheek_3d_input.clear()
                cheek_3d_input.send_keys("1234")
                cheek_3d_btn = locator.find_element("id=submit")
                click_interactable(cheek_3d_btn, driver)
                print("3D认证通过")
            except:
                print("无需3D认证")
        
        wait_and_capture(driver, 3)
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# PayPal支付个人中心订阅流程
def profile_paypal_subscribe(subscribe_data, user_email):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        
        profile_btn = locator.find_element("xpath=//span[text()='Profile']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
        click_interactable(subscribe_btn, driver)
        
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        paypal_payment_btn = locator.find_element("class=paypal-btn")
        click_interactable(paypal_payment_btn, driver)
        
        # 捕获可能的 API 调用
        wait_and_capture(driver, 2)
        
        paypal_email_input = locator.find_element("id=email")
        paypal_email_input.clear()
        paypal_email_input.send_keys(user_email)
        paypal_btnNext = locator.find_element("id=btnNext")
        click_interactable(paypal_btnNext, driver)
        
        paypal_password_input = locator.find_element("id=password")
        paypal_password_input.clear()
        paypal_password_input.send_keys("Ye123456")
        paypal_btnLogin = locator.find_element("id=btnLogin")
        click_interactable(paypal_btnLogin, driver)
        
        paypal_consentButton = locator.find_element("id=consentButton")
        click_interactable(paypal_consentButton, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 10)
        
        time.sleep(0.5)
        uuid_test = locator.find_element("class=userId")
        full_text = uuid_test.text
        print(f"完整文本: {full_text}")
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# PayPal支付FOR YOU 订阅流程
def foryou_paypal_subscribe(subscribe_data, user_email):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='For You']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
        click_interactable(subscribe_btn, driver)
        trigger = locator.find_element("class=trigger")
        click_interactable(trigger, driver)
        episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
        click_interactable(episode_element, driver)
        lock_btn= locator.find_element("class=lock")
        click_interactable(lock_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        paypal_payment_btn = locator.find_element("class=paypal-btn")
        click_interactable(paypal_payment_btn, driver)
        
        wait_and_capture(driver, 2)
        
        paypal_email_input = locator.find_element("id=email")
        paypal_email_input.clear()
        paypal_email_input.send_keys(user_email)
        paypal_btnNext = locator.find_element("id=btnNext")
        click_interactable(paypal_btnNext, driver)
        
        paypal_password_input = locator.find_element("id=password")
        paypal_password_input.clear()
        paypal_password_input.send_keys("Ye123456")
        paypal_btnLogin = locator.find_element("id=btnLogin")
        click_interactable(paypal_btnLogin, driver)
        paypal_consentButton = locator.find_element("id=consentButton")
        click_interactable(paypal_consentButton, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 10)
        
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# 老aw_more支付个人中心订阅流程
def profile_awoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    scroll_handler = ScrollHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='Profile']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
        click_interactable(subscribe_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        time.sleep(2)
        
        sidebar = locator.find_element("class=van-field__body")
        eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
        eamil_more_input.clear()
        eamil_more_input.send_keys(user_email)
        
        more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
        click_interactable(more_contirm_btn, driver)
        
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
        
        scroll_handler.scroll_to_bottom()
        pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 5)
        uuid_test = locator.find_element("class=userId")
        full_text = uuid_test.text
        print(f"完整文本: {full_text}")
        print("等待 3 秒后关闭...")
        wait_and_capture(driver, 3)
    finally:
        driver.quit()

# 老aw_more支付FOR YOU 订阅流程
def foryou_awoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    scroll_handler = ScrollHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='For You']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
        click_interactable(subscribe_btn, driver)
        trigger = locator.find_element("class=trigger")
        click_interactable(trigger, driver)
        episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
        click_interactable(episode_element, driver)
        lock_btn= locator.find_element("class=lock")
        click_interactable(lock_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        time.sleep(2)
        
        sidebar = locator.find_element("class=van-field__body")
        eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
        eamil_more_input.clear()
        eamil_more_input.send_keys(user_email)
        
        more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
        click_interactable(more_contirm_btn, driver)
        
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
        
        scroll_handler.scroll_to_bottom()
        pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 10)
        
        driver.refresh()
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# 老st_more支付个人中心订阅流程
def profile_stoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    scroll_handler = ScrollHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='Profile']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
        click_interactable(subscribe_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        time.sleep(2)
        
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
        
        scroll_handler.scroll_to_bottom()
        pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 10)
        
        driver.refresh()
        time.sleep(0.5)
        uuid_test = locator.find_element("class=userId")
        full_text = uuid_test.text
        print(f"完整文本: {full_text}")
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# 老st_more支付FOR YOU 订阅流程
def foryou_stoldmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    scroll_handler = ScrollHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='For You']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
        click_interactable(subscribe_btn, driver)
        trigger = locator.find_element("class=trigger")
        click_interactable(trigger, driver)
        episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
        click_interactable(episode_element, driver)
        lock_btn= locator.find_element("class=lock")
        click_interactable(lock_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        time.sleep(2)
        
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
        
        scroll_handler.scroll_to_bottom()
        pay_more_btn = locator.find_element("class=SubmitButton-CheckmarkIcon")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 10)
        
        driver.refresh()
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# 新aw_more支付个人中心订阅流程
def profile_awnewmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    iframe_handler = IFrameHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='Profile']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
        click_interactable(subscribe_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        time.sleep(2)
        
        sidebar = locator.find_element("class=van-field__body")
        eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
        eamil_more_input.clear()
        eamil_more_input.send_keys(user_email)
        more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
        click_interactable(more_contirm_btn, driver)
        
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
        
        pay_more_btn = locator.find_element("class=css-yen4e3")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 5)
        
        try:
            # 处理 3D 认证
            iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
            code_input = locator.find_element("id=challengeDataEntry")
            code_input.clear()
            code_input.send_keys("1234")
            submit_btn = locator.find_element("id=submit")
            click_interactable(submit_btn, driver)
            print("3D认证通过")
        except:
            print("无需3D认证")
        
        wait_and_capture(driver, 5)
        
        driver.refresh()
        time.sleep(0.5)
        uuid_test = locator.find_element("class=userId")
        full_text = uuid_test.text
        print(f"完整文本: {full_text}")
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# 新aw_more支付FOR YOU 订阅流程
def foryou_awnewmore_subscribe(subscribe_data, user_email, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    iframe_handler = IFrameHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='For You']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
        click_interactable(subscribe_btn, driver)
        trigger = locator.find_element("class=trigger")
        click_interactable(trigger, driver)
        episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
        click_interactable(episode_element, driver)
        lock_btn= locator.find_element("class=lock")
        click_interactable(lock_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        time.sleep(2)
        
        sidebar = locator.find_element("class=van-field__body")
        eamil_more_input = locator.find_element("class=van-field__control", context=sidebar)
        eamil_more_input.clear()
        eamil_more_input.send_keys(user_email)
        more_contirm_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Confirm']")
        click_interactable(more_contirm_btn, driver)
        
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
        
        pay_more_btn = locator.find_element("class=css-yen4e3")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 5)
        
        try:
            iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
            code_input = locator.find_element("id=challengeDataEntry")
            code_input.clear()
            code_input.send_keys("1234")
            submit_btn = locator.find_element("id=submit")
            click_interactable(submit_btn, driver)
            print("3D认证通过")
        except:
            print("无需3D认证")
        
        wait_and_capture(driver, 5)
        
        driver.refresh()
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# 新st_more支付个人中心订阅流程
def profile_stnewmore_subscribe(subscribe_data, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    iframe_handler = IFrameHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='Profile']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Subscribe Now']")
        click_interactable(subscribe_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        
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
        
        pay_more_btn = locator.find_element("class=css-yen4e3")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 5)
        
        try:
            iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
            code_input = locator.find_element("id=challengeDataEntry")
            code_input.clear()
            code_input.send_keys("1234")
            submit_btn = locator.find_element("id=submit")
            click_interactable(submit_btn, driver)
            print("3D认证通过")
        except:
            print("无需3D认证")
        
        wait_and_capture(driver, 5)
        
        driver.refresh()
        time.sleep(0.5)
        uuid_test = locator.find_element("class=userId")
        full_text = uuid_test.text
        print(f"完整文本: {full_text}")
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()

# 新st_more支付FOR YOU 订阅流程
def foryou_stnewmore_subscribe(subscribe_data, card_no, card_expire, card_cvv):
    driver = init_driver_with_logging()
    locator = SmartLocator(driver)
    iframe_handler = IFrameHandler(driver)
    driver.implicitly_wait(5)
    
    try:
        driver.get("https://{}".format(subscribe_data[0]))
        profile_btn = locator.find_element("xpath=//span[text()='For You']")
        click_interactable(profile_btn, driver)
        subscribe_btn = locator.find_element("xpath=//span[@class='van-button__text' and text()='Watch Now']")
        click_interactable(subscribe_btn, driver)
        trigger = locator.find_element("class=trigger")
        click_interactable(trigger, driver)
        episode_element = locator.find_element("xpath=//p[starts-with(text(), 'Episode')]")
        click_interactable(episode_element, driver)
        lock_btn= locator.find_element("class=lock")
        click_interactable(lock_btn, driver)
        subscribe_type_btn = locator.find_element("xpath=//div[@class='right-title' and text()={}]".format(repr(subscribe_data[1])))
        click_interactable(subscribe_type_btn, driver)
        
        subscribe_type_btn = locator.find_element("class=stripe-btn")
        click_interactable(subscribe_type_btn, driver)
        
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
        
        pay_more_btn = locator.find_element("class=css-yen4e3")
        click_interactable(pay_more_btn, driver)
        
        print("正在等待API响应并捕获数据...")
        wait_and_capture(driver, 5)
        
        try:
            iframe_handler.switch_to_iframe_by_path(["Airwallex 3DS wrapper iframe", "Airwallex 3DS iframe", "issuer-iframe"])
            code_input = locator.find_element("id=challengeDataEntry")
            code_input.clear()
            code_input.send_keys("1234")
            submit_btn = locator.find_element("id=submit")
            click_interactable(submit_btn, driver)
            print("3D认证通过")
        except:
            print("无需3D认证")
        
        wait_and_capture(driver, 5)
        
        driver.refresh()
        print("等待 10 秒后关闭...")
        wait_and_capture(driver, 10)
    finally:
        driver.quit()


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
            profile_paypal_subscribe(subscribe_data, user_email)
        case 4:
            foryou_paypal_subscribe(subscribe_data, user_email)
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
    subscribe_test_from_env()