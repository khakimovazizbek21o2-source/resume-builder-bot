import os
import re
from html import escape

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

from states import ResumeForm
from pdf_generator import create_resume_pdf

router = Router()

# ==================== KLAVIATURALAR ==================== #

def get_step_keyboard(can_skip: bool = False):
    buttons = []
    if can_skip:
        buttons.append([KeyboardButton(text="⏭ O'tkazib yuborish")])
    buttons.append([KeyboardButton(text="⬅️ Orqaga")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def get_photo_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Rasmsiz davom etish")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def get_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ PDF Yaratish", callback_data="generate_pdf"),
            InlineKeyboardButton(text="🔄 Qayta boshlash", callback_data="restart_form")
        ]
    ])

# ==================== HANDLERLAR ==================== #

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    # /start bosilganda FSM holati to'liq tozalanadi
    await state.clear()
    await message.answer(
        "Xush kelibsiz! Rezyume yaratish uchun <b>To'liq ism-familiyangizni</b> kiriting:\n\n<i>Misol: Azizbek Xakimov</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ResumeForm.full_name)

# Orqaga tugmasi
@router.message(F.text == "⬅️ Orqaga")
async def go_back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == ResumeForm.profession:
        await message.answer("To'liq ism-familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(ResumeForm.full_name)
    elif current_state == ResumeForm.location:
        await message.answer("Kasbingiz yoki mutaxassisligingizni kiriting:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.profession)
    elif current_state == ResumeForm.phone:
        await message.answer("Yashash shahringiz yoki manzilingizni kiriting:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.location)
    elif current_state == ResumeForm.email:
        await message.answer("Telefon raqamingizni kiriting:", reply_markup=get_phone_keyboard())
        await state.set_state(ResumeForm.phone)
    elif current_state == ResumeForm.salary:
        await message.answer("Email manzilingizni kiriting:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.email)
    elif current_state == ResumeForm.about:
        await message.answer("Kutilayotgan oylik maoshni kiriting:", reply_markup=get_step_keyboard(can_skip=True))
        await state.set_state(ResumeForm.salary)
    elif current_state == ResumeForm.education:
        await message.answer("O'zingiz haqida qisqacha yozing:", reply_markup=get_step_keyboard(can_skip=True))
        await state.set_state(ResumeForm.about)
    elif current_state == ResumeForm.skills:
        await message.answer("Ta'lim joyingiz va mutaxassisligingiz haqida yozing:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.education)
    elif current_state == ResumeForm.languages:
        await message.answer("Kompyuter va dasturlash ko'nikmalaringizni kiriting:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.skills)
    elif current_state == ResumeForm.exp_company:
        await message.answer("Chet tillarini bilish darajangizni kiriting:", reply_markup=get_step_keyboard(can_skip=True))
        await state.set_state(ResumeForm.languages)
    elif current_state == ResumeForm.exp_position:
        await message.answer("Ishlagan korxona yoki kompaniyangiz nomini kiriting:", reply_markup=get_step_keyboard(can_skip=True))
        await state.set_state(ResumeForm.exp_company)
    elif current_state == ResumeForm.exp_period:
        await message.answer("Ushbu korxonada qaysi lavozimda ishlagansiz?", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.exp_position)
    elif current_state == ResumeForm.exp_duties:
        await message.answer("Ishlagan davringizni kiriting:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.exp_period)
    elif current_state == ResumeForm.photo:
        data = await state.get_data()
        if data.get("has_experience"):
            await message.answer("Majburiyat va yutuqlaringiz haqida yozing:", reply_markup=get_step_keyboard())
            await state.set_state(ResumeForm.exp_duties)
        else:
            await message.answer("Ishlagan korxona yoki kompaniyangiz nomini kiriting:", reply_markup=get_step_keyboard(can_skip=True))
            await state.set_state(ResumeForm.exp_company)

# 1. Ism
@router.message(ResumeForm.full_name)
async def process_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 3 or any(char.isdigit() for char in text):
        await message.answer("❌ Noto'g'ri ism kiritdingiz! Faqat harflardan foydalaning.")
        return
    await state.update_data(full_name=escape(text))
    await message.answer("Kasbingiz yoki mutaxassisligingizni kiriting:\n<i>(Masalan: Python Dasturchi)</i>", parse_mode="HTML", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.profession)

# 2. Mutaxassislik
@router.message(ResumeForm.profession)
async def process_profession(message: types.Message, state: FSMContext):
    await state.update_data(profession=escape(message.text.strip()))
    await message.answer("Yashash shahringiz yoki manzilingizni kiriting:\n<i>(Masalan: Toshkent sh., Chilonzor)</i>", parse_mode="HTML", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.location)

# 3. Manzil
@router.message(ResumeForm.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=escape(message.text.strip()))
    await message.answer("Telefon raqamingizni kiriting yoki tugmani bosing:", reply_markup=get_phone_keyboard())
    await state.set_state(ResumeForm.phone)

# 4. Telefon
@router.message(ResumeForm.phone, F.contact | F.text)
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
    else:
        phone = message.text.strip()
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not re.match(r'^\+?[0-9]{9,13}$', clean_phone):
            await message.answer("❌ Noto'g'ri telefon raqami!")
            return
        phone = clean_phone

    await state.update_data(phone=escape(phone))
    await message.answer("Email manzilingizni kiriting:", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.email)

# 5. Email
@router.message(ResumeForm.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        await message.answer("❌ Noto'g'ri email formati!")
        return

    await state.update_data(email=escape(email))
    await message.answer("Kutilayotgan oylik ish haqini kiriting (Masalan: $700):", reply_markup=get_step_keyboard(can_skip=True))
    await state.set_state(ResumeForm.salary)

# 6. Maosh
@router.message(ResumeForm.salary)
async def process_salary(message: types.Message, state: FSMContext):
    salary = None if message.text == "⏭ O'tkazib yuborish" else escape(message.text.strip())
    await state.update_data(salary=salary)
    await message.answer(
        "<b>PROFIL / HAQIDA</b>\n\nO'zingiz, tajribangiz va maqsadingiz haqida qisqacha yozing:",
        parse_mode="HTML",
        reply_markup=get_step_keyboard(can_skip=True)
    )
    await state.set_state(ResumeForm.about)

# 7. Haqida
@router.message(ResumeForm.about)
async def process_about(message: types.Message, state: FSMContext):
    about = None if message.text == "⏭ O'tkazib yuborish" else escape(message.text.strip())
    await state.update_data(about=about)
    await message.answer("Ta'lim joyingiz va mutaxassisligingiz haqida yozing:", parse_mode="HTML", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.education)

# 8. Ta'lim
@router.message(ResumeForm.education)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=escape(message.text.strip()))
    await message.answer("Ko'nikmalaringizni kiriting (vergul bilan ajratib):\n<i>(Masalan: Python, Django, Git)</i>", parse_mode="HTML", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.skills)

# 9. Ko'nikmalar
@router.message(ResumeForm.skills)
async def process_skills(message: types.Message, state: FSMContext):
    await state.update_data(skills=escape(message.text.strip()))
    await message.answer("Chet tillarini bilish darajangizni kiriting:", parse_mode="HTML", reply_markup=get_step_keyboard(can_skip=True))
    await state.set_state(ResumeForm.languages)

# 10. Chet tillari
@router.message(ResumeForm.languages)
async def process_languages(message: types.Message, state: FSMContext):
    langs = None if message.text == "⏭ O'tkazib yuborish" else escape(message.text.strip())
    await state.update_data(languages=langs)
    await message.answer(
        "<b>ISH TAJRIBASI</b>\n\nIshlagan korxona/kompaniyangiz nomini kiriting:",
        parse_mode="HTML",
        reply_markup=get_step_keyboard(can_skip=True)
    )
    await state.set_state(ResumeForm.exp_company)

# 11. Ish tajribasi - Kompaniya
@router.message(ResumeForm.exp_company)
async def process_exp_company(message: types.Message, state: FSMContext):
    if message.text == "⏭ O'tkazib yuborish":
        await state.update_data(has_experience=False, exp_company=None, exp_position=None, exp_period=None, exp_duties=None)
        await message.answer("📸 <b>Rezyume uchun rasmingizni yuboring:</b>", parse_mode="HTML", reply_markup=get_photo_keyboard())
        await state.set_state(ResumeForm.photo)
    else:
        await state.update_data(has_experience=True, exp_company=escape(message.text.strip()))
        await message.answer("Ushbu korxonada qaysi lavozimda ishlagansiz?", parse_mode="HTML", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.exp_position)

# 12. Lavozim
@router.message(ResumeForm.exp_position)
async def process_exp_position(message: types.Message, state: FSMContext):
    await state.update_data(exp_position=escape(message.text.strip()))
    await message.answer("Ishlagan davringizni kiriting:", parse_mode="HTML", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.exp_period)

# 13. Davr
@router.message(ResumeForm.exp_period)
async def process_exp_period(message: types.Message, state: FSMContext):
    await state.update_data(exp_period=escape(message.text.strip()))
    await message.answer("Majburiyatingiz va erishgan yutuqlaringiz haqida yozing:", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.exp_duties)

# 14. Majburiyatlar
@router.message(ResumeForm.exp_duties)
async def process_exp_duties(message: types.Message, state: FSMContext):
    await state.update_data(exp_duties=escape(message.text.strip()))
    await message.answer("📸 <b>Rezyume uchun rasmingizni yuboring:</b>", parse_mode="HTML", reply_markup=get_photo_keyboard())
    await state.set_state(ResumeForm.photo)

# 15. Rasm va Yakunlash
@router.message(ResumeForm.photo, F.photo | (F.text == "⏭ Rasmsiz davom etish"))
async def process_photo(message: types.Message, state: FSMContext, bot):
    photo_path = None

    if message.photo:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        os.makedirs("temp_photos", exist_ok=True)
        photo_path = f"temp_photos/user_{message.from_user.id}.jpg"
        await bot.download_file(file_info.file_path, destination=photo_path)
    
    await state.update_data(photo_path=photo_path)
    data = await state.get_data()

    exp_info = "Mavjud emas ❌"
    if data.get("has_experience"):
        exp_info = f"\n  • 🏢 Kompaniya: {data.get('exp_company')}\n  • 💼 Lavozim: {data.get('exp_position')}\n  • 📅 Davr: {data.get('exp_period')}"

    summary = (
        "📋 <b>Kiritilgan ma'lumotlarni tekshiring:</b>\n\n"
        f"👤 <b>F.I.SH:</b> {data['full_name']}\n"
        f"📌 <b>Kasbi:</b> {data.get('profession')}\n"
        f"📍 <b>Manzil:</b> {data.get('location')}\n"
        f"📞 <b>Tel:</b> {data['phone']}\n"
        f"📧 <b>Email:</b> {data['email']}\n"
        f"💰 <b>Kutilgan maosh:</b> {data.get('salary') or 'Kiritilmadi'}\n"
        f"🎓 <b>Ta'lim:</b> {data['education']}\n"
        f"🛠 <b>Ko'nikmalar:</b> {data['skills']}\n"
        f"🌐 <b>Chet tillari:</b> {data.get('languages') or 'Kiritilmadi'}\n"
        f"💼 <b>Ish tajribasi:</b> {exp_info}\n"
        f"🖼 <b>Rasm:</b> {'Mavjud ✅' if data.get('photo_path') else 'Mavjud emas ❌'}\n\n"
        "PDF faylni yarataylikmi?"
    )

    await message.answer("Ma'lumotlar qabul qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer(summary, parse_mode="HTML", reply_markup=get_confirm_keyboard())
    await state.set_state(ResumeForm.confirm)

# Callbacks
@router.callback_query(F.data == "restart_form")
async def cb_restart(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Anketa qayta boshlandi. <b>To'liq ism-familiyangizni</b> kiriting:", parse_mode="HTML")
    await state.set_state(ResumeForm.full_name)
    await call.answer()

@router.callback_query(F.data == "generate_pdf")
async def cb_generate_pdf(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await call.message.answer("Ma'lumotlar topilmadi. Qaytadan /start bosing.")
        await call.answer()
        return

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("⏳ PDF rezyumengiz tayyorlanmoqda...")
    
    pdf_path = f"resume_{call.from_user.id}.pdf"

    try:
        # 1. PDF yaratish
        create_resume_pdf(data, pdf_path)

        # 2. Faqat PDF faylni yuborish
        doc = FSInputFile(pdf_path)
        await call.message.answer_document(
            document=doc,
            caption="🎉 <b>Sizning tayyor PDF rezyumengiz!</b>\n\nYangi rezyume yaratish uchun /start bosing.",
            parse_mode="HTML"
        )
        
        # Vaqtinchalik yuklangan profil rasmini o'chirish
        photo_p = data.get("photo_path")
        if photo_p and os.path.exists(photo_p):
            os.remove(photo_p)
            
        await state.clear()

    except Exception as e:
        await call.message.answer(f"❌ PDF yaratishda xatolik yuz berdi: {str(e)}")

    finally:
        # Yaratilgan PDF faylni o'chirish
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    await call.answer()