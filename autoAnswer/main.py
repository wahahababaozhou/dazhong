import asyncio
import time
from pathlib import Path
import mysql.connector
from playwright.async_api import async_playwright
from selenium.webdriver.common.by import By

from conf import BASE_DIR, LOCAL_CHROME_PATH, HEADLESS, DB_CONFIG
from utils.base_social_media import set_init_script
import json


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


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
        context = await browser.new_context()
        context = await set_init_script(context)
        page = await context.new_page()
        # https://m-pass.svw-volkswagen.com/login
        await page.goto(url)
        await page.pause()
        await context.storage_state(path=account_file)


async def autoAnswer(account_file, url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=HEADLESS,
            executable_path=LOCAL_CHROME_PATH  # Ensure this path is correct
        )
        context = await browser.new_context(storage_state=account_file)
        context = await set_init_script(context)  # Bypass detection if needed

        page = await context.new_page()
        await page.set_viewport_size({'width': 1280, 'height': 800})

        # 打开答题页面
        await page.goto(url)
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

        try:
            # await page.wait_for_url(url, timeout=15000)  # Timeout after 15s
            print("✅ 更新cookie!")
            await context.storage_state(path=f"{account_file}")
        except Exception as e:
            print(f"❌ Page load failed: {e}")


async def extractAnswers(accountFile, url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=HEADLESS,
            executable_path=LOCAL_CHROME_PATH  # Ensure this path is correct
        )
        context = await browser.new_context(storage_state=accountFile)
        context = await set_init_script(context)  # Bypass detection if needed

        page = await context.new_page()
        await page.set_viewport_size({'width': 1280, 'height': 800})

        TARGET_PREFIX = "https://m.svw-volkswagen.com/ss-survey-adapter/api/survey/"

        correct_answers = []  # List to store the correct answers

        async def handle_response(response):
            if response.url.startswith(TARGET_PREFIX):  # Match the specified prefix
                try:
                    if "application/json" in response.headers.get("content-type", ""):
                        json_data = await response.json()
                        print(f"✅ JSON Response: {response.url}\n📦 Data: {json_data}\n")

                        # Extract correct answers
                        if 'data' in json_data and 'surveyQuestionInfoList' in json_data['data']:
                            for idx, question in enumerate(json_data['data']['surveyQuestionInfoList'], start=1):
                                correct_answer = [
                                    option['optionSeq']
                                    for option in question.get('surveyOptionInfoList', [])
                                    if option.get('boolCorrectOption') is True
                                ]
                                if correct_answer:
                                    correct_answers.append(
                                        (idx, correct_answer))  # Store question index and correct options
                                    print(f"问题{idx}，正确答案 {', '.join(map(str, correct_answer))}；")
                except Exception as e:
                    print(f"⚠️ Failed to parse JSON: {e}")

        page.on("response", lambda response: asyncio.create_task(handle_response(response)))

        await page.goto(url)
        await page.wait_for_load_state("load")
        await page.wait_for_load_state("networkidle")

        try:
            # await page.wait_for_url(url, timeout=15000)  # Timeout after 15s
            print("✅ 更新cookie!")
            await context.storage_state(path=f"{accountFile}")
        except Exception as e:
            print(f"❌ Page load failed: {e}")

        await browser.close()

        return correct_answers  # Return the correct answers as a result


def updataAnswer(id, answer, answerTxt):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE processed_ids SET answer = %s, answerTxt = %s WHERE id = %s",
                   (answer, answerTxt, id))
    conn.commit()
    conn.close()


def run(surveyurl, item_id):
    account_file = Path(BASE_DIR / "cookies" / "dazhong" / "account.json")
    url = surveyurl + "&processKey=MF17712895"
    # url = "https://m.svw-volkswagen.com/marketing/survey/questionAnswer/index.html?surveyId=1900016874458370050&n=n"
    asyncio.run(autoAnswer(str(account_file), url))
    getAnswer = asyncio.run(extractAnswers(str(account_file), url))

    formatted_result = ' '.join([f'问题{item[0]}，正确答案 {", ".join(map(str, item[1]))}；' for item in getAnswer])

    if getAnswer:
        print("最终的正确答案：", formatted_result)
        formatted_answer_json = json.dumps(getAnswer)
        updataAnswer(item_id, formatted_answer_json, formatted_result)

        return formatted_result
    else:
        return None
def timer():
    url = "https://m.svw-volkswagen.com/marketing/survey/questionAnswer/index.html?surveyId=1900016874458370050"
    run(url, "1420491057860739072")
if __name__ == '__main__':
    url = "https://m.svw-volkswagen.com/marketing/survey/questionAnswer/index.html?surveyId=1900016874458370050"
    run(url, "1420491057860739072")

    # account_file = Path(BASE_DIR / "cookies" / "dazhong" / "account.json")
    # auto = asyncio.run(init_dazhong_cookie(str(account_file), url))
    # getAnswer = asyncio.run(extractAnswers(str(account_file), url))
    # formatted_result = ' '.join([f'问题{item[0]}，正确答案 {item[1][0]}；' for item in getAnswer])
    # print("最终的正确答案：", formatted_result)
