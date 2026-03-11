import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- AYARLAR ---
API_TOKEN = '8753313319:AAFe10Xqo2cXRXoklg_-qSx36VZnRV6kmP8'
ADMIN_ID = 8361787830

CHANNELS = [
    {"id": -1003759269337, "link": "https://t.me/+RkWr6UId-zhiYzUx"},
    {"id": -1003584016271, "link": "https://t.me/+KIyuo8WQrs42Njk9"},
    {"id": -1003871279471, "link": "https://t.me/+6osI9t8Qi9Y3Zjg1"},
    {"id": -1003840204007, "link": "https://t.me/leaugeguvence"}
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- VERİTABANI ---
conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

async def check_all_subs(user_id):
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if m.status in ['left', 'kicked']: return False
        except: return False
    return True

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    if not await check_all_subs(message.from_user.id):
        kb = InlineKeyboardMarkup(row_width=1)
        for i, ch in enumerate(CHANNELS, 1):
            kb.add(InlineKeyboardButton(text=f"📢 {i}. Kanala Katıl", url=ch["link"]))
        kb.add(InlineKeyboardButton(text="✅ Katıldım", callback_data="check"))
        await message.answer("⚠️ **Erişim Kısıtlı!**\n\nPanel için 4 kanala da katılmalısın.", reply_markup=kb)
    else:
        await message.answer("✅ **Erişim Onaylandı.**\nSorgu için veri girin:")

@dp.callback_query_handler(text="check")
async def check(call: types.CallbackQuery):
    if await check_all_subs(call.from_user.id):
        await call.answer("Onaylandı!", show_alert=True)
        await call.message.edit_text("🔍 **Sorgu Paneli Hazır.**\nVeri gönderin:")
    else:
        await call.answer("❌ Eksik kanal var!", show_alert=True)

@dp.message_handler(commands=['istatistik'], user_id=ADMIN_ID)
async def stats(message: types.Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    await message.reply(f"📊 Toplam Üye: {cursor.fetchone()[0]}")

@dp.message_handler()
async def f_handler(message: types.Message):
    if not await check_all_subs(message.from_user.id): return await start(message)
    w = await message.answer("🔄 **Sorgulanıyor...**")
    await asyncio.sleep(3)
    await w.edit_text("❌ **HATA:** Sunucu meşgul! Lütfen 10 dk sonra tekrar deneyin.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
      
