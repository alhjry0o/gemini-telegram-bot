```markdown
# 🤖 بوت تيليجرام ذكي - Gemini 1.5 Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-1.5%20Pro-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**مساعد ذكي عربي متخصص في التعليم والبرمجة**

</div>

---

## ✨ المميزات

- 🧠 **ذكاء اصطناعي متقدم** — Gemini 1.5 Pro بنافذة سياق 2 مليون رمز
- 🎨 **متعدد الوسائط** — صور، PDF، فيديو، صوت
- 💾 **ذاكرة محادثة** — يتذكر السياق لكل مستخدم
- 📦 **مشاريع ZIP** — يولّد مشاريع كاملة تلقائيًا
- 👨‍💻 **لوحة إدارية** — حظر، إذاعة، قفل/فتح
- ✅ **اشتراك إجباري** — التحقق من عضوية القناة

---

## 🚀 التشغيل السريع

```bash
# 1. استنساخ المشروع
git clone https://github.com/USERNAME/gemini-telegram-bot.git
cd gemini-telegram-bot

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. إعداد البيئة
cp .env.example .env
nano .env    # املأ القيم الحقيقية

# 4. التشغيل
python bot.py
```

---

⚙️ متغيرات .env

المتغير الوصف
GEMINI_API_KEY مفتاح API من Google AI Studio
TELEGRAM_BOT_TOKEN توكن البوت من @BotFather
DEVELOPER_ID معرفك الرقمي من @userinfobot
DEVELOPER_NAME اسمك الظاهر في لوحة التحكم
DEVELOPER_TELEGRAM_URL رابط حسابك في تيليجرام
CHANNEL_TELEGRAM_URL رابط قناتك الرسمية
CHANNEL_ID معرف القناة (@username أو -100xxx) للتحقق من الاشتراك

---

🎮 الأوامر

الأمر الوصف
/start رسالة ترحيبية
/admin لوحة التحكم (للمطور)
/stats إحصائيات المستخدمين (للمطور)
أي رسالة محادثة مع الذكاء الاصطناعي

لوحة التحكم /admin:
👥 عدد المستخدمين · ⛔ الحظر · 🎙 الإذاعة · 👀 حالة البوت

---

🏗️ هيكل المشروع

```
├── bot.py              # نقطة الانطلاق
├── config/             # الإعدادات
├── core/               # منطق Gemini والملفات
├── handlers/           # معالجات الأوامر
├── services/           # الخدمات المساعدة
├── utils/              # الأدوات
├── data/               # البيانات (تُنشأ تلقائيًا)
└── logs/               # السجلات
```

---

⚠️ ملاحظات

· حدود Gemini المجانية: gemini-1.5-pro = 50 طلب/يوم. للحصول على حدود أعلى، غيّر الموديل في config/settings.py إلى gemini-1.5-flash.
· الاشتراك الإجباري: يجب أن يكون البوت مشرفًا في القناة.
· الأمان: لا ترفع ملف .env إلى GitHub أبدًا.

---

📜 الترخيص

MIT License — راجع LICENSE للتفاصيل.

---

<div align="center">

صُنع في اليمن 🇾🇪

</div>
```
