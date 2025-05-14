from gewechat_client import GewechatClient
import http.client
import json
import wechat

# from phonwx import publish_group_notice

# 配置参数
base_url = "http://localhost:2531/v2/api"
token = "797fcae1307149d3bbe566fa7d162c85"
appid = "wx_UBkF_48rXEAAozpuU9JTk"
uuid = "oY3kAuyN8-Foyn5v5Ha7"


def syncGeweStatus():
    # 创建 GewechatClient 实例
    client = GewechatClient(base_url, token)
    # 登录, 自动创建二维码，扫码后自动登录
    app_id, error_msg = client.login(appid)
    if error_msg:
        print("登录失败")
        return
    try:
        # 发送消息
        send_msg_result = client.get_profile(app_id)
        if send_msg_result.get('ret') != 200:
            print("获取个人信息失败:", send_msg_result)
            wechat.sendtext(f"gewe获取个人信息失败：{str(send_msg_result)}")
            return
        print("gewe获取个人信息成功:", send_msg_result)
    except Exception as e:
        print("获取个人信息失败:", str(e))
        wechat.sendtext(f"gewe获取个人信息失败：{str(e)}")


def sendDzMsgToWeCom(msg, title, desc, url, activityUrl="", item_id=""):
    # 发送消息至企业微信
    if activityUrl:
        msgData = msg + "\n活动链接： \n" + url + "\n直接答题链接" + activityUrl
    else:
        msgData = msg + "\n活动链接： \n" + url
    wechat.sendtext(msgData)
    sendToGongzhonghao(title, msgData)


def sendToGongzhonghao(title, content):
    conn = http.client.HTTPSConnection("www.pushplus.plus")
    payload = json.dumps({
        "token": "ff28e59b90264a2f85233d947a3ea8d3",
        "title": title,
        "content": content,
        "template": "markdown"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/send", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


def sendDzMsgToTeambak(msg, title, desc, url, activityUrl="", item_id=""):
    # 创建 GewechatClient 实例
    client = GewechatClient(base_url, token)
    # 登录, 自动创建二维码，扫码后自动登录
    app_id, error_msg = client.login(appid)
    if error_msg:
        print("登录失败")
        return
    try:
        # 发送消息
        # 薅豆子群 34662819283@chatroom
        # 测试群 56461690037@chatroom
        # yq wx  wxid_5fcqy84vsodb21
        userid = "34662819283@chatroom"
        # userid = "wxid_5fcqy84vsodb21"
        send_msg_result = client.post_text(app_id, userid, "@所有人 " + msg, ats="notify@all")
        client.post_link(app_id,
                         userid,
                         title,
                         desc,
                         url,
                         "https://img0.baidu.com/it/u=3208604261,3520655236&fm=253&fmt=auto&app=138&f=JPEG?w=771&h=500")
        if activityUrl:
            client.post_link(app_id,
                             userid,
                             title,
                             "--直接答题链接--" + desc,
                             activityUrl,
                             "https://img0.baidu.com/it/u=3208604261,3520655236&fm=253&fmt=auto&app=138&f=JPEG?w=771&h=500")
            # 尝试获取答案
            # 调用run方法，传入activityUrl和item_id
            # answerTxt = run(activityUrl, item_id)
            # if answerTxt:
            #     client.post_text(app_id, userid, answerTxt)

        if send_msg_result.get('ret') != 200:
            print("发送消息失败:", send_msg_result)
            wechat.sendtext(f"gewe发送微信群消息失败：{send_msg_result}")
            return
        print("发送消息成功:", send_msg_result)
    except Exception as e:
        print("发送微信群消息失败:", str(e))
        wechat.sendtext(f"gewe发送微信群消息失败：{str(e)}")


if __name__ == "__main__":
    sendDzMsgToWeCom(
        " 新答题类V豆奖励内容\n    文章标题: 周末来打卡 | 你的目标现在完成了吗？\n    发布时间: 2025-05-03 11:00:07\n    审核通过时间: 2025-05-03 11:02:30",
        "周末来打卡 | 你的目标现在完成了吗？", "test", "https://m.svw-volkswagen.com/community/article/article-detail?id=1438248395078381568",
        "https://m.svw-volkswagen.com/marketing/survey/v2/questionnaire?surveyId=1920313680169734145&surveyType=7")
