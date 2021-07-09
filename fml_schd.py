import logging
import fml_schd_db as db
import fml_schd_parse as parse
import fml_schd_kbd as kb

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.deep_linking import decode_payload
from aiogram.types import Message

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, datetime, timedelta

import re
from fml_schd_const import TIME_REGEXP_LONG

import asyncio
import aioschedule as schedule

import os

from fml_schd_middleware import AccessMiddleware

from aiogram.dispatcher.handler import CancelHandler

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
if db.user_table():
    ROOT_ID = db.get_root_user_tid()
else:
    ROOT_ID = None

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)

# Use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Use middleware for user authorization
dp.middleware.setup(AccessMiddleware())

# scheduler run by "on_startup=" in executor.start_polling()============================================================


async def job_1m():
    # logging.info('schedule test')
    for i in db.get_notify_now():
        if not i.is_notify:
            await bot.send_message(i.user_id, f'Notify: {i.task_name} '
                                              f'{i.start_date.strftime("%H:%M")}-'
                                              f'{i.end_date.strftime("%H:%M")}')
            # await bot.send_message(i.user_id, '10', reply_markup=kb.notify_kbd)
            # # Set state
            # await Notify.wait.set()
            # state = Dispatcher.get_current().current_state()
            # await state.update_data(notify_task=i)
            db.set_task_state(i, 'Notified')
    for i in db.get_start_now():
        if i.state != 'InProgress':
            await bot.send_message(i.user_id, f'Start:  {i.task_name} '
                                              f'{i.start_date.strftime("%H:%M")}-'
                                              f'{i.end_date.strftime("%H:%M")}')
            db.set_task_state(i, 'InProgress')
    for i in db.get_end_now():
        if i.state == 'InProgress':
            await bot.send_message(i.user_id, f'Stop:  {i.task_name} '
                                              f'{i.start_date.strftime("%H:%M")}-'
                                              f'{i.end_date.strftime("%H:%M")}')
            db.set_task_state(i, 'Done')
            db.move_task_to_arch(i)


async def scheduler():
    schedule.every(1).minutes.do(job_1m)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(0.1)


async def on_startup(_):
    asyncio.create_task(scheduler())


# ======================================================================================================================


# States
class Go(StatesGroup):
    set_desc = State()  # Will be represented in storage as 'Go: set_desc'
    set_date = State()  # Will be represented in storage as 'Go: set_date'
    set_time = State()  # Will be represented in storage as 'Go: set_time'
    set_duration = State()  # Will be represented in storage as 'Go: set_duration'
    task = State()  # Will be represented in storage as 'Go: task'
    notify = State()  # Will be represented in storage as 'Go: notify'


class Ask(StatesGroup):
    ask_task = State()


class Join(StatesGroup):
    contact = State()


class Unjoin(StatesGroup):
    unjoin_yes_no = State()


class Rm(StatesGroup):
    rm_yes_no = State()


class Notify(StatesGroup):
    wait = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Family scheduler bot.\n\n"
                        "/join - join to bot service, and manage join requests\n"
                        "/user - list of active users\n\n"
                        "Create task examples:\n"
                        "/go 10 Lunch\n"
                        "/go at 11 gym\n"
                        "/go from 18 till 20:30 to cinema\n"
                        "/go tomorrow at 20 Party\n"
                        "/go 28-12-2021 at 11 gym\n"
                        "/go mon 8 to work\n"
                        "/go 27.07 from 18:23 till 20:30 to cinema\n"
                        "/go fr from 10 till 11 Lunch\n\n"
                        "/today - All users today task list\n"
                        "/todo - user today task list"
                        )


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Conversation cancelled! Try /help', reply_markup=types.ReplyKeyboardRemove())


# Notify Task

# @dp.callback_query_handler(lambda call: call.data in ["ok", "remind", "cancel"], state=Notify.wait)
# async def notify_callback(call: types.CallbackQuery, state: FSMContext):
#     await call.message.delete_reply_markup()
#     async with state.proxy() as data:
#         i = data['notify_task']
#
#     if str(call.data) == 'ok':
#         db.set_task_state(i, 'Notified')
#         await bot.send_message(call.from_user.id, 'Notified')
#         await call.answer()
#         await state.finish()
#     elif str(call.data) == 'cancel':
#         db.set_task_state(i, 'Notified')
#         await bot.send_message(call.from_user.id, f'Task cancelled!')
#         await call.answer(text="Task canceled!", show_alert=False)
#         await state.finish()
#     elif str(call.data) == 'remind':
#         await bot.send_message(call.from_user.id, f'Remind in 10 min!')
#         await call.answer(text="Remind in 10 min!", show_alert=False)
#         await state.finish()


# @dp.callback_query_handler(state=Notify.wait)
# async def inline_kb_notify_wait(call: types.CallbackQuery, state: FSMContext):
#     await asyncio.sleep(10)
#     count = 9
#     await bot.edit_message_text(str(count),
#                                     call.message.chat.id,
#                                     call.message.message_id)
#     # await asyncio.sleep(1)
#     # count -= 1


# /join -- Join to bot service and manage join requests
@dp.message_handler(commands=['join'])
async def join(message: types.Message):
    args = message.get_args()
    args_list = args.split()

    global ROOT_ID

    if not db.user_table():
        # First joined user will be a ROOT!!

        db.add_user(int(message.from_user.id), str(message.from_user.username), str(message.from_user.first_name),
                    str(message.from_user.last_name), admin=True)
        ROOT_ID = message.from_user.id
        await message.reply(f'Congrats, {str(message.from_user.username)}!\n\n'
                            f'Your ID {message.from_user.id} added to Family Schedule Bot as ROOT!')
    elif int(message.from_user.id) == ROOT_ID:
        # If ROOT ask /join
        if not db.req_table():
            await message.reply('No users waiting for join.\n')
        else:
            if args and args_list[0].isdigit() and db.req_exist(int(args_list[0])):
                db.req_to_user_move(int(args_list[0]))
                await message.reply(f'{int(args_list[0])} moved to User!')
                await bot.send_message(int(args_list[0]), 'Access granted! Welcome to Family!\n/help to command list.')
            else:
                res = ''
                for i in db.show_req():
                    res = res + f'{i.tid}, @{i.name}\n'
                await message.reply(f'Users waiting for join:\n{res}')

    else:
        if db.user_exist(int(message.from_user.id)):
            # Existing user sent /join
            await message.reply(f'User {message.from_user.username} already exist!')
        elif db.req_exist(int(message.from_user.id)):
            # User already sent request
            await message.reply(f'{str(message.from_user.first_name)} {str(message.from_user.last_name)} '
                                f'(tid={message.from_user.id}, username={message.from_user.username})'
                                f' already sent request.\nWait for authorization!')
        else:
            # New user sent request. Request contact for authorization.

            await message.answer('Press button to send your phone number!', reply_markup=kb.contact_request)
            # Set state
            await Join.contact.set()


@dp.message_handler(state=Join.contact)
async def handle_contact_invalid(message: types.Message):
    await message.reply('Press button "Send contact" at bottom of the screen to send your phone number!',
                        reply_markup=kb.contact_request)


@dp.message_handler(content_types=['contact'], state=Join.contact)
async def handle_contact(message: types.Message, state: FSMContext):
    if message.contact is not None:
        await message.answer(f'Your contact number is {str(message.contact.phone_number)}.\n'
                             f'Wait for authorization, please!', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(f'You not sent contact number.\n'
                             f'Wait for authorization, please!', reply_markup=types.ReplyKeyboardRemove())
    db.add_req(int(message.from_user.id), str(message.from_user.username), str(message.from_user.first_name),
               str(message.from_user.last_name), str(message.contact.phone_number))
    await bot.send_message(ROOT_ID,
                           f'{message.from_user.first_name} {message.from_user.last_name} '
                           f'(tid={int(message.from_user.id)}, username={str(message.from_user.username)},'
                           f' contact={str(message.contact.phone_number)})'
                           f' want to join.\n  ')
    await state.finish()


# /go processing START =================================================================================================
# /go -- Create task
#
# /task|go [<day>] <time> <Task description>
# or /task|go without args for interactive mode

@dp.message_handler(commands=['task', 'go'])
async def task(message: types.Message, state: FSMContext):
    args = message.get_args()
    if args:
        add_task = parse.go(args)
        if not add_task[0] or not add_task[1] or not add_task[2]:
            await message.reply("Can't parse task string.\nRead /help or use /go for interactive mode.")
            raise CancelHandler()
        async with state.proxy() as data:
            data['task'] = add_task
        await message.answer(f"Your task:\n\nStart: {data['task'][0]}\nEnd: {data['task'][1]}\nTask: {data['task'][2]}",
                             reply_markup=kb.inline_yes_no_kbd)
        # Set state
        await Go.task.set()
    else:
        await message.answer("Your can use line mode to create task:\n"
                             "/go [<day>] <time> <Task description>\n"
                             "For example:\n\n"
                             "/go 10 Lunch\n"
                             "/go 28-12-2021 at 11 gym\n"
                             "/go from 18 till 20:30 to cinema\n"
                             "/go tomorrow at 20 Party\n"
                             "/go mon 8 to work\n"
                             "/go 27.07 from 18:23 till 20:30 to cinema\n"
                             "/go fr from 10 till 11 Lunch\n\n"
                             "/cancel and use line mode or \n\n"
                             "===\n"
                             "Enter new task description:")
        # Set state
        await Go.set_desc.set()


# state: Go.set_desc


@dp.message_handler(state=Go.set_desc)
async def process_calendar(message: types.Message, state: FSMContext):
    await state.update_data(set_desc=message.text)
    calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
    await message.answer("Set task start:")
    await bot.send_message(message.chat.id,
                           f"Select {LSTEP[step]}",
                           reply_markup=calendar)
    # Set state
    await Go.set_date.set()


# state: Go.set_date


@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=Go.set_date)
async def inline_kb_calculator_callback_handler(call: types.CallbackQuery, state: FSMContext):
    result, key, step = DetailedTelegramCalendar(min_date=date.today()).process(call.data)

    if not result and key:
        await bot.edit_message_text(f"Select {LSTEP[step]}",
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=key)
    elif result:
        await bot.edit_message_text(f"Task start: {result}\n\nSet start time, (HH:MM):",
                                    call.message.chat.id,
                                    call.message.message_id)
        async with state.proxy() as data:
            data['set_date'] = result
        # Set state
        await Go.next()


# state: Go.set_time


# Time must looks like HH:MM
@dp.message_handler(lambda message: not re.match(TIME_REGEXP_LONG, message.text), state=Go.set_time)
async def process_set_time_invalid(message: types.Message):
    """
       If time format is invalid
    """
    await message.reply("Incorrect value!\nSet start time, (HH:MM):")


@dp.message_handler(state=Go.set_time)
async def process_set_time(message: types.Message, state: FSMContext):
    """
    Set start time
    """
    await state.update_data(set_time=str(message.text))
    await Go.next()
    await message.answer("Set duration, (min):")


# state: Go.set_duration


# Check Duration. Duration gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Go.set_duration)
async def process_notify_invalid(message: types.Message):
    """
    If duration is invalid
    """
    return await message.reply("Incorrect value!\nSet duration, (min): (digits only)")


@dp.message_handler(state=Go.set_duration)
async def process_set_duration(message: types.Message, state: FSMContext):
    """
    Set Duration
    """
    await state.update_data(set_duration=int(message.text))
    await Go.next()
    async with state.proxy() as data:
        start_str = f"{data['set_date']} {data['set_time']}"
        start_datetime = datetime.strptime(start_str, '%Y-%m-%d %H:%M')
        stop_datetime = start_datetime + timedelta(minutes=int(data['set_duration']))
        # data['task'] = f"Your task:\n\nStart: {start_datetime}\nEnd: {stop_datetime}\nTask: "
        data['task'] = (start_datetime, stop_datetime, data['set_desc'])
        await bot.send_message(message.from_user.id,
                               f"Your task:\n\nStart: {data['task'][0]}\n"
                               f"End: {data['task'][1]}\n"
                               f"Task: {data['task'][2]}",
                               reply_markup=kb.inline_yes_no_kbd)


# state: Go.task


@dp.callback_query_handler(lambda call: call.data in ["yes", "no"], state=Go.task)
async def process_callback_task(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    if str(call.data) == 'yes':
        await Go.next()
        await bot.send_message(call.from_user.id, f'Do you want set default notification for this task to 1 hour?',
                               reply_markup=kb.inline_notify_kbd)
        await call.answer()
    elif str(call.data) == 'no':
        await bot.send_message(call.from_user.id, f'Task cancelled!')
        await call.answer(text="Task canceled!", show_alert=False)
        # Finish conversation
        await state.finish()


@dp.message_handler(state=Go.task)
async def process_yes_no_invalid(message: types.Message):
    """
    In this check answer has to be one of: yes or no.
    """
    return await message.reply("Choose 'yes' or 'no' from the keyboard.")


# state: Go.notify

@dp.callback_query_handler(state=Go.notify)
async def process_callback_notify(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    if str(call.data) == 'default':
        async with state.proxy() as data:
            data['notify'] = data['task'][0] - timedelta(minutes=60)
            await bot.send_message(call.from_user.id,
                                   f"Task: {data['task'][2]}\n\nStart: {data['task'][0]}\nEnd: {data['task'][1]}\n"
                                   f"\nNotify at: {data['notify']}")
            # Finish conversation
            await state.finish()
            await call.answer(text="Task created!", show_alert=False)

            # PLACE TO SAVE TASK TO DB !!!!
            db.add_task(data['task'][2], call.from_user.id, start_date=data['task'][0], end_date=data['task'][1],
                        notify_at=data['notify'])

            await bot.send_message(call.from_user.id, "Task added to DB!")

    elif str(call.data) == 'custom':
        await bot.send_message(call.from_user.id, f'Set custom notify:')
        await call.answer()


# Check Notify. Notify gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Go.notify)
async def process_notify_invalid(message: types.Message):
    """
    If notify is invalid
    """
    return await message.reply("Notify gotta be a number.\nSet custom notify: (digits only)")


@dp.message_handler(lambda message: message.text.isdigit(), state=Go.notify)
async def process_custom_notify(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['notify'] = data['task'][0] - timedelta(minutes=int(message.text))
        await bot.send_message(message.from_user.id,
                               f"Task: {data['task'][2]}\n\nStart: {data['task'][0]}\nEnd: {data['task'][1]}\n"
                               f"\nNotify at: {data['notify']}")
        # Finish conversation
        await state.finish()

        # PLACE TO SAVE TASK TO DB !!!!
        db.add_task(data['task'][2], message.from_user.id, start_date=data['task'][0], end_date=data['task'][1],
                    notify_at=data['notify'])

        await message.answer('Task added to DB!')


# /go processing FINISH ==============================================================================================

# Ask processing START =============================================================================================

@dp.message_handler(commands=['ask'])
async def ask(message: types.Message, state: FSMContext):
    """
    Ask family to accept some task
    On the way ...
    """
    args = message.get_args()
    if args:
        add_task = parse.go(args)
        if not add_task[0] or not add_task[1] or not add_task[2]:
            await message.reply("Can't parse task string.\nRead /help or use /go for interactive mode.")
            raise CancelHandler()
        async with state.proxy() as data:
            data['ask_task'] = add_task
        await message.answer(f"Do you want ask family to accept this task?\n\n"
                             f"Start: {data['ask_task'][0]}\n"
                             f"End: {data['ask_task'][1]}\n"
                             f"Task: {data['ask_task'][2]}")

        await message.answer(f"Wait 60",
                             reply_markup=kb.inline_yes_no_kbd)
        # Set state
        await Ask.ask_task.set()
    else:
        await message.answer("Use line mode to create task!")

# state: Ask.task


@dp.callback_query_handler(lambda call: call.data in ["yes", "no"], state=Ask.ask_task)
async def process_callback_ask_task(call: types.CallbackQuery, state: FSMContext):
    if str(call.data) == 'yes':
        # await Ask.next()
        count = 9
        await asyncio.sleep(1)
        while count:
            await bot.edit_message_text(f"Wait {count}",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=kb.inline_yes_no_kbd)
            await asyncio.sleep(1)
            count -= 1
        await bot.edit_message_text(f'Wait 0\nTask cancelled!',
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=kb.inline_yes_no_kbd)
        await call.answer(text="Task canceled!", show_alert=False)
        await call.message.delete_reply_markup()
        # Finish conversation
        await state.finish()
    elif str(call.data) == 'no':
        await bot.send_message(call.from_user.id, f'Task cancelled!')
        await call.answer(text="Task canceled!", show_alert=False)
        await call.message.delete_reply_markup()
        # Finish conversation
        await state.finish()


@dp.message_handler(state=Ask.ask_task)
async def process_ask_task_yes_no_invalid(message: types.Message):
    """
    In this check answer has to be one of: yes or no.
    """
    return await message.reply("Choose 'yes' or 'no' from the keyboard.")


# Ask processing FINISH =============================================================================================


@dp.message_handler(commands=['user'])
async def user(message: types.Message):
    """
    Show users list
    """
    res = ''
    for usr in db.show_users():
        res = res + f'{usr.firstname} {usr.lastname} ({usr.tid}, {usr.phone_number})\n'
    await message.answer(res)


@dp.message_handler(commands=['todo'])
async def todo(message: types.Message):
    """
    Show user today task
    """
    res = ''
    for tsk in db.get_task_at_date(message.from_user.id, date.today()):
        res = res + f'/rm{tsk.id} {tsk.start_date.strftime("%H:%M")} {tsk.end_date.strftime("%H:%M")} {tsk.task_name}\n'
    if res:
        await message.reply(res)
    else:
        await message.reply('There is no task for today!')


@dp.message_handler(commands=['today'])
async def today(message: types.Message):
    """
    Show all users today tasks
    """
    res = f'Today {date.today()}\n'
    for usr in db.show_users():
        res = res + f'\n{usr.firstname} {usr.lastname} ({usr.tid}, {usr.phone_number}):\n'
        for tsk in db.get_task_at_date(usr.tid, date.today()):
            res = res + f'{tsk.start_date.strftime("%H:%M")} {tsk.end_date.strftime("%H:%M")} {tsk.task_name}\n'
    if res:
        await message.reply(res)
    else:
        await message.reply('There is no task for today!')


@dp.message_handler(lambda message: re.match("^/rm", message.text))
async def rm(message: types.Message):
    """
    Remove task by ID
    To prevent abuse db.get_task_by_id accept user ID and task ID,
    so users can remove only own task!!
    """
    tsk = db.get_task_by_id(int(message.from_user), int(str(message.text).removeprefix('/rm')))
    if tsk:
        db.set_task_state(tsk, "Canceled")
        db.move_task_to_arch(tsk)
        await message.reply(f'{tsk.start_date.strftime("%H:%M")} '
                            f'{tsk.end_date.strftime("%H:%M")} '
                            f'{tsk.task_name}\nTask canceled!')
    else:
        await message.reply("Can't delete task!")


@dp.message_handler(commands=['every'])
async def every(message: types.Message):
    """
    Set regular task
    On the way ...
    """
    pass

# /unjoin START =====================================================================================================


@dp.message_handler(commands=['unjoin'])
async def unjoin(message: types.Message):
    """
    Unjoin from bot service
    """
    if int(message.from_user) != ROOT_ID:
        await message.reply("Do you really want to delete all tasks and un join from service?",
                            reply_markup=kb.inline_yes_no_kbd)
        await State.set(Unjoin.unjoin_yes_no)
    else:
        await message.reply("ROOT can't unjoin yet. Stay strong, die hard!")


@dp.callback_query_handler(lambda call: call.data in ["yes", "no"], state=Unjoin.unjoin_yes_no)
async def process_callback_unjoin(call: types.CallbackQuery, state: FSMContext):
    if str(call.data) == 'yes':
        await bot.send_message(call.from_user.id, f'User un joined, tasks deleted! Bye!')
        db.rm_user_tasks(int(call.from_user))
        db.rm_user(int(call.from_user))
        await call.answer(text="Bye!", show_alert=False)
        await call.message.delete_reply_markup()
        # Finish conversation
        await state.finish()
    elif str(call.data) == 'no':
        await bot.send_message(call.from_user.id, f'Unjoin cancelled!')
        await call.answer(text="Unjoin canceled!", show_alert=False)
        await call.message.delete_reply_markup()
        # Finish conversation
        await state.finish()


@dp.message_handler(state=Unjoin.unjoin_yes_no)
async def process_unjoin_yes_no_invalid(message: types.Message):
    """
    In this check answer has to be one of: yes or no.
    """
    return await message.reply("Choose 'yes' or 'no' from the keyboard.")

# /unjoin FINISH ====================================================================================================

@dp.message_handler()
async def last_resort(message: types.Message):
    await message.reply("Sorry, I don't understand. Try /help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
