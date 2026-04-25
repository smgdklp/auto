from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
import time
from datetime import datetime

edge_options = Options()
edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(r"C:\Users\ZhuanZ\AppData\Local\Programs\Python\Python313\msedgedriver.exe")
driver = webdriver.Edge(service=service, options=edge_options)

def init_driver():
    edge_options = Options()
    edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    service = Service(r"C:\Users\ZhuanZ\AppData\Local\Programs\Python\Python313\msedgedriver.exe")
    return webdriver.Edge(service=service, options=edge_options)

try:
    driver.switch_to.window(driver.window_handles[0])
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if "学生学习页面" in driver.title:
            break
    else:
        print("找不到页面")
        driver.quit()
        exit()
except:
    print("创立失败")
    driver.quit()
    exit()

life = True
index = 0

def check_connect():
    global driver
    try:
        # 检查是否还能连接
        driver.title
        print("连接正常")
        return True
    except (InvalidSessionIdException, WebDriverException) as e:
        print(f"连接断开: {e}")
        try:
            print("尝试重连...")
            driver.quit()
        except:
            pass
        time.sleep(2)
        try:
            driver = init_driver()
            # 重新找页面
            driver.switch_to.window(driver.window_handles[0])
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if "学生学习页面" in driver.title:
                    print("重连成功")
                    return True
            print("重连成功但找不到学习页面")
            return False
        except Exception as e2:
            print(f"重连失败: {e2}")
            print("老大，连爆了。。。")
            return False

def check_play():
    driver.switch_to.default_content()
    
    try:
        iframe = driver.find_element("css selector", "iframe#iframe")
        driver.switch_to.frame(iframe)
        try:
            video_iframe = driver.find_element("css selector", "iframe.ans-insertvideo-online")
            driver.switch_to.frame(video_iframe)
        except:
            pass
        
        # 获取 video 元素
        video = driver.find_element("css selector", "video#video_html5_api, video")
        
        # 获取播放状态（处理 None 值）
        is_ended = driver.execute_script("return arguments[0].ended;", video)
        current_time = driver.execute_script("return arguments[0].currentTime;", video)
        duration = driver.execute_script("return arguments[0].duration;", video)
        
        # 安全打印（处理 None 值）
        if current_time is not None and duration is not None:
            print(f"视频进度: {current_time:.1f} / {duration:.1f} 秒, ended={is_ended}")
        else:
            print(f"视频进度: 加载中... currentTime={current_time}, duration={duration}")
        
        # 判断是否播放完成（需要确保 duration 不是 None）
        if is_ended or (duration and duration > 0 and current_time and current_time >= duration - 1):
            print("检测视频已播放完成，准备下一节")
            driver.switch_to.default_content()
            try:
                next_btn = driver.find_element("css selector", "div#prevNextFocusNext")
                next_btn.click()
                print("切入下一节")
            except:
                print("下一节按钮未找到")
        else:
            print("检测视频未播放完成")
            # 检查是否在播放，没播放就点播放（需要确保 video 存在）
            if video:
                is_paused = driver.execute_script("return arguments[0].paused;", video)
                if is_paused:
                    print("视频处于暂停状态，尝试播放")
                    # 滑动到页面最底部
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    print("成功滑动")
                    
                    # 找播放按钮
                    try:
                        btn = driver.find_element("css selector", "button.vjs-big-play-button")
                        print(f"按键状态: 显示={btn.is_displayed()}, 可用={btn.is_enabled()}")
                        driver.execute_script("arguments[0].click();", btn)
                        print("已执行点击，开始播放")
                    except:
                        # 如果没找到播放按钮，尝试直接播放video
                        try:
                            driver.execute_script("arguments[0].play();", video)
                            print("已执行video.play()")
                        except:
                            print("video.play() 执行失败")
                else:
                    print("视频正在播放中")
            else:
                print("未找到video元素")
                
    except Exception as e:
        print(f"视频检测出错: {e}")
    finally:
        driver.switch_to.default_content()
def check_win():
    driver.switch_to.default_content()
    
    try:
        pop = driver.find_element("css selector", "div.maskDiv.jobFinishTip")
        if pop.is_displayed():
            print("任务点未完成弹窗，点去学习")
            go_learn = driver.find_element("css selector", "a.btnBlue")
            go_learn.click()
            print("已点去学习")
    except:
        pass

    try:
        limit1 = driver.find_element("css selector", "div.maskDiv.jobCountDiv")
        if limit1.is_displayed() and "视频任务点完成数已达上限" in limit1.text:
            print("老大出事了，跑路了")
            driver.quit()
            exit()
    except:
        pass

    try:
        limit2 = driver.find_element("css selector", "div.maskDiv.jobCountDiv")
        if limit2.is_displayed() and "视频观看时长已达上限" in limit2.text:
            print("老大出事了，跑路了")
            driver.quit()
            exit()
    except:
        pass

while life:
    current_time = datetime.now()
    print(f"第 {index} 次 - {current_time.hour:02d}:{current_time.minute:02d}")
    
    if not check_connect():
        print("连接失败，退出")
        break
    
    check_play()
    check_win()
    time.sleep(100)  # 每5分钟检测一次视频进度
    index += 1