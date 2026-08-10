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
    buttons = [[KeyboardButton(text="⬅️ Orqaga")]]
    if can_skip:
        buttons[0].append(KeyboardButton(text="⏭ O'tkazib yuborish"))
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
    await state.clear()
    await message.answer(
        "Xush kelibsiz! Rezyume yaratish uchun <b>To'liq ism-familiyangizni</b> kiriting:\n\n<i>Misol: Azizbek Xakimov</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ResumeForm.full_name)

# Universal 'Orqaga' tugmasi
@router.message(F.text == "⬅️ Orqaga")
async def go_back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == ResumeForm.phone:
        await message.answer("<b>To'liq ism-familiyangizni</b> kiriting:", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        await state.set_state(ResumeForm.full_name)
    elif current_state == ResumeForm.email:
        await message.answer("Telefon raqamingizni kiriting:", reply_markup=get_phone_keyboard())
        await state.set_state(ResumeForm.phone)
    elif current_state == ResumeForm.education:
        await message.answer("Email manzilingizni kiriting:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.email)
    elif current_state == ResumeForm.skills:
        await message.answer("Ma'lumotingiz (Universitet/Kollej) haqida yozing:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.education)
    elif current_state == ResumeForm.experience:
        await message.answer("Ko'nikmalaringizni kiriting:", reply_markup=get_step_keyboard())
        await state.set_state(ResumeForm.skills)
    elif current_state == ResumeForm.photo:
        await message.answer("Ish tajribangiz haqida yozing:", reply_markup=get_step_keyboard(can_skip=True))
        await state.set_state(ResumeForm.experience)

# 1. Ism
@router.message(ResumeForm.full_name)
async def process_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 3 or any(char.isdigit() for char in text):
        await message.answer("❌ Noto'g'ri ism kiritdingiz! Faqat harflardan foydalaning va kamida 3 ta belgi bo'lsin.")
        return

    await state.update_data(full_name=escape(text))
    await message.answer("Telefon raqamingizni kiriting yoki tugmani bosing:", reply_markup=get_phone_keyboard())
    await state.set_state(ResumeForm.phone)

# 2. Telefon (Contact yoki Text)
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
            await message.answer("❌ Noto'g'ri telefon raqami! Masalan: +998901234567")
            return
        phone = clean_phone

    await state.update_data(phone=escape(phone))
    await message.answer("Email manzilingizni kiriting:", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.email)

# 3. Email
@router.message(ResumeForm.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        await message.answer("❌ Noto'g'ri email formati! (Masalan: name@gmail.com)")
        return

    await state.update_data(email=escape(email))
    await message.answer("Ta'lim joyingiz va yo'nalishingiz haqida yozing:", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.education)

# 4. Ta'lim
@router.message(ResumeForm.education)
async def process_education(message: types.Message, state: FSMContext):
    if len(message.text.strip()) < 5:
        await message.answer("❌ Iltimos, ta'lim joyingiz haqida batafsilroq yozing.")
        return

    await state.update_data(education=escape(message.text.strip()))
    await message.answer("Ko'nikmalaringizni kiriting (Masalan: Python, SQL, Git, Linux):", reply_markup=get_step_keyboard())
    await state.set_state(ResumeForm.skills)

# 5. Ko'nikmalar
@router.message(ResumeForm.skills)
async def process_skills(message: types.Message, state: FSMContext):
    await state.update_data(skills=escape(message.text.strip()))
    await message.answer(
        "Ish tajribangiz haqida yozing (Aks holda 'O'tkazib yuborish' tugmasini bosing):",
        reply_markup=get_step_keyboard(can_skip=True)
    )
    await state.set_state(ResumeForm.experience)

# 6. Ish tajribasi
@router.message(ResumeForm.experience)
async def process_experience(message: types.Message, state: FSMContext):
    exp_text = "Mavjud emas" if message.text == "⏭ O'tkazib yuborish" else message.text.strip()
    await state.update_data(experience=escape(exp_text))
    
    await message.answer(
        "📸 <b>Rezyume uchun rasmingizni yuboring:</b>\n\n"
        "<i>(Agar rasm qo'shishni xohlamasangiz, 'Rasmsiz davom etish' tugmasini bosing)</i>",
        parse_mode="HTML",
        reply_markup=get_photo_keyboard()
    )
    await state.set_state(ResumeForm.photo)

# 7. Rasm qabul qilish va Tasdiqlash
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

    summary = (
        "📋 <b>Kiritilgan ma'lumotlarni tekshiring:</b>\n\n"
        f"👤 <b>F.I.SH:</b> {data['full_name']}\n"
        f"📞 <b>Tel:</b> {data['phone']}\n"
        f"📧 <b>Email:</b> {data['email']}\n"
        f"🎓 <b>Ta'lim:</b> {data['education']}\n"
        f"🛠 <b>Ko'nikmalar:</b> {data['skills']}\n"
        f"💼 <b>Tajriba:</b> {data['experience']}\n"
        f"🖼 <b>Rasm:</b> {'Mavjud ✅' if data.get('photo_path') else 'Mavjud emas ❌'}\n\n"
        "PDF faylni yarataylikmi?"
    )

    await message.answer("Ma'lumotlar qabul qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer(summary, parse_mode="HTML", reply_markup=get_confirm_keyboard())
    await state.set_state(ResumeForm.confirm)

# Callback: Qayta boshlash
@router.callback_query(F.data == "restart_form")
async def cb_restart(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Anketa qayta boshlandi. <b>To'liq ism-familiyangizni</b> kiriting:", parse_mode="HTML")
    await state.set_state(ResumeForm.full_name)
    await call.answer()

# Callback: PDF generator va yuborish
@router.callback_query(F.data == "generate_pdf")
async def cb_generate_pdf(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await call.message.answer("Ma'lumotlar topilmadi. Qaytadan /start bosing.")
        await call.answer()
        return

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("⏳ PDF rezyumengiz tayyorlanmoqda, kuting...")
    
    pdf_path = f"resume_{call.from_user.id}.pdf"
    try:
        create_resume_pdf(data, pdf_path)
        
        doc = FSInputFile(pdf_path)
        await call.message.answer_document(
            document=doc,
            caption="🎉 <b>Sizning tayyor PDF rezyumengiz!</b>\n\nYangi rezyume yaratish uchun /start bosing.",
            parse_mode="HTML"
        )
        await state.clear()
    except Exception as e:
        await call.message.answer(f"❌ PDF yaratishda xatolik yuz berdi: {str(e)}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    await call.answer()
