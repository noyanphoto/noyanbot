from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from datetime import time

# اطلاعات ربات
TOKEN = '7820256456:AAGIAP_HMruFYMFbhQB8-_YLZqXbcwROUIs'
ADMIN_CHAT_ID = 7021453138

# مراحل مکالمه
SELECT_DAY, SELECT_TIME = range(2)

# دکمه‌ها
main_menu = [['📸 رزرو وقت عکاسی'], ['🎓 ثبت‌نام در دوره آموزشی']]
back_button = [['🔙 بازگشت به منو']]

# روزهای کاری (جمعه حذف شده)
available_days = ['شنبه', 'یک‌شنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه']

# ساعت‌های کاری (۹ تا ۲۰)
available_hours = [f"{hour}:00" for hour in range(9, 21)]

# ذخیره نوبت‌های رزرو شده (به‌صورت موقتی در حافظه)
busy_times = {day: [] for day in available_days}

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# شروع رزرو وقت
async def book_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days_keyboard = [[day] for day in available_days]
    await update.message.reply_text(
        "🗓 لطفاً یک روز برای رزرو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(days_keyboard + back_button, resize_keyboard=True)
    )
    return SELECT_DAY

# انتخاب روز و نمایش ساعت‌های آزاد
async def select_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = update.message.text
    if day == '🔙 بازگشت به منو':
        return await start(update, context)

    if day not in available_days:
        await update.message.reply_text("❗️روز نامعتبره. لطفاً از دکمه‌ها استفاده کن.")
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

# انتخاب ساعت و ثبت رزرو
async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chosen_time = update.message.text
    if chosen_time == '🔙 بازگشت به منو':
        return await start(update, context)

    day = context.user_data.get('selected_day')
    free_times = context.user_data.get('free_times', [])

    if chosen_time not in free_times:
        await update.message.reply_text("❗️این ساعت در دسترس نیست. لطفاً از گزینه‌ها انتخاب کن.")
        return SELECT_TIME

    # ذخیره زمان رزرو
    busy_times[day].append(chosen_time)

    # ارسال پیام تأیید به کاربر
    await update.message.reply_text("✅ وقتت رزرو شد! منتظر تماس ما باش.")

    # ارسال پیام به ادمین
    user = update.effective_user
    msg = f"""📸 رزرو جدید عکاسی:

🗓 روز: {day}
⏰ ساعت: {chosen_time}
👤 کاربر: {user.full_name} (@{user.username or 'نداره'})"""
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    return ConversationHandler.END

# تابع اصلی
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # هندلر رزرو وقت عکاسی
    booking_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📸 رزرو وقت عکاسی$'), book_session)],
        states={
            SELECT_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_day)],
            SELECT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_time)],
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت به منو$'), start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(booking_conv)

    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
from keep_alive import keep_alive
keep_alive()
