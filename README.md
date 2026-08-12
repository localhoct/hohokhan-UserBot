# HoHoKhan UserBot

بازنویسی ماژولار HoHoKhan به‌صورت Telegram **Userbot** با Pyrogram 2 و Python 3.11.
نسخه قدیمی تک‌فایلی، APIهای ازکارافتاده، dependencyهای بدون استفاده و credentialهای
هاردکدشده حذف شده‌اند.

> این پروژه Bot Token محور نیست و روی حساب کاربری تلگرام اجرا می‌شود. استفاده از
> Userbot ممکن است با قوانین تلگرام یا سرویس‌های دانلودشده تعارض داشته باشد؛ مسئولیت
> رعایت قوانین، حق نشر و شرایط سرویس‌ها با اجراکننده است.

## قابلیت‌ها

- دانلود صوت از YouTube با جست‌وجوی نام آهنگ یا لینک
- جست‌وجوی YouTube و دانلود ویدیو از YouTube، Instagram، TikTok، X/Twitter، Likee
  و Radio Javan با `yt-dlp`
- سقف قابل‌تنظیم برای حجم، مدت و تعداد دانلود هم‌زمان
- جست‌وجوی ویکی‌پدیای فارسی و نمایش آب‌وهوا با کلید اختیاری OpenWeather
- ساخت/خواندن QR، OCR فارسی و انگلیسی، تبدیل عکس و استیکر ثابت
- Hash، رمز تصادفی امن، ROT13، Base64 و محاسبه subnet
- تبدیل hostname موجود در دستور `remote` فایل OpenVPN به IP عمومی
- اطلاعات کاربر، ping و اطلاعات سیستم
- پاسخ‌های خودکار پایدار با SQLite
- مدیریت گروه: حذف، kick، mute، unmute، add، join، leave، tag و قفل/بازکردن گروه
- block/unblock با محدودکردن دستورات حساس به مالک یا شناسه‌های مجاز
- rate limit، پاک‌سازی خودکار فایل موقت و لاگ خطای بدون افشای جزئیات به کاربر

قابلیت‌های قدیمی پرخطر یا غیرقابل‌اتکا مانند SMS bomber، shell/eval از راه دور،
profile cloning، proxy scraping، endpointهای ناشناس محتوای بزرگسال و APIهای خاموش
عمداً به نسخه جدید منتقل نشده‌اند.

## پیش‌نیازها

- Telegram `API_ID` و `API_HASH` از [my.telegram.org/apps](https://my.telegram.org/apps)
- شناسه عددی حساب مالک
- Python 3.11، Node.js 24 و `ffmpeg`، `tesseract` و `libzbar` برای نصب مستقیم
- Docker یا Incus برای روش‌های کانتینری

Pyrogram رسمی از سال 2023 نسخه جدیدی منتشر نکرده و آخرین نسخه رسمی آن `2.0.106` است؛
برای بازتولیدپذیری همین نسخه pin شده است. دانلودر روی `yt-dlp 2026.7.4` قرار دارد و
برای پشتیبانی کامل YouTube از `yt-dlp-ejs` و Node.js 24 استفاده می‌کند.

## تنظیمات

```bash
cp .env.example .env
```

این مقدارها را در `.env` تکمیل کنید:

| متغیر | لازم | توضیح |
|---|---:|---|
| `API_ID` / `API_HASH` | بله | credential برنامه تلگرام |
| `OWNER_ID` | بله | شناسه عددی مالک |
| `SESSION_STRING` | برای Docker | سشن Pyrogram؛ محرمانه |
| `SUDO_USER_IDS` | خیر | شناسه‌های مجاز با ویرگول |
| `OPENWEATHER_API_KEY` | خیر | فعال‌سازی آب‌وهوا |
| `MEDIA_ARCHIVE_CHAT_ID` | خیر | کپی دانلود موفق در چت مشخص |
| `YTDLP_COOKIES_FILE` | خیر | مسیر cookie برای محتوای نیازمند login |
| `MAX_DOWNLOAD_MB` | خیر | پیش‌فرض 150 MB |
| `MAX_MEDIA_DURATION_SECONDS` | خیر | پیش‌فرض 1800 ثانیه |

هرگز `.env`، `SESSION_STRING`، فایل `.session` یا cookie را Commit نکنید.

## اجرا با Docker Compose

ابتدا فایل تنظیمات را بسازید. برای تولید session string به شکل تعاملی:

```bash
cp .env.example .env
# API_ID و API_HASH را در .env وارد کنید
docker compose run --rm --no-deps hohokhan python -m scripts.generate_session
```

مقدار چاپ‌شده را داخل `.env` قرار دهید و سپس:

```bash
docker compose up -d --build
docker compose logs -f --tail=100
```

دیتابیس در `./data` نگهداری می‌شود؛ filesystem کانتینر read-only و `/tmp` از نوع
tmpfs است.

## نصب مستقیم

```bash
sudo apt update
sudo apt install -y ffmpeg libzbar0 tesseract-ocr tesseract-ocr-fas python3.11-venv
# Node.js باید نسخه 23.5 یا جدیدتر باشد (نسخه 24 پیشنهاد می‌شود).
node --version
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.generate_session
python -m hohokhan
```

در اجرای تعاملی می‌توانید `SESSION_STRING` را خالی بگذارید تا Pyrogram فایل session
را داخل `DATA_DIR` بسازد؛ آن فایل نیز محرمانه است.

## اجرا با Incus

فایل `deploy/incus/cloud-init.yaml` یک Debian 12 container را آماده، Docker را نصب و
مخزن Public را در `/opt/hohokhan/source` clone می‌کند:

```bash
incus init images:debian/12 hohokhan \
  -c security.nesting=true \
  -c cloud-init.user-data="$(cat deploy/incus/cloud-init.yaml)"
incus start hohokhan
incus exec hohokhan -- cloud-init status --wait
```

سپس تنظیمات را بدون ثبت در history به کانتینر منتقل کنید:

```bash
incus file push .env hohokhan/opt/hohokhan/source/.env --mode 600
incus exec hohokhan -- bash -lc \
  'cd /opt/hohokhan/source && docker-compose up -d --build'
incus exec hohokhan -- bash -lc \
  'cd /opt/hohokhan/source && docker-compose logs --tail=100'
```

## تست و بررسی

```bash
python -m compileall -q hohokhan scripts tests
python -m unittest discover -s tests -v
```

پیش از راه‌اندازی، نکات نگهداری credentialها و چرخش اسرار در
[`SECURITY.md`](SECURITY.md) را مطالعه کنید.

## ساختار پروژه

```text
hohokhan/
├── plugins/      # handlerهای Pyrogram
├── services/     # yt-dlp، Wikipedia، Weather و OpenVPN
├── utils/        # فایل، پیام و کاربر
├── app.py        # lifecycle کلاینت
├── config.py     # تنظیمات محیطی و validation
└── database.py   # SQLite async
```

## مجوز

این پروژه تحت مجوز [MIT](LICENSE) منتشر می‌شود.
