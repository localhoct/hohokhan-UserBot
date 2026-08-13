# HoHoKhan UserBot

بازنویسی ماژولار HoHoKhan به‌صورت Telegram **Userbot** با API سازگار Pyrogram و
Python 3.11 تا 3.14.
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
- فال حافظ آفلاین از مجموعه داخلی ۴۹۵ غزل و تعبیر، همراه با صوت آرشیو تلگرام
- بازی‌های بومی تلگرام: تاس، دارت و بسکتبال
- ساخت/خواندن QR، OCR فارسی و انگلیسی، تبدیل عکس و استیکر ثابت
- Hash، رمز تصادفی امن، ROT13، Base64 و محاسبه subnet
- تبدیل hostname موجود در دستور `remote` فایل OpenVPN به IP عمومی
- اطلاعات کاربر، ping و اطلاعات سیستم
- وضعیت AFK پایدار با دلیل، مدت و پاسخ کنترل‌شده به منشن/پیام خصوصی
- ری‌اکشن خودکار قلب به تشکرهایی که خطاب به هوهوخان یا در پاسخ به پیام او هستند
- یادداشت‌های متنی پایدار با SQLite
- پاک‌سازی گروهی حداکثر ۱۰۰ پیام و ساخت نقل‌قول از پیام ریپلای‌شده
- نمایش شناسه‌ها، اطلاعات چت و فهرست مدیران گروه
- پاسخ‌های خودکار پایدار با SQLite
- مدیریت گروه: حذف، kick، mute، unmute، add، join، leave، tag و قفل/بازکردن گروه
- فرمان «هوهوخان بگو» برای پاسخ از طرف ربات، محدود به مدیران گروه
- block/unblock با محدودکردن دستورات حساس به مالک یا شناسه‌های مجاز
- rate limit، پاک‌سازی خودکار فایل موقت و لاگ خطای بدون افشای جزئیات به کاربر

قابلیت‌های قدیمی پرخطر یا غیرقابل‌اتکا مانند SMS bomber، shell/eval از راه دور،
profile cloning، proxy scraping، endpointهای ناشناس محتوای بزرگسال و APIهای خاموش
عمداً به نسخه جدید منتقل نشده‌اند.

## راهنمای داخل ربات

دستور `.help` فهرست بخش‌ها را نمایش می‌دهد. برای مشاهده یک بخش یا همه قابلیت‌ها:

```text
.help media
.help productivity
.help all
راهنما مدیریت
```

راهنمای داخلی تمام دستورات را همراه با سطح دسترسی، توضیح و مثال‌های لازم نمایش
می‌دهد و هم‌زمان با ماژول‌ها نگهداری می‌شود.

## پیش‌نیازها

- Telegram `API_ID` و `API_HASH` از [my.telegram.org/apps](https://my.telegram.org/apps)
- شناسه عددی حساب مالک
- Python 3.11 تا 3.14، Node.js 24 و `ffmpeg`، `tesseract` و `libzbar` برای نصب مستقیم
- Docker یا Incus برای روش‌های کانتینری

پروژه از `Kurigram 2.2.24`، فورک maintained و drop-in-compatible پایروگرام، استفاده
می‌کند؛ بنابراین importهای استاندارد `pyrogram` حفظ شده و Python 3.14 نیز پشتیبانی
می‌شود. دانلودر روی `yt-dlp 2026.7.4` قرار دارد و برای پشتیبانی کامل YouTube از
`yt-dlp-ejs` و Node.js 24 استفاده می‌کند.

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
| `YTDLP_COOKIES_FILE` | در IP محدودشده | مسیر فایل محرمانه `cookies.txt` برای YouTube |
| `YTDLP_SLEEP_INTERVAL_SECONDS` | خیر | فاصله تصادفی دانلود؛ پیش‌فرض ۵ تا ۱۰ ثانیه |
| `MAX_DOWNLOAD_MB` | خیر | پیش‌فرض 150 MB |
| `MAX_MEDIA_DURATION_SECONDS` | خیر | پیش‌فرض 1800 ثانیه |

هرگز `.env`، `SESSION_STRING`، فایل `.session` یا cookie را Commit نکنید.

### آرشیو صوتی حافظ

خوانش غزل‌ها در کانال [`@Hafez_Ghazals`](https://t.me/Hafez_Ghazals) با شناسه
`-1003967959794` نگهداری می‌شود. دستور «بخونش» پیام صوتی مرتبط را مستقیماً از این
کانال کپی می‌کند؛ بنابراین فایل صوتی روی سرور ربات نگهداری نمی‌شود.

برای بارگذاری اولیه تمام ۴۹۵ خوانش، حسابی که `SESSION_STRING` آن در `.env` است باید
در کانال اجازه ارسال پیام داشته باشد. سپس ربات اصلی را موقتاً متوقف و این دستور را
اجرا کنید:

```bash
python -m scripts.archive_hafez_audio
```

در Docker Compose:

```bash
docker compose stop hohokhan
docker compose run --rm --no-deps hohokhan python -m scripts.archive_hafez_audio
docker compose up -d
```

اسکریپت قبل از هر بارگذاری، تگ همان غزل را در کانال جست‌وجو می‌کند؛ بنابراین در
صورت قطع‌شدن می‌توان آن را دوباره اجرا کرد و فایل‌های قبلی تکرار نمی‌شوند. برای
ادامه از یک بازه مشخص نیز می‌توان از `--start 101 --end 495` استفاده کرد. هنگام
اجرا هر فایل فقط موقتاً دانلود می‌شود و بلافاصله پس از ارسال حذف خواهد شد.

متن کامل ۴۹۵ غزل و تعبیر آن‌ها داخل بسته پروژه قرار دارد و انتخاب فال در زمان اجرا
هیچ وابستگی‌ای به سایت خارجی ندارد. اینترنت فقط برای ارتباط با تلگرام و آرشیو صوتی
لازم است.

### رفع خطای ضدربات YouTube

پیام `Sign in to confirm you're not a bot` خرابی `yt-dlp` نیست؛ YouTube معمولاً
IP سرور را محدود کرده و به یک نشست معتبر نیاز دارد. برای حل آن یک فایل
`cookies.txt` با فرمت Netscape بسازید:

1. در کامپیوتر شخصی یک پنجره Incognito/Private تازه باز کنید، با ترجیحاً یک حساب
   جداگانه وارد YouTube شوید و در همان tab به
   [`youtube.com/robots.txt`](https://www.youtube.com/robots.txt) بروید.
2. فقط cookieهای دامنه YouTube را با یکی از روش‌های معرفی‌شده در
   [راهنمای رسمی yt-dlp](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)
   به فرمت Netscape صادر کنید؛ سپس پنجره خصوصی را ببندید و آن نشست را دوباره باز
   نکنید. YouTube cookie نشست‌های باز را مرتب عوض می‌کند.
3. فایل را خارج از Git و به‌شکل امن به پوشه `data` سرور منتقل کنید:

```bash
# روی سرور
mkdir -p ~/hohokhan-UserBot/data
chmod 700 ~/hohokhan-UserBot/data

# روی کامپیوتر شخصی؛ USER و SERVER را جایگزین کنید
scp youtube-cookies.txt USER@SERVER:~/hohokhan-UserBot/data/youtube-cookies.txt

# دوباره روی سرور؛ برای نصب مستقیم، مالک فایل باید همان کاربر اجراکننده باشد
cd ~/hohokhan-UserBot
chmod 600 data/youtube-cookies.txt
```

برای نصب مستقیم، مسیر واقعی سرور را در `.env` قرار دهید:

```dotenv
YTDLP_COOKIES_FILE=/root/hohokhan-UserBot/data/youtube-cookies.txt
```

برای Docker Compose یا Incus، پوشه `data` روی `/app/data` mount می‌شود:

```dotenv
YTDLP_COOKIES_FILE=/app/data/youtube-cookies.txt
```

image با کاربر محدود UID `10001` اجرا می‌شود؛ پیش از اجرای Docker مالکیت پوشه را
تنظیم کنید:

```bash
sudo chown -R 10001:10001 data
sudo chmod 600 data/youtube-cookies.txt
```

سپس ربات را restart کنید. اگر پیام «کوکی منقضی شده» دریافت شد، همین مراحل را با
یک نشست خصوصی تازه تکرار کنید. cookie عملاً کلید ورود حساب است؛ آن را برای کسی
نفرستید و به Git اضافه نکنید. استفاده مکرر از حساب ممکن است باعث محدودیت حساب شود؛
توصیه‌های نرخ درخواست در
[راهنمای رسمی YouTube در yt-dlp](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#youtube)
را رعایت کنید.

## اجرا با Docker Compose

ابتدا فایل تنظیمات را بسازید. برای تولید session string به شکل تعاملی:

```bash
cp .env.example .env
# API_ID و API_HASH را در .env وارد کنید
mkdir -p data
sudo chown -R 10001:10001 data
docker compose run --rm --no-deps hohokhan python -m scripts.generate_session
```

مقدار چاپ‌شده را داخل `.env` قرار دهید و سپس:

```bash
docker compose up -d --build
docker compose logs -f --tail=100
```

دیتابیس در `./data` نگهداری می‌شود؛ filesystem کانتینر read-only و `/tmp` از نوع
tmpfs است. فایل cookie نیز در صورت نیاز باید داخل همین `./data` قرار بگیرد، نه داخل
image.

## نصب مستقیم

```bash
sudo apt update
sudo apt install -y ffmpeg libzbar0 tesseract-ocr tesseract-ocr-fas python3-venv
# Node.js باید نسخه 23.5 یا جدیدتر باشد (نسخه 24 پیشنهاد می‌شود).
node --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.generate_session
python -m hohokhan
```

در اجرای تعاملی می‌توانید `SESSION_STRING` را خالی بگذارید تا Pyrogram فایل session
را داخل `DATA_DIR` بسازد؛ آن فایل نیز محرمانه است.

### ارتقا از نسخه دارای Pyrogram رسمی

Pyrogram و Kurigram هر دو namespace یکسان `pyrogram` را نصب می‌کنند؛ آن‌ها را در یک
virtualenv نگه ندارید. اگر قبلاً requirements قدیمی را نصب کرده‌اید، محیط را از نو
بسازید:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m scripts.generate_session
```

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
# در صورت نیاز به cookie یوتیوب:
incus file push data/youtube-cookies.txt \
  hohokhan/opt/hohokhan/source/data/youtube-cookies.txt \
  --uid 10001 --gid 10001 --mode 600
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

ایده برخی قابلیت‌های عمومی مانند AFK، notes، purge و quote از اکوسیستم UserBot و
پروژه‌های [Dragon Userbot](https://github.com/Dragon-Userbot/Dragon-Userbot)،
[AsenaUserBot](https://github.com/yusufusta/AsenaUserBot) و
[Moon Userbot](https://github.com/The-MoonTg-project/Moon-Userbot) الهام گرفته شده
است. چون این پروژه‌ها GPL-3.0 هستند، پیاده‌سازی HoHoKhan مستقل و بدون کپی کد آن‌ها
نوشته شده است.
