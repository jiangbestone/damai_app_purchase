# -*- coding: UTF-8 -*-


import time
from datetime import datetime, timedelta
from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import Config


delay_time = 0.05

class DamaiBot:
    def __init__(self):
        self.config = Config.load_config()
        self.driver = None
        self.wait = None
        self._setup_driver()

    def _setup_driver(self):
        """初始化驱动配置"""
        device_app_info = None
        try:
            print("开始初始化驱动配置...")
            capabilities = {
                "platformName": "Android",  # 操作系统
                "platformVersion": "15",  # 系统版本
                "deviceName": "OPPO Find X8 Pro",  # 设备名称
                "appPackage": "cn.damai",  # app 包名
                "appActivity": ".launcher.splash.SplashMainActivity",  # app 启动 Activity
                "unicodeKeyboard": True,  # 支持 Unicode 输入
                "resetKeyboard": True,  # 隐藏键盘
                "noReset": True,  # 不重置 app
                "newCommandTimeout": 6000,  # 超时时间
                "automationName": "UiAutomator2",  # 使用 uiautomator2
                "skipServerInstallation": False,  # 跳过服务器安装
                "ignoreHiddenApiPolicyError": True,  # 忽略隐藏 API 策略错误
                "disableWindowAnimation": True,  # 禁用窗口动画
                # 优化性能配置
                "mjpegServerFramerate": 1,  # 降低截图帧率
                "shouldTerminateApp": False,
                "adbExecTimeout": 20000,
                "connectionTimeout": 30000,  # 增加连接超时时间
                "commandTimeout": 30000,  # 增加命令超时时间
            }

            print("设置AppiumOptions...")
            device_app_info = AppiumOptions()
            print("AppiumOptions设置完成")
            
            # 直接设置capabilities而不是使用load_capabilities
            for key, value in capabilities.items():
                device_app_info.set_capability(key, value)
                
            print(f"尝试连接Appium服务器: {self.config.server_url}")
            # 适配Appium 3.0版本
            server_url = "http://127.0.0.1:4723"
            print(f"使用服务器URL: {server_url}")
            
            # 添加必要的capabilities
            device_app_info.set_capability("appium:automationName", "UiAutomator2")
            
            self.driver = webdriver.Remote(server_url, options=device_app_info)
            print("成功连接到Appium服务器")
            
            # 更激进的性能优化设置
            self.driver.update_settings({
                "waitForIdleTimeout": 0,  # 空闲时间，0 表示不等待，让 UIAutomator2 不等页面"空闲"再返回
                "actionAcknowledgmentTimeout": 0,  # 禁止等待动作确认
                "keyInjectionDelay": 0,  # 禁止输入延迟
                "waitForSelectorTimeout": 0.01,  # 从500减少到300ms
                "ignoreUnimportantViews": False,  # 保持false避免元素丢失
                "allowInvisibleElements": True,
                "enableNotificationListener": False,  # 禁用通知监听
            })

            # 极短的显式等待，抢票场景下速度优先
            self.wait = WebDriverWait(self.driver, 0.05)  # 从5秒减少到2秒
        except Exception as e:
            print(f"初始化驱动配置或连接Appium服务器时出错: {e}")
            print("请确保Appium服务器已启动，并且设备已连接")
            raise

    def ultra_fast_click(self, by, value, timeout=1.5):
        """超快速点击 - 适合抢票场景"""
        try:
            # 直接查找并点击，不等待可点击状态
            el = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            # 直接使用元素ID点击
            self.driver.execute_script('mobile: clickGesture', {'elementId': el.id})
            return True
        except TimeoutException:
            return False
            
    def smart_wait_and_click(self, *selectors, timeout=2, retry_count=3):
        """智能等待并点击元素，支持多种选择器尝试
        
        参数:
            *selectors: 选择器列表，每个选择器格式为(by, value)
            timeout: 等待超时时间
            retry_count: 重试次数
        """
        print(f"调试: smart_wait_and_click 被调用，选择器数量: {len(selectors)}")
        
        # 处理选择器参数
        all_selectors = []
        for selector in selectors:
            # 如果是元组且长度为2，直接添加
            if isinstance(selector, tuple) and len(selector) == 2:
                all_selectors.append(selector)
            # 如果是列表，尝试将其中的元组添加进来
            elif isinstance(selector, list):
                for item in selector:
                    if isinstance(item, tuple) and len(item) == 2:
                        all_selectors.append(item)
            # 其他情况，尝试构建AppiumBy选择器
            elif isinstance(selector, str):
                # 尝试处理常见的选择器字符串格式
                if selector.startswith('new UiSelector()'):
                    all_selectors.append((AppiumBy.ANDROID_UIAUTOMATOR, selector))
                elif selector.startswith('//'):
                    all_selectors.append((AppiumBy.XPATH, selector))
                elif selector.startswith('#'):
                    all_selectors.append((AppiumBy.ID, selector[1:]))
        
        print(f"处理后的选择器列表: {all_selectors}")
        
        # 如果没有有效选择器，直接返回失败
        if not all_selectors:
            print("没有有效的选择器，无法执行点击操作")
            return False
            
        # 保存页面源码以便调试
        try:
            page_source = self.driver.page_source
            print(f"页面源码片段: {page_source[:200]}...")
        except Exception as e:
            print(f"获取页面源码失败: {e}")
            
        for attempt in range(retry_count):
            print(f"尝试点击，第 {attempt+1}/{retry_count} 次")
            for selector in all_selectors:
                try:
                    by, value = selector
                    print(f"尝试使用选择器: ({by}, {value})")
                    
                    # 先尝试查找元素是否存在
                    try:
                        el = WebDriverWait(self.driver, timeout/2).until(
                            EC.presence_of_element_located((by, value))
                        )
                        print(f"找到元素: {el.tag_name}, ID: {el.id}")
                    except Exception as find_err:
                        print(f"元素未找到: {find_err}")
                        continue
                        
                    if self.ultra_fast_click(by, value, timeout):
                        print(f"成功点击元素: ({by}, {value})")
                        return True
                    else:
                        print(f"点击失败: ({by}, {value})")
                except Exception as e:
                    print(f"点击过程中出错: {e}")
                    continue
            print(f"所有选择器尝试失败，等待0.5秒后重试")
            time.sleep(delay_time)
        print(f"所有尝试均失败")
        return False

    def batch_click(self, elements_info, delay=0.1):
        """批量点击操作"""
        for by, value in elements_info:
            if self.ultra_fast_click(by, value):
                if delay > 0:
                    time.sleep(delay_time)
            else:
                print(f"点击失败: {value}")

    def ultra_batch_click(self, elements_info, timeout=2):
        """超快批量点击 - 带等待机制"""
        coordinates = []
        # 批量收集坐标，带超时等待
        for by, value in elements_info:
            try:
                # 等待元素出现
                el = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                rect = el.rect
                x = rect['x'] + rect['width'] // 2
                y = rect['y'] + rect['height'] // 2
                coordinates.append((x, y, value))
            except TimeoutException:
                print(f"超时未找到用户: {value}")
            except Exception as e:
                print(f"查找用户失败 {value}: {e}")
        print(f"成功找到 {len(coordinates)} 个用户")
        # 快速连续点击
        for i, (x, y, value) in enumerate(coordinates):
            self.driver.execute_script("mobile: clickGesture", {
                "x": x,
                "y": y,
                "duration": 30
            })
            if i < len(coordinates) - 1:
                time.sleep(delay_time)
            print(f"点击用户: {value}")

    def select_first_search_result(self):
        """选择搜索结果中的第一个项目"""
        try:
            print("\n===== 尝试选择第一个搜索结果 =====")
            # 等待页面加载
            time.sleep(delay_time)  # 增加等待时间，确保搜索结果完全加载
            
            # 检查当前Activity
            try:
                current_activity = self.driver.current_activity
                print(f"当前Activity: {current_activity}")
            except Exception as e:
                print(f"获取当前Activity失败: {e}")
            
            # 保存页面源码以便调试
            try:
                page_source = self.driver.page_source
                print(f"搜索结果页面源码片段: {page_source[:300]}...")
                
                # 保存页面源码到文件
                try:
                    with open("search_results_page.xml", "w", encoding="utf-8") as f:
                        f.write(page_source)
                    print("已保存搜索结果页面源码到search_results_page.xml")
                except Exception as e:
                    print(f"保存页面源码到文件失败: {e}")
            except Exception as e:
                print(f"获取页面源码失败: {e}")
            
            
            # 扩展搜索结果选择器
            # 搜索结果选择器 - 优先使用演员名称
            keyword = self.config.keyword  # 默认使用配置中的关键词（如"刘若英"）
            
            # 确保使用演员名称进行搜索
            result_selectors = [
                # 演员名称特定选择器（最高优先级）
                (AppiumBy.XPATH, f'//android.widget.TextView[contains(@text, "{keyword}")]/parent::*'),
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{keyword}")'),
                
                # 第一个搜索结果选择器（通用）
                (AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="cn.damai:id/ll_search_item"][1]'),
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="cn.damai:id/item_title"][1]'),
                (AppiumBy.XPATH, '//android.widget.ListView/android.widget.LinearLayout[1]'),
                (AppiumBy.XPATH, '//android.widget.RecyclerView/android.widget.LinearLayout[1]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ListView").childSelector(new UiSelector().index(0))'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.RecyclerView").childSelector(new UiSelector().index(0))')
            ]
            
            print(f"尝试点击包含'{keyword}'的第一个搜索结果...")
            success = False
            
            # 使用选择器精确定位并模拟点击
            for by, value in result_selectors:
                if success:
                    break
                    
                try:
                    print(f"尝试使用选择器: ({by}, {value})")
                    # 增加等待时间，确保元素完全加载
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, value))
                    )
                    print(f"找到元素: {element.tag_name}, 尝试点击...")
                    
                    # 获取元素位置和大小，用于模拟点击
                    location = element.location
                    size = element.size
                    center_x = location['x'] + size['width'] // 2
                    center_y = location['y'] + size['height'] // 2
                    
                    print(f"元素中心点坐标: ({center_x}, {center_y})")
                    
                    # 尝试多种点击方式
                    try:
                        # 方式1: 使用driver.tap方法模拟点击
                        self.driver.tap([(center_x, center_y)])
                        print(f"已使用tap方法模拟点击坐标 ({center_x}, {center_y})")
                        success = True
                    except Exception as touch_err:
                        print(f"tap方法点击失败: {touch_err}，尝试其他方式")
                        
                        try:
                            # 方式2: 直接点击元素
                            element.click()
                            print("已使用element.click()点击搜索结果")
                            success = True
                        except Exception as click_err:
                            print(f"直接点击失败: {click_err}，尝试使用JS点击")
                            
                            # 方式3: 使用JS点击
                            try:
                                self.driver.execute_script('mobile: clickGesture', {'elementId': element.id})
                                print("已使用JS点击搜索结果")
                                success = True
                            except Exception as js_err:
                                print(f"JS点击也失败: {js_err}，尝试使用坐标点击")
                                # 方式4: 使用坐标点击
                                try:
                                    rect = element.rect
                                    x = rect['x'] + rect['width'] // 2
                                    y = rect['y'] + rect['height'] // 2
                                    self.driver.tap([(x, y)], 500)  # 增加点击时间
                                    print(f"已使用坐标({x}, {y})点击第一个搜索结果")
                                    success = True
                                except Exception as tap_err:
                                    print(f"坐标点击也失败: {tap_err}")
                    
                    # 等待页面跳转
                    time.sleep(delay_time)  # 增加等待时间
                    
                    # 验证是否成功进入演出详情页
                    if self.verify_detail_page():
                        return True
                        
                except Exception as e:
                    print(f"尝试点击 {by}={value} 失败: {e}")
                    continue
            
            # 方法2: 如果所有选择器都失败，尝试点击搜索结果区域
            if not success:
                print("尝试点击搜索结果区域...")
                try:
                    # 尝试获取屏幕尺寸
                    screen_size = self.driver.get_window_size()
                    width = screen_size['width']
                    height = screen_size['height']
                    print(f"屏幕尺寸: {width}x{height}")
                    
                    # 定义可能的搜索结果位置
                    click_positions = [
                        (width // 2, int(height * 0.25)),  # 屏幕上部
                        (width // 2, int(height * 0.3)),   # 稍微往下一点
                        (width // 2, int(height * 0.35)),  # 再往下一点
                        (width // 2, int(height * 0.4))    # 更往下一点
                    ]
                    
                    for i, (x, y) in enumerate(click_positions):
                        if success:
                            break
                            
                        try:
                            # 使用长按确保点击成功
                            self.driver.tap([(x, y)], 500)  # 增加点击时间
                            print(f"尝试点击位置 {i+1}: ({x}, {y})")
                            time.sleep(delay_time)
                            
                            # 验证是否成功进入演出详情页
                            if self.verify_detail_page():
                                success = True
                                return True
                        except Exception as e:
                            print(f"点击位置 {i+1} 失败: {e}")
                except Exception as e:
                    print(f"使用坐标点击失败: {e}")
            
            print("无法找到搜索结果")
            return False
        except Exception as e:
            print(f"选择第一个搜索结果时出错: {e}")
            return False
            
    def verify_detail_page(self):
        """验证是否已进入详情页面"""
        try:
            # 检查Activity变化
            try:
                current_activity = self.driver.current_activity
                print(f"当前Activity: {current_activity}")
                if ".detail." in current_activity or "DetailActivity" in current_activity:
                    print("已成功进入演出详情页 (Activity包含detail)")
                    return True
            except Exception as e:
                print(f"获取当前Activity失败: {e}")
            
            # 检查页面元素
            detail_indicators = [
                (AppiumBy.ID, "cn.damai:id/detail_title"),
                (AppiumBy.ID, "cn.damai:id/detail_subtitle"),
                (AppiumBy.ID, "cn.damai:id/detail_time"),
                (AppiumBy.ID, "cn.damai:id/detail_address"),
                (AppiumBy.XPATH, "//android.widget.Button[contains(@text, '立即购买') or contains(@text, '确定')]"),
                (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '场次') or contains(@text, '票档')]")
            ]
            
            for by, value in detail_indicators:
                try:
                    element = self.driver.find_element(by, value)
                    if element:
                        print(f"找到详情页指示元素: {by}={value}")
                        return True
                except Exception:
                    continue
            
                
            return False
        except Exception as e:
            print(f"验证详情页时出错: {e}")
            return False
        except Exception as e:
            print(f"选择搜索结果时出错: {e}")
            return False

    def run_ticket_grabbing(self):
        """执行抢票主流程"""
        try:
            print("开始抢票流程...")
            start_time = time.time()

            # 检查APP是否已启动
            try:
                print("检查APP是否已启动...")
                current_activity = self.driver.current_activity
                current_package = self.driver.current_package
                print(f"当前活动: {current_activity}, 当前包: {current_package}")
                
                # 如果APP未启动，尝试启动它
                if current_package != "cn.damai":
                    print("大麦APP未启动，尝试启动...")
                    self.driver.activate_app("cn.damai")
                    time.sleep(delay_time)  # 等待APP启动
                    print("APP启动完成")
            except Exception as e:
                print(f"检查APP状态时出错: {e}")
            
            
            # 先点击精选菜单栏
            try:
                print("尝试点击精选菜单栏...")
                featured_tab_selectors = [
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("精选")'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("精选")'),
                    (By.XPATH, '//android.widget.TextView[@text="精选"]'),
                    (By.XPATH, '//*[contains(@text, "精选")]')
                ]
                
                if self.smart_wait_and_click(*featured_tab_selectors[0], featured_tab_selectors[1:]):
                    print("成功点击精选菜单栏")
                else:
                    print("未找到精选菜单栏，尝试点击底部导航栏...")
                    # 尝试点击底部导航栏的任意按钮
                    nav_btn_selectors = [
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("首页")'),
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("我的")'),
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("发现")'),
                        (By.XPATH, '//android.widget.TextView[@text="首页"]'),
                        (By.XPATH, '//android.widget.TextView[@text="我的"]'),
                        (By.XPATH, '//android.widget.TextView[@text="发现"]')
                    ]
                    if self.smart_wait_and_click(*nav_btn_selectors[0], nav_btn_selectors[1:]):
                        print("成功点击导航按钮")
                        # 再次尝试点击精选菜单栏
                        if self.smart_wait_and_click(*featured_tab_selectors[0], featured_tab_selectors[1:]):
                            print("成功点击精选菜单栏")
                        else:
                            print("无法找到精选菜单栏")
                    else:
                        print("无法找到导航按钮")
            except Exception as e:
                print(f"点击精选菜单栏时出错: {e}")
            
            # 尝试搜索关键词
            try:
                print("尝试搜索关键词...")
                
                # 简化后的搜索框选择器，优先使用textContains("搜索")
                search_box_selectors = [
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("搜索")'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("cn.damai:id/search_bar")'),
                    (By.XPATH, '//*[contains(@text, "搜索")]')
                ]
                
                # 尝试点击搜索框
                print("尝试点击搜索框...")
                if self.smart_wait_and_click(*search_box_selectors):
                    print("成功点击搜索框")
                    
                    # 检查是否已进入搜索页面
                    try:
                        current_activity = self.driver.current_activity
                        print(f"当前Activity: {current_activity}")
                    except Exception as e:
                        print(f"获取当前Activity失败: {e}")
                    
                    # 简化后的搜索输入框查找和输入逻辑
                    try:
                        # 优先使用EditText类查找输入框
                        search_input = self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.EditText")
                        print("找到搜索输入框: class name=android.widget.EditText")
                        
                        # 清除并输入关键词
                        search_input.clear()
                        search_input.send_keys(self.config.keyword)
                        print(f"已输入搜索关键词: {self.config.keyword}")
                    except Exception as e:
                        print(f"输入搜索关键词时出错: {e}")
                        
                        # 点击搜索按钮或回车
                        print("尝试点击搜索按钮或使用回车键...")
                        
                        # 简化的搜索按钮选择器
                        search_btn_selectors = [
                            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("搜索")'),
                            (By.XPATH, '//android.widget.TextView[@text="搜索"]')
                        ]
                        
                        # 尝试点击搜索按钮
                        if self.smart_wait_and_click(*search_btn_selectors):
                            print("成功点击搜索按钮")
                        else:
                            # 使用回车键搜索
                            try:
                                from selenium.webdriver.common.keys import Keys
                                from selenium.webdriver import ActionChains
                                actions = ActionChains(self.driver)
                                actions.send_keys(Keys.ENTER).perform()
                                print("已使用回车键搜索")
                            except Exception as e:
                                print(f"使用回车键失败: {e}")
                        
                        # 等待搜索结果加载
                        print("等待搜索结果加载...")

                        # 检查当前Activity
                        try:
                            current_activity = self.driver.current_activity
                            print(f"搜索后当前Activity: {current_activity}")
                        except Exception as e:
                            print(f"获取搜索后当前Activity失败: {e}")
                    except Exception as e:
                        print(f"输入搜索关键词失败: {e}")
                else:
                    print("未找到搜索框，尝试点击首页按钮...")
                    # 尝试点击底部导航栏的任意按钮
                    nav_btn_selectors = [
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("首页")'),
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("我的")'),
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("发现")'),
                        (By.XPATH, '//android.widget.TextView[@text="首页"]'),
                        (By.XPATH, '//android.widget.TextView[@text="我的"]'),
                        (By.XPATH, '//android.widget.TextView[@text="发现"]')
                    ]
                    if self.smart_wait_and_click(*nav_btn_selectors[0], nav_btn_selectors[1:]):
                        print("成功点击导航按钮")
                        # 再次尝试点击搜索框
                        if self.smart_wait_and_click(*search_box_selectors[0], search_box_selectors[1:]):
                            print("成功点击搜索框")
                            # 输入搜索关键词
                            try:
                                search_input = self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.EditText")
                                search_input.send_keys(self.config.keyword)
                
                                # 点击搜索按钮
                                search_btn_selectors = [
                                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("搜索")'),
                                    (By.XPATH, '//android.widget.TextView[@text="搜索"]')
                                ]
                                if self.smart_wait_and_click(*search_btn_selectors[0], search_btn_selectors[1:]):
                                    print("成功点击搜索按钮")
                                    # 选择第一个搜索结果
                                    self.select_first_search_result()
                                else:
                                    # 尝试按回车键
                                    search_input.send_keys("\n")
                                    print("已按回车键搜索")
                                    # 选择第一个搜索结果
                                    self.select_first_search_result()
                            except Exception as e:
                                print(f"输入搜索关键词失败: {e}")
                        else:
                            print("无法找到搜索框")
                    else:
                        print("无法找到导航按钮")
            except Exception as e:
                print(f"导航到搜索界面时出错: {e}")
                
            # 城市选择功能已移除，只保留演员搜索
            print("已跳过城市选择，只进行演员搜索...")
            
            # 确保点击搜索结果进入详情页
            print("尝试点击搜索结果进入详情页...")
            keyword = self.config.keyword
            
            # 搜索结果选择器 - 优先使用演员名称
            result_selectors = [
                # 演员名称特定选择器（最高优先级）
                (AppiumBy.XPATH, f'//android.widget.TextView[contains(@text, "{keyword}")]/parent::*'),
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{keyword}")'),
                
                # 第一个搜索结果选择器（通用）
                (AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="cn.damai:id/ll_search_item"][1]'),
                (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="cn.damai:id/item_title"][1]'),
                (AppiumBy.XPATH, '//android.widget.ListView/android.widget.LinearLayout[1]'),
                (AppiumBy.XPATH, '//android.widget.RecyclerView/android.widget.LinearLayout[1]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ListView").childSelector(new UiSelector().index(0))'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.RecyclerView").childSelector(new UiSelector().index(0))')
            ]
            
            print(f"尝试点击包含'{keyword}'的第一个搜索结果...")
            success = False
            
            # 使用选择器精确定位并模拟点击
            for by, value in result_selectors:
                if success:
                    break
                    
                try:
                    print(f"尝试使用选择器: ({by}, {value})")
                    # 增加等待时间，确保元素完全加载
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, value))
                    )
                    print(f"找到元素: {element.tag_name}, ID: {element.id}")
                    
                    # 获取元素位置和大小，用于模拟点击
                    rect = element.rect
                    center_x = rect['x'] + rect['width'] // 2
                    center_y = rect['y'] + rect['height'] // 2
                    
                    print(f"元素中心点坐标: ({center_x}, {center_y})")
                    
                    # 尝试多种点击方式
                    try:
                        # 方式1: 使用driver.tap方法模拟点击
                        self.driver.tap([(center_x, center_y)], 500)
                        print(f"已使用tap方法模拟点击坐标 ({center_x}, {center_y})")
                        success = True
                    except Exception as touch_err:
                        print(f"tap方法点击失败: {touch_err}，尝试其他方式")
                        
                        try:
                            # 方式2: 直接点击元素
                            element.click()
                            print("已使用element.click()点击搜索结果")
                            success = True
                        except Exception as click_err:
                            print(f"直接点击失败: {click_err}，尝试使用JS点击")
                            
                            # 方式3: 使用JS点击
                            try:
                                self.driver.execute_script('mobile: clickGesture', {'elementId': element.id})
                                print("已使用JS点击搜索结果")
                                success = True
                            except Exception as js_err:
                                print(f"JS点击也失败: {js_err}，尝试使用坐标点击")
                                # 方式4: 使用坐标点击
                                try:
                                    x = rect['x'] + rect['width'] // 2
                                    y = rect['y'] + rect['height'] // 2
                                    self.driver.tap([(x, y)], 500)  # 增加点击时间
                                    print(f"已使用坐标({x}, {y})点击第一个搜索结果")
                                    success = True
                                except Exception as tap_err:
                                    print(f"坐标点击也失败: {tap_err}")
                    
                    
                    if success:
                        print("成功点击搜索结果，等待页面加载...")
                        break
                        
                except Exception as e:
                    print(f"使用选择器 ({by}, {value}) 查找元素失败: {e}")
                    continue
            
            if not success:
                print("所有选择器都无法找到搜索结果元素，请检查页面状态或选择器")
                return False
            
            # 进入详情页后选择城市
            print("已进入详情页，尝试选择城市...")
            print(f"要选择的城市: {self.config.city}")
                      
            # 针对截图中的城市列表界面，直接尝试选择城市
            city_selected = False
            
            # 1. 首先尝试直接点击城市名称
            city_direct_selectors = [
                # 精确匹配城市名
                (AppiumBy.XPATH, f'//android.widget.TextView[@text="{self.config.city}"]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{self.config.city}")'),
                
                # 包含城市名
                (AppiumBy.XPATH, f'//android.widget.TextView[contains(@text, "{self.config.city}")]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{self.config.city}")'),
                
                # 城市名所在的父元素
                (AppiumBy.XPATH, f'//*[contains(@text, "{self.config.city}")]/parent::*'),
                (AppiumBy.XPATH, f'//*[contains(@text, "{self.config.city}")]/..'),
                
                # 城市卡片选择器
                (AppiumBy.XPATH, f'//android.view.View[contains(@content-desc, "{self.config.city}")]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().descriptionContains("{self.config.city}")'),
                
                # 针对城市列表页面的特殊选择器
                (AppiumBy.XPATH, f'//android.widget.FrameLayout[.//android.widget.TextView[contains(@text, "{self.config.city}")]]'),
                (AppiumBy.XPATH, f'//android.view.ViewGroup[.//android.widget.TextView[contains(@text, "{self.config.city}")]]'),
                
                # 针对热卖中标签的选择器
                (AppiumBy.XPATH, f'//android.widget.TextView[contains(@text, "{self.config.city}")]/following-sibling::android.widget.TextView[contains(@text, "热卖中")]/../..'),
                (AppiumBy.XPATH, f'//android.widget.TextView[contains(@text, "{self.config.city}")]/parent::*/parent::*'),
                
                # 针对截图中的布局添加更精确的选择器
                (AppiumBy.XPATH, f'//android.widget.TextView[@text="{self.config.city}"]/parent::android.view.ViewGroup'),
                (AppiumBy.XPATH, f'//android.widget.TextView[@text="{self.config.city}"]/following-sibling::android.widget.TextView'),
                (AppiumBy.XPATH, f'//android.widget.TextView[@text="{self.config.city}"]/../..'),
                
                # 针对日期和热卖中标签的组合选择器
                (AppiumBy.XPATH, f'//android.widget.TextView[@text="{self.config.city}"]/following-sibling::*[1]')
            ]
            
            print(f"尝试直接选择城市: {self.config.city}")
            if self.smart_wait_and_click(*city_direct_selectors[0], city_direct_selectors[1:]):
                print(f"成功直接选择城市: {self.config.city}")
                city_selected = True
            
                
            if city_selected:
                print(f"已完成城市选择: {self.config.city}")
            else:
                print("城市选择可能失败，继续执行后续流程")

            wait_until(self.config.time)#时间需要在抢票开始前1分钟进行
            # 点击立即预订按钮
            print("尝试点击立即预订按钮...")

            
            # 获取屏幕尺寸
            screen_size = self.driver.get_window_size()
            screen_width = screen_size['width']
            screen_height = screen_size['height']
            print(f"屏幕尺寸: {screen_width}x{screen_height}")
            
            # 定义多个可能的点击位置
            click_positions = [
                # 右下角位置 - 优先尝试
                (int(screen_width * 0.9), int(screen_height * 0.95)),  # 最右下角
                (int(screen_width * 0.85), int(screen_height * 0.95)), # 右下角稍左
                (int(screen_width * 0.9), int(screen_height * 0.9)),   # 右下角稍上
                (int(screen_width * 0.8), int(screen_height * 0.95)),  # 更左一点
                
                # 屏幕底部区域 - 备选尝试
                (int(screen_width * 0.7), int(screen_height * 0.95)),
                (int(screen_width * 0.6), int(screen_height * 0.95)),
                
                # 屏幕底部中间位置 - 最后尝试
                (int(screen_width * 0.5), int(screen_height * 0.95)),
                (int(screen_width * 0.5), int(screen_height * 0.9))
            ]
            
            # 尝试多个位置点击
            click_success = False
            for i, (x, y) in enumerate(click_positions):
                try:
                    print(f"尝试点击位置 {i+1}/{len(click_positions)}: ({x}, {y})")
                    
                    # 使用tap方法模拟点击，增加点击持续时间
                    self.driver.tap([(x, y)], 100)  # 增加到1000ms
                    print(f"已模拟点击坐标: ({x}, {y})")
                    
                    
                    # 检查是否点击成功 - 可以通过页面变化来判断
                    # 这里简单等待，实际应该检查页面元素变化
                    click_success = True
                    print(f"位置 {i+1} 点击可能成功，继续流程")
                    break
                    
                except Exception as e:
                    print(f"位置 {i+1} 点击失败: {e}")
                    continue
            
            
            if click_success:
                print("立即预订按钮点击操作完成")
                print("开始选择日期...")
                target_date = self.config.date
                print(f"目标日期: {target_date}")
                
                # 检查是否已经在票档选择页面（跳过了日期选择）
                try:
                    ticket_elements = self.driver.find_elements(AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "票档")]')
                    if ticket_elements and len(ticket_elements) > 0:
                        print("已经在票档选择页面，无需选择日期")
                        return True
                except Exception:
                    pass  # 忽略检查错误，继续尝试选择日期
                

                
                # 尝试找到日期选择器 - 扩展选择器列表
                date_selectors = [
                    # 匹配截图中的日期格式 "YYYY-MM-DD 周X HH:MM"
                    (AppiumBy.XPATH, f'//android.widget.TextView[starts-with(@text, "{target_date}")]'),
                    
                    # 匹配日期部分（不含时间和星期）
                    (AppiumBy.XPATH, f'//android.widget.TextView[contains(@text, "{target_date}")]'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{target_date}")'),
                    
                    # 匹配月日部分（例如"11-01"或"11-02"）
                    (AppiumBy.XPATH, f'//android.widget.TextView[contains(@text, "{"-".join(target_date.split("-")[1:]) if "-" in target_date and len(target_date.split("-")) > 2 else target_date}")]'),
                    
                    # 匹配场次选择界面中的日期元素
                    (AppiumBy.XPATH, '//android.view.ViewGroup//android.widget.TextView[contains(@text, "周") and contains(@text, ":")]'),
                    
                    # 匹配常见日期元素
                    (AppiumBy.XPATH, '//android.widget.TextView[contains(@resource-id, "dateItemText")]'),
                    (AppiumBy.XPATH, '//android.widget.TextView[contains(@resource-id, "date")]'),
                    
                    # 匹配可选择的日期（通常是亮色显示的）
                    (AppiumBy.XPATH, '//android.widget.TextView[@enabled="true" and contains(@resource-id, "date")]'),
                    
                    # 匹配日历视图中的日期
                    (AppiumBy.XPATH, '//android.view.ViewGroup[contains(@resource-id, "calendar")]/android.widget.TextView')
                ]
                
                date_found = False
                # 如果找不到日期，尝试点击屏幕中间位置
                if not date_found:
                    print("未找到日期元素，尝试点击屏幕中间位置...")
                    try:
                        screen_size = self.driver.get_window_size()
                        screen_width = screen_size['width']
                        screen_height = screen_size['height']
                        
                        # 点击屏幕中间位置
                        x = int(screen_width * 0.5)
                        y = int(screen_height * 0.4)
                        self.driver.tap([(x, y)], 500)
                        print(f"已点击屏幕位置: ({x}, {y})")

                        date_found = True
                    except Exception as e:
                        print(f"点击屏幕中间位置失败: {str(e)}")
                
                
                # 选择票档
                try:
                    print("开始选择票档...")
                    
                    # 尝试找到票档列表
                    ticket_selectors = [
                        # 匹配截图中的价格元素格式（如"499元"、"699元"等）
                        (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "元") and not(contains(@text, "缺货登记"))]/../..'),
                        (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "元")]/../..'),
                        
                        # 匹配价格数字（如"499"、"699"等）
                        (AppiumBy.XPATH, '//android.widget.TextView[matches(@text, "[0-9]+元") and not(contains(@text, "缺货登记"))]/../..'),
                        (AppiumBy.XPATH, '//android.widget.TextView[matches(@text, "[0-9]+元")]/../..'),
                        
                        # 原有选择器
                        (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "票档")]/../..'),
                        (AppiumBy.XPATH, '//android.view.ViewGroup[contains(@resource-id, "item_container")]'),
                        (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "¥")]/../..'),
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("¥")'),
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("票档")'),
                        (AppiumBy.XPATH, '//android.widget.FrameLayout[contains(@resource-id, "item_container")]'),
                        (AppiumBy.XPATH, '//android.widget.LinearLayout[contains(@resource-id, "item_container")]')
                    ]
                    
                    ticket_found = False
                    for selector_type, selector_value in ticket_selectors:
                        try:
                            print(f"尝试使用选择器: {selector_type} - {selector_value}")
                            ticket_elements = self.driver.find_elements(selector_type, selector_value)
                            
                            if ticket_elements and len(ticket_elements) > 0:
                                print(f"找到 {len(ticket_elements)} 个票档选项")
                                
                                # 过滤掉包含"缺货登记"的元素
                                available_tickets = []
                                for element in ticket_elements:
                                    try:
                                        element_text = element.text
                                        print(f"票档元素文本: {element_text}")
                                        if "缺货登记" not in element_text:
                                            available_tickets.append(element)
                                    except Exception:
                                        continue
                                
                                # 如果有可用票档，选择第一个
                                if available_tickets:
                                    available_tickets[0].click()
                                    print("已选择第一个可用票档")
                                    ticket_found = True
                                # 如果没有可用票档，选择第一个票档
                                elif ticket_elements:
                                    ticket_elements[0].click()
                                    print("未找到可用票档，选择第一个票档")
                                    ticket_found = True
                                
                                
                                # 选择数量，根据配置中的抢票人数
                                try:
                                    print("开始选择数量...")
                                    # 获取抢票人数
                                    num_tickets = len(self.config.users)
                                    print(f"抢票人数: {num_tickets}")
                                    
                                    # 如果人数为1，则不需要点击加号，直接进行下一步
                                    if num_tickets == 1:
                                        print("抢票人数为1，无需点击加号，直接进行下一步")
                                        # 保存选择数量后的截图
                                        
                                        # 点击确定按钮
                                        print("人数为1，直接点击确定按钮...")
                                        confirm_selectors = [
                                            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches(".*确定.*|.*购买.*")'),
                                            (AppiumBy.XPATH, '//android.widget.Button[contains(@text, "确定")]'),
                                            (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "确定")]'),
                                            (By.ID, "btn_buy_view")
                                        ]
                                        
                                        for selector_type, selector_value in confirm_selectors:
                                            try:
                                                if self.ultra_fast_click(selector_type, selector_value):
                                                    print(f"成功点击确定按钮: {selector_type} - {selector_value}")
                                                    # 设置标记，表示已完成选择数量和确认
                                                    ticket_found = True
                                                    break
                                            except Exception as e:
                                                print(f"点击确定按钮失败: {selector_type} - {selector_value} - {e}")
                                                continue
                                    else:
                                        
                                        # 直接使用固定坐标点击加号按钮
                                        clicks_needed = num_tickets - 1
                                        print(f"需要点击加号 {clicks_needed} 次")
                                        
                                        # 获取屏幕尺寸
                                        window_size = self.driver.get_window_size()
                                        width = window_size['width']
                                        height = window_size['height']
                                        
                                        # 尝试先通过元素定位加号按钮
                                        try:
                                            # 尝试通过各种选择器定位加号按钮
                                            plus_selectors = [
                                                (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "+")]'),
                                                (AppiumBy.XPATH, '//android.widget.Button[contains(@resource-id, "plus")]'),
                                                (AppiumBy.XPATH, '//android.widget.ImageView[contains(@resource-id, "plus")]'),
                                                (AppiumBy.XPATH, '//android.view.View[contains(@resource-id, "plus")]'),
                                                (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "1")]/following-sibling::*'),
                                                (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "1张")]/following-sibling::*')
                                            ]
                                            
                                            plus_button = None
                                            for selector_type, selector_value in plus_selectors:
                                                try:
                                                    elements = self.driver.find_elements(selector_type, selector_value)
                                                    if elements and len(elements) > 0:
                                                        plus_button = elements[0]
                                                        print(f"找到加号按钮元素: {selector_type} - {selector_value}")
                                                        break
                                                except Exception:
                                                    continue
                                            
                                            # 如果找到了加号按钮元素，直接点击
                                            if plus_button:
                                                for i in range(clicks_needed):
                                                    plus_button.click()
                                                    print(f"成功点击加号按钮元素，当前数量: {i + 2}")
                                                    time.sleep(delay_time)
                                                    
                                                
                                                # 点击确定按钮
                                                print("数量选择完成，点击确定按钮...")
                                                confirm_selectors = [
                                                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches(".*确定.*|.*购买.*")'),
                                                    (AppiumBy.XPATH, '//android.widget.Button[contains(@text, "确定")]'),
                                                    (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "确定")]'),
                                                    (By.ID, "btn_buy_view"),
                                                    (AppiumBy.XPATH, '//android.view.View[contains(@text, "确定")]')
                                                ]
                                                
                                                confirm_clicked = False
                                                for selector_type, selector_value in confirm_selectors:
                                                    try:
                                                        confirm_elements = self.driver.find_elements(selector_type, selector_value)
                                                        if confirm_elements and len(confirm_elements) > 0:
                                                            confirm_elements[0].click()
                                                            print(f"成功点击确定按钮: {selector_type} - {selector_value}")
                                                            confirm_clicked = True
                                                            
                                                            # 等待观演人选择页面加载
                                                            time.sleep(delay_time)
                                                            print("开始勾选观演人...")
                                                            
                                                            try:
                                                                # 检查是否在观演人选择页面
                                                                page_source = self.driver.page_source
                                                                if "观演人" in page_source or "选择收货人" in page_source or "选择购票人" in page_source:
                                                                    print("已确认进入观演人选择页面")
                                                                else:
                                                                    print("警告：可能未进入观演人选择页面，尝试继续执行...")
                                                                
                                                                
                                                                # 方法1：使用用户名称精确匹配
                                                                user_clicks = []
                                                                for user in self.config.users:
                                                                    print(f"准备勾选观演人: {user}")
                                                                    user_clicks.append((AppiumBy.XPATH, f'//android.widget.CheckBox[..//*[contains(@text, "{user}")]]'))

                                                                # 尝试使用ultra_batch_click进行批量点击
                                                                self.ultra_batch_click(user_clicks)
                                                                
                                                                
                                                                
                                                                # 尝试点击提交订单按钮
                                                                submit_selectors = [
                                                                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("立即提交")'),
                                                                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches(".*提交.*|.*确认.*")'),
                                                                    (By.XPATH, '//*[contains(@text,"提交")]')
                                                                 ]
                                                                self.smart_wait_and_click(*submit_selectors[0], submit_selectors[1:])
                                                                
                                                            except Exception as e:
                                                                print(f"勾选观演人过程中出现错误: {str(e)}")


                                                            if ticket_found:
                                                                return True
                                                            time.sleep(delay_time)
                                                            break
                                                    except Exception as e:
                                                        print(f"点击确定按钮失败: {selector_type} - {selector_value} - {e}")
                                                        continue
                                                
                                        except Exception as e:
                                            print(f"通过元素定位加号按钮失败: {str(e)}")
                                    
                                        
                                except Exception as e:
                                    print(f"选择数量过程中出现错误: {str(e)}")
                        except Exception as e:
                            print(f"使用选择器 {selector_type} - {selector_value} 选择票档失败: {str(e)}")
                            continue
                    print("人数选择完成")
                    
                    
                except Exception as e:
                    print(f"选择票档过程中出现错误: {str(e)}")

                
                return True
            else:
                print("所有点击立即预订按钮的尝试均失败，请检查页面状态")
                return False


        except Exception as e:
            print(f"抢票过程发生错误: {e}")
            return False
        finally:
            time.sleep(delay_time)  # 给最后的操作一点时间
            self.driver.quit()

    def run_with_retry(self, max_retries=3):
        """带重试机制的抢票"""
            
        for attempt in range(max_retries):
            print(f"第 {attempt + 1} 次尝试...")
            if self.run_ticket_grabbing():
                print("抢票成功！")
                return True
            else:
                print(f"第 {attempt + 1} 次尝试失败")
                if attempt < max_retries - 1:
                    print("2秒后重试...")
                    time.sleep(delay_time)
                    # 重新初始化驱动
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self._setup_driver()

        print("所有尝试均失败")
        return False


def wait_until(target_time: str, check_interval=0.01, advance_seconds=0):
    """
    等待直到目标时间（格式: HH:MM:SS），期间每隔 check_interval 检查一次
    """
    target = datetime.strptime(target_time, "%H:%M:%S").replace(
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day
    ) - timedelta(seconds=advance_seconds)
    print(f"等待到 {target} ...")

    while True:
        now = datetime.now()
        print(f"当前时间: {now}")
        if now >= target:
            print("时间已到，开始执行点击操作！")
            break
        time.sleep(check_interval)


# 使用示例
if __name__ == "__main__":
    config = Config.load_config()
    wait_until(config.time, advance_seconds=20)
    bot = DamaiBot()
    bot.run_with_retry(max_retries=3)
