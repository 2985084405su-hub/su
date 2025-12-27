from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)
import time
import re

from mysql_connection import MySQLConnection, load_config_from_file

class SmartLocator:
    def __init__(self, driver, timeout=10, poll_frequency=0.5):
        """
        初始化智能定位器
        
        Args:
            driver: WebDriver实例
            timeout: 超时时间（秒）
            poll_frequency: 轮询频率（秒）
        """
        self.driver = driver
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        self.wait = WebDriverWait(driver, timeout, poll_frequency)
    
    def find_element(self, locator_strategy, context=None, **kwargs):
        """
        智能查找单个元素
        
        Args:
            locator_strategy: 定位策略，支持多种格式
            context: 查找上下文（父元素），默认为driver
            **kwargs: 其他参数
        
        Returns:
            WebElement对象
        
        Raises:
            NoSuchElementException: 元素未找到
        """
        context = context or self.driver
        
        # 如果传入的是元组格式的定位器，直接使用
        if isinstance(locator_strategy, tuple):
            by, value = locator_strategy
            return self._find_with_retry(context, by, value, **kwargs)
        
        # 如果是字符串，智能解析
        elif isinstance(locator_strategy, str):
            return self._smart_find(context, locator_strategy, **kwargs)
        
        # 如果是字典，使用多策略查找
        elif isinstance(locator_strategy, dict):
            return self._multi_strategy_find(context, locator_strategy, **kwargs)
        
        else:
            raise ValueError(f"不支持的定位器类型: {type(locator_strategy)}")
    
    def find_elements(self, locator_strategy, context=None, **kwargs):
        """
        智能查找多个元素
        """
        context = context or self.driver
        
        if isinstance(locator_strategy, tuple):
            by, value = locator_strategy
            return context.find_elements(by, value)
        
        elif isinstance(locator_strategy, str):
            by, value = self._parse_locator_string(locator_strategy)
            return context.find_elements(by, value)
        
        elif isinstance(locator_strategy, dict):
            # 对于多策略，只使用第一个策略查找多个元素
            for strategy in locator_strategy.get('strategies', []):
                try:
                    by, value = self._parse_locator_string(strategy)
                    elements = context.find_elements(by, value)
                    if elements:
                        return elements
                except:
                    continue
            return []
        
        else:
            raise ValueError(f"不支持的定位器类型: {type(locator_strategy)}")
    
    def _smart_find(self, context, locator_string, **kwargs):
        """
        智能解析定位字符串并查找元素
        """
        # 解析定位器类型和值
        by, value = self._parse_locator_string(locator_string)
        
        # 应用动态参数
        if kwargs:
            value = value.format(**kwargs)
        
        return self._find_with_retry(context, by, value)
    
    def _parse_locator_string(self, locator_string):
        """
        解析定位器字符串，返回(By, value)元组
        """
        locator_string = locator_string.strip()
        
        # 预定义模式匹配
        patterns = [
            (r'^id=(.+)$', By.ID),
            (r'^css=(.+)$', By.CSS_SELECTOR),
            (r'^xpath=(.+)$', By.XPATH),
            (r'^name=(.+)$', By.NAME),
            (r'^class=(.+)$', By.CLASS_NAME),
            (r'^tag=(.+)$', By.TAG_NAME),
            (r'^link=(.+)$', By.LINK_TEXT),
            (r'^partial_link=(.+)$', By.PARTIAL_LINK_TEXT),
        ]
        
        for pattern, by_type in patterns:
            match = re.match(pattern, locator_string)
            if match:
                return by_type, match.group(1)
        
        # 自动识别：以//开头的是XPath
        if locator_string.startswith('//') or locator_string.startswith('./'):
            return By.XPATH, locator_string
        
        # 自动识别：以括号开头的是CSS选择器
        if (locator_string.startswith('.') or 
            locator_string.startswith('#') or
            '[' in locator_string or 
            ':' in locator_string):
            return By.CSS_SELECTOR, locator_string
        
        # 默认使用CSS选择器
        return By.CSS_SELECTOR, locator_string
    
    def _multi_strategy_find(self, context, strategy_config, **kwargs):
        """
        使用多种策略查找元素
        
        Args:
            strategy_config: 策略配置字典
        """
        strategies = strategy_config.get('strategies', [])
        retry_times = strategy_config.get('retry_times', 3)
        delay = strategy_config.get('delay', 0.5)
        
        for attempt in range(retry_times):
            for strategy in strategies:
                try:
                    by, value = self._parse_locator_string(strategy)
                    if kwargs:
                        value = value.format(**kwargs)
                    element = context.find_element(by, value)
                    print(f"使用策略 '{strategy}' 成功找到元素")
                    return element
                except NoSuchElementException:
                    continue
            
            if attempt < retry_times - 1:
                time.sleep(delay)
        
        raise NoSuchElementException(f"所有策略均未找到元素: {strategies}")
    
    def _find_with_retry(self, context, by, value, max_retries=3, delay=1):
        """
        带重试的查找方法
        """
        for attempt in range(max_retries):
            try:
                return context.find_element(by, value)
            except NoSuchElementException as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
                print(f"重试查找元素: {value} (尝试 {attempt + 1}/{max_retries})")
    
    def wait_for_element(self, locator_strategy, condition="visible", timeout=None, **kwargs):
        """
        等待元素满足特定条件
        
        Args:
            locator_strategy: 定位策略
            condition: 等待条件
                - visible: 元素可见
                - clickable: 元素可点击
                - present: 元素存在
                - invisible: 元素不可见
                - selected: 元素被选中
            timeout: 超时时间，默认为初始化时的timeout
        """
        conditions = {
            "visible": EC.visibility_of_element_located,
            "clickable": EC.element_to_be_clickable,
            "present": EC.presence_of_element_located,
            "invisible": EC.invisibility_of_element_located,
            "selected": EC.element_to_be_selected,
        }
        
        if condition not in conditions:
            raise ValueError(f"不支持的等待条件: {condition}")
        
        # 使用指定的超时时间或默认值
        wait_timeout = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_timeout, self.poll_frequency)
        
        # 解析定位器
        if isinstance(locator_strategy, tuple):
            locator = locator_strategy
        else:
            by, value = self._parse_locator_string(locator_strategy)
            if kwargs:
                value = value.format(**kwargs)
            locator = (by, value)
        
        try:
            return wait.until(conditions[condition](locator))
        except TimeoutException:
            raise TimeoutException(f"元素未满足条件 '{condition}': {locator}")

class ScrollHandler:
    """页面滚动处理器"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def scroll_to_element(self, element):
        """滚动到指定元素"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
    
    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(0.5)
    
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        time.sleep(0.5)
    
    def scroll_by_pixels(self, x_pixels=0, y_pixels=100):
        """按像素滚动"""
        self.driver.execute_script(f"window.scrollBy({x_pixels}, {y_pixels});")
        time.sleep(0.3)
    
    def scroll_until_element_found(self, locator, max_scrolls=10):
        """滚动直到找到元素"""
        from selenium.webdriver.common.by import By
        
        for i in range(max_scrolls):
            try:
                if isinstance(locator, tuple):
                    element = self.driver.find_element(*locator)
                else:
                    # 如果是字符串，尝试解析
                    if locator.startswith('//'):
                        element = self.driver.find_element(By.XPATH, locator)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, locator)
                        
                if element.is_displayed():
                    return element
            except:
                pass
            
            # 向下滚动
            self.scroll_by_pixels(y_pixels=500)
            time.sleep(1)
        
        raise NoSuchElementException(f"滚动{max_scrolls}次后未找到元素")

class IFrameHandler:
    def __init__(self, driver):
        self.driver = driver
    
    def switch_to_iframe_by_path(self, iframe_path):
        """切换到指定路径的iframe"""
        # 先切回主文档
        self.driver.switch_to.default_content()
        
        for locator in iframe_path:
            try:
                if isinstance(locator, str):
                    # 尝试通过name、id或CSS选择器查找
                    try:
                        # 先尝试name或id
                        self.driver.switch_to.frame(locator)
                    except:
                        # 尝试CSS选择器
                        iframe = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[name="{locator}"], iframe[id="{locator}"]'))
                        )
                        self.driver.switch_to.frame(iframe)
                elif isinstance(locator, int):
                    # 通过索引切换
                    self.driver.switch_to.frame(locator)
                else:
                    # 已经是WebElement
                    self.driver.switch_to.frame(locator)
                    
                print(f"成功切换到: {locator}")
                
            except Exception as e:
                print(f"切换iframe失败: {locator}, 错误: {str(e)}")
                raise


# 主域名，订阅类型，支付方式数据查询
def select_subscribe_title(site_name='VIVI',subscribe_type=2):
    config = load_config_from_file('config_example.json')
    if not config:
        print("无法加载配置文件")
        return
    
    db = MySQLConnection(**config)
    if db.connect():
        try:
            # 使用参数化查询
            subscribe_title_sql = "SELECT title from v_subscribe_plan_lang where site_id = (SELECT id FROM v_site where site_name = %s) and lang_code = 'en' and plan_id = %s;"
            main_site_sql = "SELECT name from v_domain where site_id = (SELECT id FROM v_site where site_name = %s) and is_main = 1;"
            subscribe_title = db.execute_query(subscribe_title_sql, (site_name,subscribe_type,))
            main_site = db.execute_query(main_site_sql, (site_name,))  # 传入参数元组
            # column_names = db.get_column_names()
            # print("查询结果列名:", column_names)
            # print(main_site,subscribe_title)
        finally:
            db.close()
    return main_site[0][0], subscribe_title[0][0]






def click_interactable(element, driver, max_retries=3):
    """
    安全地点击元素，处理各种异常情况
    
    Args:
        element: 要点击的WebElement
        driver: WebDriver实例
        max_retries: 最大重试次数
    """
    for attempt in range(max_retries):
        try:
            # 确保元素在可视区域
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            
            # 等待元素可点击
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(element)
            )
            
            # 点击元素
            element.click()
            print(f"✓ 成功点击元素")
            return True
            
        except ElementClickInterceptedException:
            print(f"元素被遮挡，尝试 {attempt + 1}/{max_retries}")
            # 尝试点击不同的位置
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except:
                pass
                
        except StaleElementReferenceException:
            print(f"元素过时，尝试 {attempt + 1}/{max_retries}")
            # 需要重新查找元素
            return False
            
        except Exception as e:
            print(f"点击失败，尝试 {attempt + 1}/{max_retries}: {e}")
        
        time.sleep(1)
    
    print(f"✗ 点击失败，已尝试{max_retries}次")
    return False