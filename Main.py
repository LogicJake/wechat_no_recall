# coding=utf-8
import os
import re
import shutil
import time
import itchat
from itchat.content import *
def ClearTimeOutMsg():
    if len(msg_dict) > 0:
        for msgid in list(msg_dict): #由于字典在遍历过程中不能删除元素，故使用此方法
            if time.time() - msg_dict.get(msgid, None)["msg_time"] > 130.0: #超时两分钟
                item = msg_dict.pop(msgid)
                #可下载类消息，并删除相关文件
                if item['msg_type'] == "Picture" \
                        or item['msg_type'] == "Recording" \
                        or item['msg_type'] == "Video" \
                        or item['msg_type'] == "Attachment":
                    if os.path.exists("."+os.sep+"Cache"+os.sep+item['msg_content']):
                        os.remove("."+os.sep+"Cache"+os.sep+item['msg_content'])

# @itchat.msg_register([TEXT , MAP, CARD, SHARING,VIDEO])
# def text_reply(msg):
#     if msg['Type'] == 'Text':
#         reply_content = msg['Text']
#     elif msg['Type'] == 'Card':
#         reply_content = r" " + msg['RecommendInfo']['NickName'] + r" 's Card"
#     elif msg['Type'] == 'Map':
#         x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1,2,3)
#         if location is None:
#             reply_content = r"Location: Lat->" + x.__str__() + r" Lon->" + y.__str__()
#         else:
#             reply_content = r"Location: " + location
#     elif msg['Type'] == 'Sharing':
#         reply_content = r"Sharing"
#     friend = itchat.search_friends(userName=msg['FromUserName'])
#     itchat.send(r"Friend:%s -- %s    "
#                 r"Time:%s    "
#                 r" Message:%s" % (friend['NickName'], friend['RemarkName'], time.ctime(), reply_content),
#                 toUserName='filehelper')
#
#     itchat.send(u"我已经收到你在【%s】发送的消息【%s】稍后回复。--微信助手(Python版)".encode('gbk') % (time.ctime(), reply_content),
#                 toUserName=msg['FromUserName'])
#
# @itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video'])
# def download_files(msg):
#     if msg['Type'] == 'Picture':
#         reply_content = r"Picture"
#     elif msg['Type'] == 'Recording':
#         reply_content = r"Recoding"
#     elif msg['Type'] == 'Attachment':
#         reply_content = r"File: " + msg['FileName']
#     elif msg['Type'] == 'Video':
#         reply_content = r"video: " + msg['FileName']
#
#     msg['Text'](msg['FileName'])
#     friend = itchat.search_friends(userName=msg['FromUserName'])
#     itchat.send(u"我已经收到你在【%s】发送的消息【%s】稍后回复。--微信助手(Python版)".encode('gbk') % (time.ctime(), reply_content),
#                 toUserName=msg['FromUserName'])
#     itchat.send(r"Friend:%s -- %s    "
#                 r"Time:%s    "
#                 r" Message:%s" % (friend['NickName'], friend['RemarkName'], time.ctime(), reply_content),
#                 toUserName='filehelper')
#     itchat.send('@%s@%s'%('img' if msg['Type'] == 'Picture' else 'fil', msg['FileName']), 'filehelper')
def GetMsgFrom(msg):
    msg_group = r""
    if itchat.search_friends(userName=msg['FromUserName']):                 #如果是联系人发的消息，FromUserNmae是@开头，代表的是联系人的身份标识
        if msg['FromUserName'] == itchat.get_friends()[0]['UserName']:      #终止读取本人发的消息
            return None,None
        if itchat.search_friends(userName=msg['FromUserName'])['RemarkName']:
            msg_from = itchat.search_friends(userName=msg['FromUserName'])['RemarkName']  # 消息发送人备注
        elif itchat.search_friends(userName=msg['FromUserName'])['NickName']:  # 消息发送人昵称
            msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']  # 消息发送人昵称
        else:
            msg_from = r"读取发送消息好友失败"
    else:                                               #如果是群里的人发的消息，FromUserNmae是@@开头，代表的是群的身份标识
        msg_from = msg['ActualNickName']
        if itchat.search_chatrooms(userName=msg['FromUserName']):
            msg_group += r'[ '
            msg_group += itchat.search_chatrooms(userName=msg['FromUserName'])['NickName']
            msg_group += u' ]中, '
    return msg_from, msg_group

@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS], isFriendChat=True,
                     isGroupChat=True)
def Revocation(msg):
    itchat.get_friends(update=True)
    if msg['FromUserName'] == itchat.get_friends()[0]['UserName']:      #终止读取本人发的消息
        return
    mytime = time.localtime()  # 这儿获取的是本地时间
    #获取用于展示给用户看的时间 2017/03/03 13:23:53
    msg_time_touser = mytime.tm_year.__str__() \
                      + "/" + mytime.tm_mon.__str__() \
                      + "/" + mytime.tm_mday.__str__() \
                      + " " + mytime.tm_hour.__str__() \
                      + ":" + mytime.tm_min.__str__() \
                      + ":" + mytime.tm_sec.__str__()

    msg_id = msg['MsgId'] #消息ID
    msg_time = msg['CreateTime'] #消息时间
    msg_from,msg_group = GetMsgFrom(msg) #消息发送人昵称
    msg_type = msg['Type'] #消息类型
    msg_content = None #根据消息类型不同，消息内容不同
    msg_url = None #分享类消息有url
    #图片 语音 附件 视频，可下载消息将内容下载暂存到当前目录
    if msg['Type'] == 'Text':
        msg_content = msg['Text']
    elif msg['Type'] == 'Picture':
        msg_content = msg['FileName']
        msg['Text']("."+os.sep+"Cache"+os.sep+msg['FileName'])
    elif msg['Type'] == 'Card':
        msg_content = msg['RecommendInfo']['NickName'] + u" 的名片"
    elif msg['Type'] == 'Map':
        x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1,2,3)
        if location is None:
            msg_content = u"纬度->" + x.__str__() + u" 经度->" + y.__str__()
        else:
            msg_content = r"" + location
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_url = msg['Url']
    elif msg['Type'] == 'Recording':
        msg_content = msg['FileName']
        msg['Text']("."+os.sep+"Cache"+os.sep+msg['FileName'])
    elif msg['Type'] == 'Attachment':
        msg_content = r"" + msg['FileName']
        msg['Text']("."+os.sep+"Cache"+os.sep+msg['FileName'])
    elif msg['Type'] == 'Video':
        msg_content = msg['FileName']
        msg['Text']("."+os.sep+"Cache"+os.sep+msg['FileName'])
    elif msg['Type'] == 'Friends':
        msg_content = msg['Text']

    #更新字典
    newdict = {msg_id:{"msg_from":msg_from ,"msg_time": msg_time, "msg_time_touser": msg_time_touser, "msg_type": msg_type,"msg_content": msg_content, "msg_url": msg_url,"msg_group": msg_group }}
    msg_dict.update(newdict)
    #清理字典
    ClearTimeOutMsg()

def GetOldMsg(msg):
    old_msg_id = ""
    old_msg = {}
    if re.search(r"\!\[CDATA\[.*\]\]", msg['Content']):
        if re.search(r"\<msgid\>(.*?)\<\/msgid\>", msg['Content']):
            old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        old_msg = msg_dict.get(old_msg_id, {})
    return old_msg_id, old_msg

def GetSendMsg(old_msg, msg_time_to_user):
    msg_send = old_msg['msg_group']
    if(msg_send == None):
        return
    msg_send += u"您的好友：%s %s在[ %s ]%s撤回了一条[ %s ]消息%s内容如下:%s" % (
        old_msg.get('msg_from', None), "\n", msg_time_to_user, "\n", old_msg.get('msg_type', None), "\n",
        old_msg.get('msg_content', None))

    if old_msg['msg_type'].__eq__("Sharing"):
        msg_send += u"%s链接:%s" % ("\n", old_msg.get('msg_url', None))

    elif old_msg['msg_type'] in ['Picture', 'Recording', 'Video', 'Attachment']:
        if not os.path.exists("."+os.sep+"Revocation"+os.sep+old_msg['msg_content']):
            shutil.move(r"."+os.sep+"Cache"+os.sep + old_msg['msg_content'], r"."+os.sep+"Revocation"+os.sep)
    return msg_send

@itchat.msg_register([NOTE],isFriendChat=True, isGroupChat=True)
def SaveMsg(msg):
    mytime = time.localtime()
    msg_time_touser = "%s/%s/%s %s:%s:%s" % (
        mytime.tm_year.__str__(), mytime.tm_mon.__str__(), mytime.tm_mday.__str__(), mytime.tm_hour.__str__(),
        mytime.tm_min.__str__(), mytime.tm_sec.__str__())

    # 创建可下载消息内容的存放文件夹，并将暂存在当前目录的文件移动到该文件中
    if not os.path.exists("."+os.sep+"Revocation"+os.sep):
        os.mkdir("."+os.sep+"Revocation"+os.sep)

    msg_id, old_msg = GetOldMsg(msg)
    if old_msg:
        msg_send = GetSendMsg(old_msg, msg_time_touser)
        itchat.send(msg_send, toUserName='filehelper')  # 将撤回消息的通知以及细节发送到文件助手
        itchat.send('@%s@%s' % ('img' if old_msg['msg_type'] == 'Picture' else 'fil', "."+os.sep+"Revocation"+os.sep+ old_msg["msg_content"]), 'filehelper')
        #发送小视频，文件
        if(old_msg['msg_type'] == 'Attachment'):
            itchat.send_file("."+os.sep+"Revocation"+os.sep+ old_msg['msg_content'],'filehelper')
        if(old_msg['msg_type'] == 'Video'):
            itchat.send_video("."+os.sep+"Revocation"+os.sep+ old_msg["msg_content"],'filehelper')
        msg_dict.pop(msg_id)

if __name__ == '__main__':
    msg_dict = {}
    ClearTimeOutMsg()
    if not os.path.exists("."+os.sep+"Cache"+os.sep):
        os.mkdir("."+os.sep+"Cache"+os.sep)
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    itchat.run()
