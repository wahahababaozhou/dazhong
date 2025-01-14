import base64
import hashlib

import requests

url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=46b23bb7-8567-4637-992c-c8ef10654284'


# 发送消息函数, msgtype定义：text 发送字符串消息，markdown 发送图片消息，image 发送图片消息， news 发送图文消息
def postmsg(post_data, msgtype):
    # sss = "这是一条用python发送的测试信息，请忽略！"
    post_data = '{"msgtype" : "%s", "%s" : %s}' % (msgtype, msgtype, post_data)
    print(post_data)
    if url == '':
        print('URL地址为空！')
    else:
        r = requests.post(url, data=post_data.encode())
        rstr = r.json()
        if r.status_code == 200 and 'error' not in rstr:
            result = '发送成功'
            return result
        else:
            return 'Error'


# 发送图片消息
def sendImg(basestr):
    md5 = hashlib.md5()
    basestr = basestr.replace('data:image/jpeg;base64,', '')
    md5.update(base64.b64decode(basestr, altchars=None, validate=False))
    md5_result = md5.hexdigest()
    out_pic_msg = '{"base64":"%s", "md5":"%s"}' % (basestr, md5_result)
    return postmsg(out_pic_msg, "image")


# 发送文本消息
def sendtext(msg):
    msg_json = '{"content":"%s", "mentioned_mobile_list":["@all"]}' % (msg)
    try:
        return postmsg(msg_json, "text")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    basestr = 'data:image/jpeg;base64,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'
    print(basestr.replace('data:image/jpeg;base64,', ''))
    sendImg(basestr)
