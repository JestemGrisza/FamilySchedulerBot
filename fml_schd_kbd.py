from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

inline_btn_yes = InlineKeyboardButton('Yes', callback_data='yes')
inline_btn_no = InlineKeyboardButton('No', callback_data='no')
inline_yes_no_kbd = InlineKeyboardMarkup(row_width=2)
inline_yes_no_kbd.row(inline_btn_yes, inline_btn_no)

inline_notify_default = InlineKeyboardButton('Set default', callback_data='default')
inline_notify_custom = InlineKeyboardButton('Set custom', callback_data='custom')
inline_notify_kbd = InlineKeyboardMarkup(row_width=2)
inline_notify_kbd.row(inline_notify_default, inline_notify_custom)

# test kbd

btn_yes = KeyboardButton('/yes')
btn_no = KeyboardButton('/no')

yes_no_kbd = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
yes_no_kbd.row(btn_yes, btn_no)

# phone & location
contact_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Send contact ☎️', request_contact=True)
)