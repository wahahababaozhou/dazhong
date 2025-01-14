from gewechat_client import GewechatClient

def sendMsgToTeam(msg, title, desc, cardId):
    # 配置参数
    base_url = "http://localhost:2531/v2/api"
    token = "797fcae1307149d3bbe566fa7d162c85"
    app_id = "wx_UBkF_48rXEAAozpuU9JTk"

    # 创建 GewechatClient 实例
    client = GewechatClient(base_url, token)

    # 登录, 自动创建二维码，扫码后自动登录
    app_id, error_msg = client.login(app_id=app_id)
    if error_msg:
        print("登录失败")
        return
    try:
        # 发送消息
        send_msg_result = client.post_text(app_id, "56461690037@chatroom", "@所有人 " + msg, ats="notify@all")
        client.post_link(app_id,
                         "56461690037@chatroom",
                         title,
                         desc,
                         "https://m.svw-volkswagen.com/community/article/article-detail?id=" + cardId,
                         "https://pics3.baidu.com/feed/0824ab18972bd407a9403f336648d15c0db30943.jpeg@f_auto?token=d26f7f142871542956aaa13799ba1946")
        if send_msg_result.get('ret') != 200:
            print("发送消息失败:", send_msg_result)
            return
        print("发送消息成功:", send_msg_result)
    except Exception as e:
        print("Failed to fetch contacts list:", str(e))


if __name__ == "__main__":
    sendMsgToTeam("123", "tt", "dd", "123")
