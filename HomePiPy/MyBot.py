import asyncio
import tgcrypto
import os

from telethon import TelegramClient

import requests
from telegram import InlineKeyboardButton, \
    InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, \
    MessageHandler, Filters

import config

whitelisted = []
waitingListed = []
blackListed = []
adminListed = []
waitingCounter = {}
statusDict = {}


def userControl(bot):

    global whitelisted
    global waitingListed
    global blackListed
    global adminListed

    if bot.effective_chat.id in whitelisted:
        return 1
    elif bot.effective_chat.id in blackListed:
        return 3
    elif bot.effective_chat.id in waitingListed:
        return 2
    elif bot.effective_chat.id in adminListed:
        return 4
    else:
        return 0


def cacheStatusDict():
    global statusDict
    statusDict.clear()
    statusDict = requests.get('http://localhost:9090/getAllStatus').json()


def cacheUserLists():
    global whitelisted
    global waitingListed
    global blackListed
    global adminListed

    whitelisted.clear()
    waitingListed.clear()
    blackListed.clear()
    adminListed.clear()

    users = requests.get('http://localhost:9090/allUsers').json()
    for serviceuser in users:
        if(serviceuser.get("status").get("id") == 1):
            whitelisted.append(serviceuser.get("id"))
        elif (serviceuser.get("status").get("id") == 2):
            waitingListed.append(serviceuser.get("id"))
        elif serviceuser.get("status").get("id") == 4:
            adminListed.append(serviceuser.get("id"))
        else:
            blackListed.append(serviceuser.get("id"))
    print(whitelisted)
    print(waitingListed)
    print(blackListed)
    print(adminListed)


def userstatuslist(bot, update):
    if bot.effective_chat.id in adminListed:
        allUsers = requests.get("http://localhost:9090/allUsers").json()

        for user in allUsers:
            keyboard = []
            row = []
            row.append(InlineKeyboardButton("WhiteList", callback_data="WhiteList;"+str(user.get("id"))))
            row.append(InlineKeyboardButton("WaitingList", callback_data="WaitingList;" +str(user.get("id"))))
            row.append(InlineKeyboardButton("BlackList", callback_data="BlackList;" +str(user.get("id"))))
            row.append(InlineKeyboardButton("Admin", callback_data="Admin;" + str(user.get("id"))))
            keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.bot.sendMessage(chat_id=config.MyChatId, text="id: " + str(user.get("id")) + " " + "firstName: " + user.get("firstname")+ " Status: " +user.get("status").get("status"),
                                       reply_markup=reply_markup)
    else:
        update.bot.sendMessage(chat_id=bot.effective_chat.id, text="This command is only for admins")


def start(bot, update):
    global whitelisted
    global blackListed
    global waitingListed
    global waitingCounter

    userStatus = userControl(bot)

    if userStatus == 1 or userStatus == 4:
        bot.message.reply_text("You are already registred :)")
    elif userStatus == 3:
        bot.message.reply_text("You are Blacklisted. Goodbye")
    elif userStatus == 2:
        counter = waitingCounter.get(bot.effective_chat.id)
        if counter == 2:
            statusdict = {"id": 3, "status": "Blacklist"}
            headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
            requests.put(url="http://localhost:9090/chageStatus/" + str(bot.effective_chat.id), json=statusdict,
                         headers=headers)
            bot.message.reply_text("You are Blacklisted. Goodbye")
            cacheUserLists()
        else:
            waitingCounter[bot.effective_chat.id] = counter+1
            bot.message.reply_text("Left trial : " + str(2-counter) +". After You will be Blacklisted")
    else:
        textToBeSent = "Personal id: " + str(bot.effective_chat.id) + "" + '\n' + "Full name : " + str(bot.effective_chat.full_name) + "" + '\n' + "Username : " + str(bot.effective_chat.username) + "" + '\n' + "Chat link : " + str(bot.effective_chat.link)
        bot.message.reply_text("You are now on waiting list.If you register 3 times you will be downgraded to black list and you will not get any answers from me." + '\n' +
                               "Your information is sent to Ozan to approve. Your information : " + '\n' + textToBeSent
                               )
        keyboard = [
            [
                InlineKeyboardButton("Approve", callback_data="Ozan_approve;"+str(bot.effective_chat.id)),
                InlineKeyboardButton("Decline", callback_data="Ozan_decline;"+str(bot.effective_chat.id)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        waitingListed.append(bot.effective_user.id)
        userDict = {
            "id" :  bot.effective_user.id,
            "firstname": str(bot.effective_user.first_name) if (hasattr(bot.effective_user, 'first_name')) else "",
            "lastname": str(bot.effective_user.last_name) if((hasattr(bot.effective_user, 'last_name') and bot.effective_user.last_name is not None)) else "",
            "username": str(bot.effective_user.username) if (hasattr(bot.effective_user, 'username')) else "",
            "isbot": bool(bot.effective_user.is_bot) if (hasattr(bot.effective_user, 'is_bot')) else "",
            "languagecode": str(bot.effective_user.language_code) if (hasattr(bot.effective_user, 'language_code')) else "",
            "status": {"id": 2}
        }
        header = {'Accept': '*/*', 'Content-Type': 'application/json', 'Content-Length': str(len(str(userDict)))}
        r = requests.post("http://localhost:9090/addAUser", headers=header, json=userDict)
        update.bot.sendMessage(chat_id=config.MyChatId, text="I want to join this telegram bot \n" + textToBeSent, reply_markup=reply_markup)
        waitingCounter[bot.effective_chat.id] = 0
        cacheUserLists()


def requestinfo(bot, update):
    global whitelisted
    global adminListed
    allUsers = requests.get("http://localhost:9090/allUsers").json()
    allUsers = [x for x in allUsers if (x.get("status").get("id") == 1 or x.get("status").get("id") == 4)] #and (x.get("id") != bot.effective_chat.id)]
    if bot.effective_chat.id in whitelisted or bot.effective_chat.id in adminListed:
        update.bot.sendMessage(chat_id=bot.effective_chat.id, text="You can request some information from approved users\nHere a list of them")
        for user in allUsers:
            keyboard = []
            row = []
            row.append(InlineKeyboardButton("Location", callback_data="Location_Information;" + str(user.get("id")) + ";" + str(bot.effective_chat.first_name) + ";" + str(bot.effective_chat.id)))
            row.append(InlineKeyboardButton("Contact Information", callback_data="Contact_Information;" + str(user.get("id")) + ";" + str(bot.effective_chat.first_name)  + ";" + str(bot.effective_chat.id)))
            keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.bot.sendMessage(chat_id=bot.effective_chat.id,
                                   text=user.get("firstname"),
                                   reply_markup=reply_markup)
    else:
        update.bot.sendMessage(chat_id=bot.effective_chat.id, text="You are not allowed to use this command")


def button(bot, update) -> None:
    query = bot.callback_query.data
    global statusDict
    datas = str(query).split(';')

    if "Ozan_approve" in query:
        status = statusDict[0]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1], text="Your request approved. You can use other commands")
        cacheUserLists()

    elif "Ozan_decline" in query:
        status = statusDict[2]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status,
                     headers=headers)
        update.bot.sendMessage(chat_id=datas[1], text="Your request rejected. You are Blacklisted")
        cacheUserLists()

    elif "WhiteList" in query:
        status = statusDict[0]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to WhiteListed")
        cacheUserLists()

    elif "WaitingList" in query:
        status = statusDict[1]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to WaitingListed")
        cacheUserLists()
    elif "BlackList" in query:
        status = statusDict[2]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to BlackListed")
        cacheUserLists()
    elif "Admin" in query:
        status = statusDict[3]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to Admin")
        cacheUserLists()

    elif "Location_Information" in query:
        keyboard = []
        row = []
        row.append(InlineKeyboardButton("Send Location", callback_data="LocationApprove;" + str(datas[1])  + ";" + str(datas[3])))
        row.append(InlineKeyboardButton("Cancel request", callback_data="CancelRequest;" + str(datas[1]) + ";" + str(datas[3])))
        keyboard.append(row)
        row = []
        row.append(InlineKeyboardButton("Block user for sending another Location Request", callback_data="LocationBlock;" + str(datas[1])))
        keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your Location information is requested by " + str(datas[2]),
                               reply_markup=reply_markup)

    elif "Contact_Information" in query:
        keyboard = []
        row = []
        row.append(InlineKeyboardButton("Send Contract", callback_data="ContractApprove;" + str(datas[1])))
        row.append(InlineKeyboardButton("Cancel request", callback_data="CancelRequest;" + str(datas[1]) + ";" + str(datas[3])))
        keyboard.append(row)
        row = []
        row.append(InlineKeyboardButton("Block user for sending another Contract Request", callback_data="ContractBlock;" + str(datas[1])))
        keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your Contract information is requested by " + str(datas[2]),
                               reply_markup=reply_markup)
    elif "CancelRequest" in query:
        update.bot.sendMessage(chat_id=datas[1],
                               text="Request Canceled")
        update.bot.sendMessage(chat_id=datas[2],
                               text="Your request canceled by the requested user")
    elif "LocationApprove" in query:
        keyboard = [[KeyboardButton(text="Approve Location Share", request_location=True),
                     KeyboardButton(text="Cancel Share", request_location=False)
                     ]]
        keyboardMarkup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.bot.sendMessage(chat_id=str(datas[1]), text="SharedLocationTo;" + datas[2], reply_markup=keyboardMarkup)





async def actual_work(api_id, api_hash):
    sem = asyncio.Semaphore(10)
    async with TelegramClient('session_name1', api_id, api_hash) as client:
        async with sem:
            async for message in client.iter_messages('@trialbotofmine1bot', limit=1):
                await asyncio.create_task(message.download_media())


def forwarededMessage(bot, update):
    api_id = config.DesktopApi_id
    api_hash = config.DesktopApi_hash

    userStatus = userControl(bot)
    if userStatus == 1 or userStatus == 2 or userStatus == 3:
        update.bot.sendMessage(chat_id=bot.effective_chat.id, text="Forward and Download feature only for Admins")
    elif userStatus == 4:
        actual_work(api_id, api_hash)

def locationshare(bot, update):
    datas = str(bot.message.reply_to_message.text).split(';')
    userStatus = userControl(bot)
    if userStatus == 1 or userStatus == 4:
        update.bot.forwardMessage(datas[1], bot.effective_chat.id, bot.message.message_id)
    else:
        pass

def main():
    updater = Updater(config.botToken)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('userstatuslist', userstatuslist))
    dp.add_handler(CommandHandler('requestinfo', requestinfo))
    dp.add_handler(MessageHandler(Filters.forwarded, forwarededMessage))
    dp.add_handler(MessageHandler(Filters.location, locationshare))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    users = requests.get('http://localhost:9090/allUsers').json()
    cacheUserLists()
    cacheStatusDict()
    main()
