import asyncio
import logging

from telethon import TelegramClient

import requests
from telegram import InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, \
    MessageHandler, Filters

import config

whitelisted = []
waitingListed = []
blackListed = []
adminListed = []
waitingCounter = {}
statusDict = {}


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


def UserStatuslist(bot, update):
    if bot.effective_chat.id in adminListed:
        blockedUsersList = requests.get("http://localhost:9090/allUsers").json()

        for user in blockedUsersList:
            keyboard = []
            row = []
            row.append(InlineKeyboardButton("WhiteList", callback_data="WhiteList;"+str(user.get("id"))))
            row.append(InlineKeyboardButton("WaitingList", callback_data="WaitingList;" +str(user.get("id"))))
            row.append(InlineKeyboardButton("BlackList", callback_data="BlackList;" +str(user.get("id"))))
            row.append(InlineKeyboardButton("Admin", callback_data="Admin;" + str(user.get("id"))))
            keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            for admin in adminListed:
                update.bot.sendMessage(chat_id=admin, text="id: " + str(user.get("id")) + " " + "firstName: " + user.get("firstname")+ " Status: " +user.get("status").get("status"),
                                       reply_markup=reply_markup)


def start(bot, update):
    global whitelisted
    global blackListed
    global waitingListed
    global waitingCounter

    if bot.effective_chat.id in whitelisted:
        bot.message.reply_text("You are already registred :)")
    elif bot.effective_chat.id in blackListed:
        bot.message.reply_text("You are Blacklisted. Goodbye")
    elif bot.effective_chat.id in waitingListed:
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


def button(bot, update) -> None:
    query = bot.callback_query.data
    global statusDict
    datas = str(query).split(';')

    if "Ozan_approve" in query:
        status = statusDict[0]
        headers ={'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1], text="Your request approved. You can use other commands")

    elif "Ozan_decline" in query:
        status = statusDict[2]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status,
                     headers=headers)
        update.bot.sendMessage(chat_id=datas[1], text="Your request rejected. You are Blacklisted")

    elif "WhiteList" in query:
        status = statusDict[0]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to WhiteListed")

    elif "WaitingList" in query:
        status = statusDict[1]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to WaitingListed")
    elif "BlackList" in query:
        status = statusDict[2]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to BlackListed")
    elif "Admin" in query:
        status = statusDict[3]
        headers = {'Accept': '*/*', 'Content-Type': 'application/json'}
        requests.put(url="http://localhost:9090/chageStatus/" + datas[1], json=status, headers=headers)
        update.bot.sendMessage(chat_id=datas[1],
                               text="Your status changed to Admin")

    cacheUserLists()


async def actual_work():
    api_id = config.DesktopApi_id
    api_hash = config.DesktopApi_hash

    from telethon import TelegramClient
    async with TelegramClient('session_name1', api_id, api_hash) as client:
        async for message in client.iter_messages('@trialbotofmine1bot', limit=1):
            await message.download_media()


def echo(update, context):
    asyncio.run(actual_work())


def main():
    updater = Updater(config.botToken)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('UserStatuslist', UserStatuslist))
    dp.add_handler(MessageHandler(Filters.forwarded, echo))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    users = requests.get('http://localhost:9090/allUsers').json()
    cacheUserLists()
    cacheStatusDict()
    main()
