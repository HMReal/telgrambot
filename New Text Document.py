from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging

TOKEN = "7682122720:AAGEkmtsl4uyjNMs_2ECK-QETGxjeiSe3Tw"  # توکن ربات تلگرام
ADMIN_ID = 123456789  # آی‌دی عددی تلگرام خودت برای تایید پرداخت‌ها
CARD_NUMBER = "6037-9981-4052-2862"  # شماره کارت دریافت پول

# لینک‌های سابسکرایب برای پلن‌های مختلف
VPN_LINKS = {
    "1month": "https://yourvpn.com/1month",
    "3months": "https://yourvpn.com/3months",
    "100gb": "https://yourvpn.com/100gb"
}

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# دکمه‌های منو
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("💰 خرید اکانت"))
menu.add(KeyboardButton("📞 پشتیبانی"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("سلام! به ربات فروش فیلترشکن خوش اومدی! 👋\nبرای خرید اکانت دکمه زیر رو بزن!", reply_markup=menu)

@dp.message_handler(lambda message: message.text == "💰 خرید اکانت")
async def buy_vpn(message: types.Message):
    plans = "💎 **پلن‌های ما:**\n\n🔹 ۱ ماهه نامحدود: 100,000 تومان (کد: 1month)\n🔹 ۳ ماهه نامحدود: 250,000 تومان (کد: 3months)\n🔹 ۱۰۰ گیگ حجمی: 50,000 تومان (کد: 100gb)\n\n💳 **شماره کارت برای پرداخت:**\n`{}`\n\n📤 بعد از واریز، اسکرین‌شات رسید + کد پلن موردنظر رو بفرست!".format(CARD_NUMBER)
    await message.answer(plans, parse_mode="Markdown")

@dp.message_handler(content_types=['photo'])
async def handle_receipt(message: types.Message):
    if message.caption and message.caption.strip() in VPN_LINKS:
        plan_code = message.caption.strip()
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"💰 رسید پرداخت از: @{message.from_user.username} ({message.from_user.id})\n🔹 پلن انتخابی: {plan_code}")
        await message.answer("✅ رسید شما دریافت شد، پس از تایید، اطلاعات اکانت برات ارسال می‌شه!")
        # ذخیره اطلاعات برای ارسال بعد از تایید
        user_data[message.from_user.id] = plan_code
    else:
        await message.answer("❌ لطفاً کد پلن رو هم در کپشن اسکرین‌شات بنویس!")

@dp.message_handler(lambda message: message.text == "📞 پشتیبانی")
async def support(message: types.Message):
    await message.answer("🔹 برای پشتیبانی به ادمین پیام بدید: @YourAdminUsername")

# ادمین بعد از تایید، با این دستور می‌تونه اکانت رو بفرسته
@dp.message_handler(commands=['confirm'])
async def confirm_payment(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ فرمت اشتباه!\nدرست وارد کنید: `/confirm user_id`", parse_mode="Markdown")
            return
        user_id = int(args[1])
        if user_id in user_data:
            plan_code = user_data[user_id]
            sub_link = VPN_LINKS.get(plan_code, "لینک نامعتبر!")
            await bot.send_message(user_id, f"✅ پرداخت شما تایید شد!\n📡 لینک اتصال شما: `{sub_link}`", parse_mode="Markdown")
            await message.answer("🚀 اطلاعات اکانت برای کاربر ارسال شد!")
            del user_data[user_id]
        else:
            await message.answer("❌ اطلاعاتی برای این کاربر یافت نشد!")
    else:
        await message.answer("❌ شما دسترسی به این دستور ندارید!")

if __name__ == "__main__":
    user_data = {}  # ذخیره پرداخت‌ها برای تایید
    executor.start_polling(dp, skip_updates=True)
