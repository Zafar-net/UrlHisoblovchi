import telebot
import re
from datetime import datetime

# Bot tokeningizni kiriting
API_TOKEN = '7630095458:AAFl77wJH_af_9qo4XtDTWEGUOVBYjwU6ro'

bot = telebot.TeleBot(API_TOKEN)

# Faqat bir ma'lum foydalanuvchi uchun (ID ni o'rnating)
TARGET_USER_ID = 7982588597

# TikTok URL'larni aniqlash uchun regex
tiktok_pattern = r"(https?://(www\.)?tiktok\.com/[^\s]+|https?://vt\.tiktok\.com/[^\s]+)"

# TikTok URL'larni saqlash
tiktok_urls = []
deleted_urls = set()

# delete_url.txt faylidan o'chirilgan URL'larni o'qish
def load_deleted_urls():
    try:
        with open("delete_url.txt", "r") as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()

# delete_url.txt fayliga yangi URL'larni qo'shish
def add_deleted_url(url):
    global deleted_urls
    deleted_urls = load_deleted_urls()  # Fayldagi mavjud URL'larni o'qish
    if url not in deleted_urls:  # URL takrorlanmasligini tekshirish
        with open("delete_url.txt", "a") as file:
            file.write(url + "\n")
        deleted_urls.add(url)  # Yangi URL'ni to'plamga qo'shish
        print(f"O'chirilgan URL faylga qo'shildi: {url}")
        return True
    else:
        print(f"URL allaqachon faylda mavjud: {url}")
        return False

# URL'larni faylga yozish
def save_urls_to_monthly_file():
    now = datetime.now()
    month_name = now.strftime("%Y_%m")
    filename = f"tiktok_urls_{month_name}.txt"

    with open(filename, "w") as file:
        file.write("\n".join(tiktok_urls) + "\n")

    print(f"TikTok URL'lar {filename} fayliga yozildi.")

# Guruhdan TikTok URL'larni qayta ishlash
@bot.message_handler(func=lambda message: message.chat.type in ["group", "supergroup"])
def handle_group_messages(message):
    global deleted_urls
    if message.from_user.id != TARGET_USER_ID:
        return

    text = message.text or message.caption
    if not text:
        return

    # TikTok URL'ni tekshirish
    urls = re.findall(tiktok_pattern, text)
    if urls:
        tiktok_urls.extend([url[0] for url in urls])  # TikTok URL'larni saqlash
        deleted_urls = load_deleted_urls()  # O'chirilgan URL'larni yangilash

        # Javob tayyorlash
        total_urls = len(tiktok_urls)
        deleted_count = sum(1 for url in tiktok_urls if url in deleted_urls)

        response_message = (
            f"TikTok yo'nalishi qabul qildi!\n\n"
            f"Oy davomida tashlangan TikTok URL'lar soni: {total_urls}ta\n\n"
            f"O'chirilgan URL'lar soni: {deleted_count}ta"
        )

        bot.reply_to(message, response_message)
        print(f"TikTok URL qabul qilindi: {urls}")

        # Har oy uchun URL'larni faylga yozish
        save_urls_to_monthly_file()

# Botga o'chirilgan URL yuborilganda
@bot.message_handler(func=lambda message: True)
def handle_deleted_url(message):
    global deleted_urls
    if message.from_user.id != TARGET_USER_ID:
        return

    text = message.text
    if not text:
        return

    # O'chirilgan URL'ni aniqlash
    if re.match(tiktok_pattern, text):
        is_added = add_deleted_url(text)  # URL'ni faylga qo'shish
        deleted_urls = load_deleted_urls()  # Yangilash

        if is_added:
            bot.reply_to(message, f"O'chirilgan URL qo'shildi: {text}")
        else:
            bot.reply_to(message, f"Bu URL allaqachon o'chirilgan: {text}")
    else:
        bot.reply_to(message, "Xato: Iltimos, faqat TikTok URL yuboring!")

print("Bot ishga tushdi...")
bot.infinity_polling()
