#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

users = {}


def start(bot, update, job_queue):
    logging.info("Received start!")
    chat_id = update.message.chat_id
    users[chat_id] = {
        'name': update.message.from_user.first_name,
        'status': 'idle',
        'tasks': list(),
        'schedule': 12,
        'message_count': 0}
    job_queue.run_repeating(tasking, 120)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Welcome! Please *do* talk to me, _F E L L O W \_ H U M A N_")

def tasking():

    pass

def schedule(bot, update, args, job_queue, chat_data):
    try:
        hour = int(args[0])
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'll contact you every day at {0} to decide".format(hour))
    except (IndexError, ValueError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Usage /schedule <hour-of-day>")


def add_task(bot, update, args):
    try:
        if len(args) == 0:
            raise IndexError
        task = " ".join(args)
        user = users[update.message.chat_id]
        user['tasks'].append(task)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Added {}".format(task))
    except (IndexError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Usage /add <task>")


def decide(bot, update, job_queue, chat_data):
    try:
        job = job_queue
        
    except (IndexError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Usage /decide")


def echo(bot, update):
    try:
        logger.info("Received message!")
        chat_id = update.message.chat_id
        if chat_id is None:
            return
        user = users.get(chat_id)
        if user is None:
            users[chat_id] = user = {
                'name': update.message.from_user.first_name,
                'status': 'idle',
                'tasks': list(),
                'schedule': 12,
                'message_count': 0}
        if user.status == 'idle':
            user.status = 'talking'
            if message_count == 0:
                bot.send_message(
                    chat_id=chat_id,
                    text=u"Welcome {name}! I'm going to be your assistant".format(**users[chat_id]))
                bot.send_message(
                    chat_id=chat_id,
                    text=u"How can I help you today?".format(**user),
                    reply_markup=ReplyKeyboardMarkup(
                        [["Add task"], ["Nevermind"]]), one_time_keyboard=True)
            user.message_count += 1
            return
        elif user.status == 'talking':
            if update.message.text.lower() == "add tasks":
                user.status = 'adding_task'
                bot.send_message(
                    chat_id=chat_id,
                    text=u"Let's add a task. What are your plans?")
        elif user.status == 'adding_task':
            if update.message.text.strip().lower() == "stop":
                user.status = 'talking'
                bot.send_message(
                    chat_id=chat_id,
                    text=u"Fair enough. Now what?".format(),
                    reply_markup=ReplyKeyboardMarkup(
                        [["Add task"], ["Nevermind"]]), one_time_keyboard=True)
            else:
                user.tasks.append(update.message.text)
                bot.send_message(
                    chat_id=chat_id,
                    text=u"Done. To stop adding plans please say 'stop'")
    except Exception as exc:
        logger.error(exc)
        bot.send_message(chat_id=chat_id, text=u"Oops!")


updater = Updater(token='525296554:AAHE2mzjBwL58Tzz21pVQfL2h2T1aiyXbog')
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
task_handler = CommandHandler('add', add_task, pass_args=True)
schedule_handler = CommandHandler(
    'schedule', schedule, pass_args=True,
    pass_job_queue=True, pass_chat_data=True)
daily_handler = CommandHandler(
    'daily', decide, pass_job_queue=True, pass_chat_data=True)
echo_handler = MessageHandler(Filters.text, echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(task_handler)
dispatcher.add_handler(schedule_handler)
dispatcher.add_handler(daily_handler)
dispatcher.add_handler(echo_handler)

if __name__ == '__main__':
    logger.info("Starting app")
    updater.start_polling()
    # Block listening to signals to exit
    updater.idle()
    logger.info("Stopping app")
