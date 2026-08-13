from __future__ import annotations

import html
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandHelp:
    usage: str
    description: str
    example: str | None = None
    access: str = "عمومی"


@dataclass(frozen=True, slots=True)
class HelpCategory:
    slug: str
    title: str
    aliases: tuple[str, ...]
    commands: tuple[CommandHelp, ...]


CATEGORIES = (
    HelpCategory(
        "general",
        "عمومی و اطلاعات",
        ("عمومی", "اطلاعات", "general"),
        (
            CommandHelp(".help [موضوع]", "نمایش فهرست یا راهنمای یک بخش", ".help media"),
            CommandHelp(".help all", "نمایش تمام بخش‌های راهنما"),
            CommandHelp("ping", "اندازه‌گیری زمان پاسخ ربات"),
            CommandHelp(".info", "اطلاعات کاربر؛ روی پیام او ریپلای کنید"),
            CommandHelp(".id", "نمایش شناسه چت، پیام و کاربر ریپلای‌شده"),
            CommandHelp(".chatinfo", "اطلاعات چت فعلی", access="مالک/مجاز"),
            CommandHelp(".admins", "فهرست مدیران گروه"),
            CommandHelp("sysinfo", "مصرف CPU، RAM و دیسک", access="مالک/مجاز"),
            CommandHelp("هو هو خان", "دریافت پاسخ تصادفی کوتاه"),
            CommandHelp("فال", "ارسال غزل و تعبیر تصادفی حافظ"),
            CommandHelp("بخونش", "ارسال صوت آخرین فال حافظ شما"),
            CommandHelp("تاس / TAS", "انداختن تاس تلگرام"),
            CommandHelp("دارت / DART", "پرتاب دارت تلگرام"),
            CommandHelp("بسکتبال / توپ", "پرتاب توپ بسکتبال تلگرام"),
        ),
    ),
    HelpCategory(
        "media",
        "رسانه",
        ("رسانه", "دانلود", "media"),
        (
            CommandHelp(".music نام یا لینک", "دانلود صدای YouTube", ".music Shadmehr Taghdir"),
            CommandHelp(".yt عبارت", "جست‌وجوی YouTube", ".yt آموزش پایتون"),
            CommandHelp(
                "ارسال لینک رسانه",
                "دانلود ویدیو از YouTube، Instagram، TikTok، X، Likee و Radio Javan",
            ),
            CommandHelp(".photo", "تبدیل استیکر ثابت به تصویر؛ با ریپلای"),
            CommandHelp(".sticker", "تبدیل تصویر به استیکر؛ با ریپلای"),
        ),
    ),
    HelpCategory(
        "tools",
        "وب، تصویر و شبکه",
        ("ابزار", "تصویر", "شبکه", "tools"),
        (
            CommandHelp(".wiki عبارت", "خلاصه ویکی‌پدیای فارسی", ".wiki شبکه عصبی"),
            CommandHelp(
                ".weather شهر",
                "آب‌وهوای فعلی؛ نیازمند OpenWeather API",
                ".weather Tehran",
            ),
            CommandHelp(".qr متن", "ساخت QR؛ برای خواندن روی تصویر ریپلای کنید"),
            CommandHelp("ocr", "استخراج متن فارسی و انگلیسی از عکس؛ با ریپلای"),
            CommandHelp("ارسال فایل .ovpn", "تبدیل hostname دستور remote به IP عمومی"),
            CommandHelp(".ips شبکه", "محاسبه اطلاعات subnet", ".ips 192.168.1.0/24"),
        ),
    ),
    HelpCategory(
        "text",
        "متن و رمزنگاری",
        ("متن", "رمز", "text"),
        (
            CommandHelp(".hash الگوریتم متن", "محاسبه hash", ".hash sha256 hello"),
            CommandHelp(".pass [طول]", "ساخت رمز تصادفی امن", ".pass 24"),
            CommandHelp(".rot13 متن", "تبدیل ROT13"),
            CommandHelp(".encode متن", "رمزگذاری URL-safe Base64"),
            CommandHelp(".decode متن", "رمزگشایی URL-safe Base64"),
        ),
    ),
    HelpCategory(
        "productivity",
        "بهره‌وری",
        ("بهره‌وری", "یادداشت", "afk", "productivity"),
        (
            CommandHelp(".afk [دلیل]", "فعال‌کردن وضعیت عدم حضور", ".afk جلسه", "مالک"),
            CommandHelp(".back", "پایان‌دادن دستی به AFK", access="مالک"),
            CommandHelp(
                ".save نام متن",
                "ذخیره یادداشت متنی",
                ".save server آدرس سرور",
                "مالک/مجاز",
            ),
            CommandHelp(".save نام", "ذخیره متن پیام ریپلای‌شده", access="مالک/مجاز"),
            CommandHelp(".note نام", "نمایش یک یادداشت", access="مالک/مجاز"),
            CommandHelp(".notes", "فهرست نام یادداشت‌ها", access="مالک/مجاز"),
            CommandHelp(".delnote نام", "حذف یک یادداشت", access="مالک/مجاز"),
        ),
    ),
    HelpCategory(
        "messages",
        "پیام‌ها",
        ("پیام", "پاکسازی", "messages"),
        (
            CommandHelp(".quote", "ساخت نقل‌قول از پیام ریپلای‌شده"),
            CommandHelp(
                ".purge",
                "حذف پیام‌ها از پیام ریپلای‌شده تا دستور؛ حداکثر ۱۰۰",
                access="مالک/مجاز",
            ),
            CommandHelp(
                ".purge تعداد",
                "حذف تعداد مشخصی از پیام‌های اخیر؛ حداکثر ۱۰۰",
                ".purge 25",
                "مالک/مجاز",
            ),
            CommandHelp("del", "حذف پیام ریپلای‌شده و دستور", access="مالک/مجاز"),
            CommandHelp("tag", "منشن اعضای غیرربات؛ حداکثر ۱۰۰ نفر", access="مالک/مجاز"),
        ),
    ),
    HelpCategory(
        "replies",
        "پاسخ خودکار",
        ("پاسخ", "جواب", "replies"),
        (
            CommandHelp("addans محرک | پاسخ", "افزودن یا ویرایش پاسخ خودکار", access="مالک/مجاز"),
            CommandHelp("delans محرک", "حذف پاسخ خودکار", access="مالک/مجاز"),
            CommandHelp("anslist", "فهرست پاسخ‌های خودکار", access="مالک/مجاز"),
            CommandHelp("cleanans", "حذف همه پاسخ‌های خودکار", access="مالک/مجاز"),
        ),
    ),
    HelpCategory(
        "admin",
        "مدیریت",
        ("مدیریت", "ادمین", "admin"),
        (
            CommandHelp(".kick", "حذف کاربر؛ با ریپلای یا شناسه", access="مالک/مجاز"),
            CommandHelp(".mute / .unmute", "اعمال یا رفع محدودیت ارسال", access="مالک/مجاز"),
            CommandHelp(".add", "افزودن کاربر به گروه", access="مالک/مجاز"),
            CommandHelp(".join لینک", "عضویت در چت", access="مالک/مجاز"),
            CommandHelp(".leave", "خروج از چت", access="مالک/مجاز"),
            CommandHelp("قفل گروه / باز کردن گروه", "تغییر دسترسی ارسال اعضا", access="مالک/مجاز"),
            CommandHelp("block / unblock", "مسدود یا آزادکردن کاربر", access="مالک/مجاز"),
            CommandHelp(
                "هوهوخان بگو متن",
                "پاسخ‌دادن با متن ربات به پیام ریپلای‌شده",
                "هوهوخان بگو سلام",
                "مدیر گروه",
            ),
        ),
    ),
)


def _render_command(command: CommandHelp) -> str:
    usage = html.escape(command.usage)
    description = html.escape(command.description)
    result = f"• <code>{usage}</code> — {description} <i>({html.escape(command.access)})</i>"
    if command.example:
        result += f"\n  مثال: <code>{html.escape(command.example)}</code>"
    return result


def render_index() -> str:
    lines = [
        "<b>راهنمای HoHoKhan UserBot</b>",
        "برای جزئیات هر بخش از <code>.help نام‌بخش</code> استفاده کنید:",
        "",
    ]
    for category in CATEGORIES:
        lines.append(
            f"• <code>.help {html.escape(category.slug)}</code> — {html.escape(category.title)}"
        )
    lines.extend(("", "نمایش همه: <code>.help all</code>"))
    return "\n".join(lines)


def render_category(category: HelpCategory) -> str:
    lines = [f"<b>{html.escape(category.title)}</b>", ""]
    lines.extend(_render_command(command) for command in category.commands)
    return "\n".join(lines)


def render_help(topic: str = "") -> tuple[str, ...]:
    normalized = topic.strip().casefold()
    if not normalized:
        return (render_index(),)
    if normalized in {"all", "همه"}:
        return tuple(render_category(category) for category in CATEGORIES)
    for category in CATEGORIES:
        aliases = {category.slug.casefold(), *(alias.casefold() for alias in category.aliases)}
        if normalized in aliases:
            return (render_category(category),)
    available = "، ".join(category.slug for category in CATEGORIES)
    raise ValueError(f"بخش راهنما پیدا نشد. بخش‌های موجود: {available}")

