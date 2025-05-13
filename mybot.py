from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

TOKEN = '7820256456:AAGIAP_HMruFYMFbhQB8-_YLZqXbcwROUIs'
ADMIN_CHAT_ID = 7021453138

# مراحل فرم ثبت‌نام
NAME, PHONE, INSTAGRAM = range(3)

# دکمه‌های منو
main_menu = [['🎓 ثبت‌نام در دوره آموزشی']]
back_button = [['🔙 بازگشت به منو']]

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! از منوی زیر یکی رو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# شروع ثبت‌نام
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 لطفاً نام و نام خانوادگی خودت رو وارد کن:",
        reply_markup=ReplyKeyboardMarkup(back_button, resize_keyboard=True)
    )
    return NAME

# گرفتن نام
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 بازگشت به منو':
        return await start(update, context)
    
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📞 لطفاً شماره تلفنت رو وارد کن:")
    return PHONE

# گرفتن شماره
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 بازگشت به منو':
        return await start(update, context)
    
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("📷 لطفاً آیدی اینستاگرامت رو وارد کن (مثلاً @myprofile):")
    return INSTAGRAM

# گرفتن اینستاگرام و ارسال اطلاعات به ادمین
async def get_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 بازگشت به منو':
        return await start(update, context)
    
    context.user_data['instagram'] = update.message.text
    user = update.effective_user

    # پیام نهایی برای کاربر
    await update.message.reply_text("✅ ثبت‌نامت انجام شد! به زودی باهات تماس می‌گیریم.")

    # ارسال به پی‌وی ادمین
    msg = f"""📥 فرم ثبت‌نام جدید:

👤 نام: {context.user_data['name']}
📞 تلفن: {context.user_data['phone']}
📷 اینستاگرام: {context.user_data['instagram']}

ارسال شده توسط: {user.full_name} (@{user.username or 'نداره'})"""
    
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    return ConversationHandler.END

# تابع اصلی
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # فرم ثبت‌نام
    register_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🎓 ثبت‌نام در دوره آموزشی$'), register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            INSTAGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_instagram)],
        },
        fallbacks=[MessageHandler(filters.Regex('^🔙 بازگشت به منو$'), start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(register_conv)

    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
