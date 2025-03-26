import asyncio
import json
import time
from pathlib import Path
from urllib.parse import urlparse

import mysql.connector
from playwright.async_api import async_playwright

import wechat
from conf import BASE_DIR, LOCAL_CHROME_PATH, HEADLESS, DB_CONFIG
from utils.base_social_media import set_init_script


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def updataAnswer(id, answer, answerTxt):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE processed_ids SET answer = %s, answerTxt = %s WHERE id = %s",
                   (answer, answerTxt, id))
    conn.commit()
    conn.close()


def query_answer_by_id(_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT answer,activityUrl FROM processed_ids WHERE id = %s", (_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1]
    return None, None


async def init_dazhong_cookie(account_file, url1):
    url = url1 + "&processKey=MF17712895"
    async with async_playwright() as playwright:
        options = {
            'args': [
                '--lang en-GB',
            ],
            'headless': HEADLESS,  # Set headless option here
        }
        browser = await playwright.chromium.launch(**options)
        # 使用 iPhone 14 Pro Max 进行设备仿真
        iPhone = playwright.devices["iPhone 14 Pro Max"]
        context = await browser.new_context(
            **iPhone,  # 直接传入设备配置
            storage_state=account_file  # 保持登录状态
        )
        context = await set_init_script(context)
        page = await context.new_page()
        # https://m-pass.svw-volkswagen.com/login
        await page.goto(url)
        await page.pause()
        await context.storage_state(path=account_file)


async def keep_login(account_file, _url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,  # 设置为 False 以便观察刷新效果
            executable_path=LOCAL_CHROME_PATH  # 确保此路径正确
        )
        # 使用 iPhone 14 Pro Max 进行设备仿真
        iPhone = playwright.devices["iPhone 14 Pro Max"]
        context = await browser.new_context(
            **iPhone,  # 直接传入设备配置
            storage_state=account_file  # 保持登录状态
        )

        page = await context.new_page()

        print("页面已加载，开始定期刷新...")

        await page.goto(_url)
        await page.wait_for_load_state('load')
        await page.wait_for_load_state("networkidle")
        while True:
            try:
                await asyncio.sleep(20)  # 等待20秒
                current_url = page.url
                # 使用 urllib 提取域名
                parsed_url = urlparse(current_url)
                domain = parsed_url.netloc
                if domain == "m-pass.svw-volkswagen.com":
                    print(f"掉登录了，重新登录！")
                    wechat.sendtext(f"大众账号： 掉登录了，需要重新登录！")
                    return
                # 定位元素 V豆页面
                back = page.locator('.backImgApp.icon.iconfont.icon-arrow-left')
                vdou = page.locator('.am-flexbox.ml-mItem.am-flexbox-dir-column.am-flexbox-align-center')
                # 检查元素是否存在并可见
                if await vdou.count() > 0:
                    print("✅ vdou元素存在，执行点击")
                    await vdou.first.click()
                    await asyncio.sleep(3)  # 等待3秒
                if await back.count() > 0:
                    print("✅ back元素存在，执行点击")
                    await back.click()
                    await asyncio.sleep(3)  # 等待3秒

                try:
                    print("✅ 更新cookie!")
                    await context.storage_state(path=f"{account_file}")
                except Exception as e:
                    print(f"❌ Page load failed: {e}")
            except Exception as e:
                print(f"点击时发生错误: {e}")


async def auto_correct_answer(account_file, _id):
    # 读取 JSON 文件
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,  # 设置为 False 以便观察刷新效果
            executable_path=LOCAL_CHROME_PATH  # 确保此路径正确
        )
        # 使用 iPhone 14 Pro Max 进行设备仿真
        iPhone = playwright.devices["iPhone 14 Pro Max"]
        context = await browser.new_context(
            **iPhone,  # 直接传入设备配置
            storage_state=account_file  # 保持登录状态
        )
        context = await set_init_script(context)  # 如果需要，绕过检测

        page = await context.new_page()

        answers, _url = query_answer_by_id(_id)
        if answers is None:
            print("未查询到答案")
            return
        # 打开页面
        await page.goto(_url)
        # 等待页面加载
        await page.wait_for_timeout(3000)  # 3秒等待
        await page.wait_for_load_state('load')
        await page.wait_for_load_state("networkidle")
        # 获取所有问题区域
        questions = await page.query_selector_all(".voteBg")
        for answer in answers:
            question_index = answer[0] - 1  # 题目序号，转换为索引（从0开始）
            selected_options = answer[1]  # 需要点击的选项列表

            if 0 <= question_index < len(questions):
                question_element = questions[question_index]
                options = await question_element.query_selector_all(".optionItem")

                # 遍历答案中指定的选项序号，点击对应选项
                for option_index in selected_options:
                    if 0 <= option_index - 1 < len(options):  # 选项索引转换
                        await options[option_index - 1].click()
                        time.sleep(1)  # 模拟用户操作间隔
        print("所有答案已自动提交")
        time.sleep(1)  # 等待一秒，防止点击过快导致页面未响应
        bottom_bg = await page.query_selector(".bottomBg")
        if bottom_bg:
            print("✅ 确认按钮存在！")
            await bottom_bg.click()  # 执行点击操作
            time.sleep(0.5)  # 等待一秒，防止点击过快导致页面未响应
            confirm = await page.query_selector(".van-dialog__confirm")
            if confirm:
                # 多选只选择一个的情况
                print("✅ 确定按钮存在！")
                time.sleep(0.5)  # 等待一秒，防止点击过快导致页面未响应
                await confirm.click()  # 执行点击操作
        else:
            print("❌ 确认按钮不存在！")


async def auto_answer_first(account_file, _url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=HEADLESS,
            executable_path=LOCAL_CHROME_PATH  # Ensure this path is correct
        )
        # 使用 iPhone 14 Pro Max 进行设备仿真
        iPhone = playwright.devices["iPhone 14 Pro Max"]
        context = await browser.new_context(
            **iPhone,  # 直接传入设备配置
            storage_state=account_file  # 保持登录状态
        )
        context = await set_init_script(context)  # Bypass detection if needed

        page = await context.new_page()

        # 打开答题页面
        await page.goto(_url)
        # 等待页面加载
        await page.wait_for_timeout(3000)  # 3秒等待
        # 获取所有问题区域
        questions = await page.query_selector_all(".voteBg")

        for question in questions:
            # 获取该问题下的所有选项
            options = await question.query_selector_all(".optionItem")

            if options:
                # 点击第一个选项
                await options[0].click()
                time.sleep(1)  # 等待一秒，防止点击过快导致页面未响应
        # 提交答案
        # 获取所有问题区域
        time.sleep(1)  # 等待一秒，防止点击过快导致页面未响应
        bottom_bg = await page.query_selector(".bottomBg")
        if bottom_bg:
            print("✅ 确认按钮存在！")
            await bottom_bg.click()  # 执行点击操作
            time.sleep(0.5)  # 等待一秒，防止点击过快导致页面未响应
            confirm = await page.query_selector(".van-dialog__confirm")
            if confirm:
                # 多选只选择一个的情况
                print("✅ 确定按钮存在！")
                time.sleep(0.5)  # 等待一秒，防止点击过快导致页面未响应
                await confirm.click()  # 执行点击操作
        else:
            print("❌ 确认按钮不存在！")


async def get_answer(account_file, _url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=HEADLESS,
            executable_path=LOCAL_CHROME_PATH  # Ensure this path is correct
        )
        # 使用 iPhone 14 Pro Max 进行设备仿真
        iPhone = playwright.devices["iPhone 14 Pro Max"]
        context = await browser.new_context(
            **iPhone,  # 直接传入设备配置
            storage_state=account_file  # 保持登录状态
        )
        context = await set_init_script(context)  # Bypass detection if needed

        page = await context.new_page()

        TARGET_PREFIX = "https://m.svw-volkswagen.com/ss-survey-adapter/api/survey/"

        correct_answers = []  # List to store the correct answers

        async def handle_response(response):
            if response.url.startswith(TARGET_PREFIX):
                try:
                    if "application/json" in response.headers.get("content-type", ""):
                        json_data = await response.json()
                        print(f"✅ JSON Response: {json_data}")

                        # Extract correct answers
                        if 'data' in json_data and 'surveyQuestionInfoList' in json_data['data']:
                            for idx, question in enumerate(json_data['data']['surveyQuestionInfoList'], start=1):
                                options = question.get('surveyOptionInfoList', [])

                                # 提取所有 `boolCorrectOption=True` 的选项
                                correct_option_seqs = [
                                    option['optionSeq'] for option in options if option.get('boolCorrectOption') is True
                                ]

                                # 如果 `boolCorrectOption=True` 存在，则使用它
                                if correct_option_seqs:
                                    correct_answers.append((idx, correct_option_seqs))
                                    print(f"问题{idx}，正确答案 {', '.join(map(str, correct_option_seqs))}；")
                                else:
                                    # 如果没有正确答案，则选择第一个选项
                                    if options:
                                        first_option_seq = options[0].get('optionSeq')
                                        correct_answers.append((idx, [first_option_seq]))
                                        print(f"问题{idx}，没有正确答案标记，默认选第一个选项 {first_option_seq}；")
                except Exception as e:
                    print(f"⚠️ JSON 解析失败: {e}")

            # 绑定事件监听

        page.on("response", handle_response)

        await page.goto(_url)
        await page.wait_for_load_state("load")
        await page.wait_for_load_state("networkidle")

        await browser.close()

        return correct_answers  # Return the correct answers as a result


def run(surveyurl, item_id):
    account_file = Path(BASE_DIR / "cookies" / "dazhong" / "account.json")
    url = surveyurl + "&processKey=MF17712895"
    asyncio.run(auto_answer_first(str(account_file), url))
    getAnswer = asyncio.run(get_answer(str(account_file), url))

    formatted_result = ' '.join([f'问题{item[0]}，正确答案 {", ".join(map(str, item[1]))}；' for item in getAnswer])

    if getAnswer:
        print("最终的正确答案：", formatted_result)
        formatted_answer_json = json.dumps(getAnswer)
        updataAnswer(item_id, formatted_answer_json, formatted_result)

        return formatted_result
    else:
        return None


def timer():
    url1 = "https://m-club.svw-volkswagen.com/pointEvents"
    account_file = Path(BASE_DIR / "cookies" / "dazhong" / "account.json")
    asyncio.run(keep_login(account_file, url1))


if __name__ == '__main__':
    # url = "https://m.svw-volkswagen.com/marketing/survey/questionAnswer/index.html?surveyId=1900016874458370050"
    # url = "https://mall.svw-volkswagen.com/user"
    # run(url, "1420491057860739072")
    timer()
    # account_file = Path(BASE_DIR / "cookies" / "dazhong" / "account.json")
    # auto = asyncio.run(init_dazhong_cookie(str(account_file), url))
    # getAnswer = asyncio.run(extractAnswers(str(account_file), url))
    # formatted_result = ' '.join([f'问题{item[0]}，正确答案 {item[1][0]}；' for item in getAnswer])
    # print("最终的正确答案：", formatted_result)
