from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from datetime import datetime

# اطلاعات ربات
TOKEN = '7820256456:AAGIAP_HMruFYMFbhQB8-_YLZqXbcwROUIs'
ADMIN_CHAT_ID = 7021453138

# مراحل مکالمه
SELECT_DAY, SELECT_TIME, GET_NAME, GET_PHONE = range(4)

# دکمه‌ها
main_menu = [['📸 رزرو وقت عکاسی'], ['🎓 ثبت‌نام در دوره آموزشی']]
back_button = [['🔙 بازگشت به منو']]

# روزهای کاری (جمعه تعطیل)
available_days = ['شنبه', 'یک‌شنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه']
available_hours = [f"{hour}:00" for hour in range(9, 21)]

# حافظه موقت نوبت‌های پر
busy_times = {day: [] for day in available_days}

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ورود به فرآیند رزرو
async def book_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days_keyboard = [[day] for day in available_days]
    await update.message.reply_text(
        "🗓 لطفاً یک روز برای رزرو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(days_keyboard + back_button, resize_keyboard=True)
    )
    return SELECT_DAY

# انتخاب روز
async def select_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = update.message.text
    if day == '🔙 بازگشت به منو':
        return await start(update, context)

    if day not in available_days:
        await update.message.reply_text("❗️روز نامعتبره. لطفاً از گزینه‌ها استفاده کن.")
        return SELECT_DAY

    context.user_data['selected_day'] = day
    reserved = busy_times.get(day, [])
    free_times = [h for h in available_hours if h not in reserved]

    if not free_times:
        await update.message.reply_text(
            "❌ همه‌ی نوبت‌های این روز پر شده.",
            reply_markup=ReplyKeyboardMarkup(back_button, resize_keyboard=True)
        )
        return SELECT_DAY

    keyboard = [[t] for t in free_times]
    await update.message.reply_text(
        f"⏰ ساعت‌های آزاد در {day}:",
        reply_markup=ReplyKeyboardMarkup(keyboard + back_button, resize_keyboard=True)
    )
    context.user_data['free_times'] = free_times
    return SELECT_TIME

# انتخاب ساعت
async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.message.text
    if time == '🔙 بازگشت به منو':
        return await start(update, context)

    free_times = context.user_data.get('free_times', [])
    if time not in free_times:
        await update.message.reply_text("❗️این ساعت در دسترس نیست. لطفاً از دکمه‌ها استفاده کن.")
        return SELECT_TIME

    context.user_data['selected_time'] = time
    await update.message.reply_text("👤 لطفاً نام و نام خانوادگی خودت رو وارد کن:")
    return GET_NAME

# گرفتن نام
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📞 حالا شماره تلفنت رو وارد کن:")
    return GET_PHONE

# گرفتن شماره تماس و ثبت نهایی
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text

    # ذخیره نوبت در حافظه
    day = context.user_data['selected_day']
    time = context.user_data['selected_time']
    busy_times[day].append(time)

    user = update.effective_user

    await update.message.reply_text("✅ وقتت رزرو شد! منتظر تماس ما باش.")

    msg = (
        f"📸 رزرو جدید عکاسی:\n\n"
        f"🗓 روز: {day}\n"
        f"⏰ ساعت: {time}\n"
        f"👤 نام: {context.user_data['name']}\n"
        f"📞 شماره: {context.user_data['phone']}\n"
        f"🆔 کاربر: {user.full_name} (@{user.username or 'نداره'})"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    return ConversationHandler.END

# اجرای برنامه
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    book_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📸 رزرو وقت عکاسی$'), book_session)],
        states={
            SELECT_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_day)],
            SELECT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_time)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت به منو$'), start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(book_conv)

    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()