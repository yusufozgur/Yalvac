#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""

import secure_info
import rezbot_datetime_utils
import sessions_logic
from selenium_get_available_sessions import extract_available_sessions, Facilities

from datetime import datetime
import logging
from pprint import pprint

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, CallbackContext, PicklePersistence


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def follow(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    keyboard = [
            [
                InlineKeyboardButton("Pazartesi", callback_data="Monday"),
                InlineKeyboardButton("Salı", callback_data="Tuesday"),
            ],
            [
                
                InlineKeyboardButton("Çarşamba", callback_data="Wednesday"),
                InlineKeyboardButton("Perşembe", callback_data="Thursday"),
            ],
            [
                InlineKeyboardButton("Cuma", callback_data="Friday"),
            ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select day", reply_markup=reply_markup)


async def follow_day(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()# CallbackQueries need to be answered
        
    keyboard = [
            [
                InlineKeyboardButton("09:35", callback_data=f"follow{query.data} 09:35"),
                InlineKeyboardButton("12:00", callback_data=f"follow{query.data} 12:00"),
            ],
            [
                InlineKeyboardButton("14:00", callback_data=f"follow{query.data} 14:00"),
                InlineKeyboardButton("16:00", callback_data=f"follow{query.data} 16:00"),
            ],
            
            [
                InlineKeyboardButton("18:00", callback_data=f"follow{query.data} 18:00"),
                InlineKeyboardButton("19:35", callback_data=f"follow{query.data} 19:35"),
            ]
    ]
    await query.edit_message_text("Which session:", 
                                    reply_markup=InlineKeyboardMarkup(keyboard))


async def follow_time(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()# CallbackQueries need to be answered
    
    #remove the leading followw
    query.data = query.data.replace("follow","")
    
    selected_datetime = rezbot_datetime_utils.get_seans_datetime(query.data)
    
    
    sessions_logic.add_session_availability_request(
        query.message.chat_id,
        context.bot_data["session_requests"],
        selected_datetime
    )
    
    await query.edit_message_text(text=f"Following for availability in: {selected_datetime.strftime('%A %H:%M')}")

    
async def get_requests(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    await update.message.reply_text(str(context.bot_data.get("session_requests","no session requests")))

async def selenium_get_available_sessions(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    await update.message.reply_text(str(context.bot_data.get("available_sessions","no available sessions")))
    
async def following(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    sessions_followed = sessions_logic.get_following_sessions_for_chatid(
            update.message.chat_id,
            context.bot_data["session_requests"]
            )
    #convert it to nicely formatted strings
    sessions_followed = [session.strftime('%A %H:%M') for session in sessions_followed]
    await update.message.reply_text(
        str(sessions_followed).replace(",",",\n")
        )   
    
async def unfollow(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    sessions_followed = sessions_logic.get_following_sessions_for_chatid(
            update.message.chat_id,
            context.bot_data["session_requests"]
            )
    
    keyboard = []
    
    for session in sessions_followed:
        keyboard.append(
            [
                InlineKeyboardButton(session.isoformat(), callback_data="unfollow"+session.isoformat()),
            ]
        )
        
        await update.message.reply_text("Select one to unfollow", 
                                        reply_markup=InlineKeyboardMarkup(keyboard))
    pass

async def unfollow_callback(update: Update, context: CallbackContext.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()# CallbackQueries need to be answered
    
    #remove leading lable
    query.data = query.data.replace("unfollow","")
    
    session_to_unfollow = datetime.fromisoformat(query.data)
    
    sessions_logic.remove_session_availability_request(query.message.chat_id,
                                                       context.bot_data["session_requests"],
                                                       session_to_unfollow)
    
    await query.edit_message_text(text=f"Unfollowing the availability for {session_to_unfollow.strftime('%A %H:%M')}")
    
    pass
    
async def check_availability(context: CallbackContext.DEFAULT_TYPE):
    # Beep the person who called this alarm:
    #await context.bot.send_message(chat_id=context.job.chat_id, text=f'BEEP {context.job.data}!')
    available_sessions = extract_available_sessions(
        secure_info.username,
        secure_info.password,
        Facilities.gym,
        headless=False)
    
    print(available_sessions)
    
    session_requests = context.bot_data["session_requests"]
    
    
    for session in available_sessions:
        chats_requesting_this_session = session_requests.get(session,[])
        for chat_id in chats_requesting_this_session: 
            await context.bot.send_message(chat_id,
                                     text=f"{session.strftime('%A %H:%M')} is Available!")

    
    #save the available sessions for giving info when requested
    context.bot_data["available_sessions"] = available_sessions
    

    
    pass

def main() -> None:
    """Run the bot."""
    # Create
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(secure_info.token).build()
    
    #add session_requests, it will store user requests for following session availability
    
    #follow handlers
    application.add_handler(CommandHandler("follow", follow))
    application.add_handler(CallbackQueryHandler(follow_day, pattern="Monday$|Tuesday$|Wednesday$|Thursday$|Friday$"))
    application.add_handler(CallbackQueryHandler(follow_time, pattern="^follow.*\\d+:\\d+$"))
    
    #following sessions: let user query for which sessions they follow
    application.add_handler(CommandHandler("following", following))
    
    #unfollowing sessions
    application.add_handler(CommandHandler("unfollow", unfollow))
    application.add_handler(CallbackQueryHandler(unfollow_callback, pattern="unfollow"))
    
    
    #other
    application.add_handler(CommandHandler("get_requests", get_requests))
    application.add_handler(CommandHandler("get_available_sessions", selenium_get_available_sessions))

    #
    application.bot_data["session_requests"] = {datetime(2024, 3, 7, 12, 0): [1814009966]}

    #check availability of sessions every 5 minutes
    application.job_queue.run_repeating(check_availability, interval=5*60, first=1)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()