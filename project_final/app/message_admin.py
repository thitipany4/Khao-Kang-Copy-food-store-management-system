from linebot import LineBotApi
from linebot.models import TextSendMessage
from .models import *
def message_to_admin(order):
    # Initialize LineBotApi with your Channel Access Token
    line_bot_api = LineBotApi('za3XvRtLy/0ddM6yPhbR7J76djPWSPSkSZa5i0TsN2GFYkgU5azYpdWqxOBo9vR39y7XLS+nKy4WfHxj+DoEoW3N0cR6Qmm85V09GTE3oyjMlf6Mw+oSXWWdFymdpF3/ZpZkIqWJ9AZoyLTTAKjWFwdB04t89/1O/w1cDnyilFU=')

    # User ID of the recipient
    user_id = 'U625b89db02391cb9cd0d8092c278a052'

    # Message to be sent
    message = TextSendMessage(text=f'คุณมีออเดอร์ เข้ามาใหม่ {order.ref_code}')

    # Send the message (messages argument should be a list)
    line_bot_api.push_message(user_id, messages=[message])

    print('Success: Message sent')

def message_cancel(order,user):
    line_bot_api = LineBotApi('za3XvRtLy/0ddM6yPhbR7J76djPWSPSkSZa5i0TsN2GFYkgU5azYpdWqxOBo9vR39y7XLS+nKy4WfHxj+DoEoW3N0cR6Qmm85V09GTE3oyjMlf6Mw+oSXWWdFymdpF3/ZpZkIqWJ9AZoyLTTAKjWFwdB04t89/1O/w1cDnyilFU=')
    member = Member.objects.get(user=user)
    print(member.line_id)
    message = TextSendMessage(text=f'ออเดอร์ {order.ref_code} ถูกยกเลิก โดยผู้ใช้งาน {member.user}')
    line_bot_api.push_message(member.line_id, messages=[message])

def message_confirmed(order,user):
    line_bot_api = LineBotApi('za3XvRtLy/0ddM6yPhbR7J76djPWSPSkSZa5i0TsN2GFYkgU5azYpdWqxOBo9vR39y7XLS+nKy4WfHxj+DoEoW3N0cR6Qmm85V09GTE3oyjMlf6Mw+oSXWWdFymdpF3/ZpZkIqWJ9AZoyLTTAKjWFwdB04t89/1O/w1cDnyilFU=')
    member = Member.objects.get(user=user)
    print(member.line_id)
    message = TextSendMessage(text=f'ออเดอร์ {order.ref_code} เวลานัดรับ {order.time_receive} ได้รับการยืนยันเเล้ว')
    line_bot_api.push_message(member.line_id, messages=[message])

     