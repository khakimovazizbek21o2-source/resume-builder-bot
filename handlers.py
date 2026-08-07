import os
import re
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from states import ResumeForm
from pdf_generator import create_resume_pdf

router = Router()

# Klaviaturalar
def get_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ PDF Yaratish", callback_data="generate_pdf"),
            InlineKeyboardButton(text="🔄 Qayta boshlash", callback_data="restart_form")
        ]
    ])

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Xush kelibsiz! Rezyume yaratish uchun **To'liq ism-familiyangizni** kiriting:\n\n*Misol: Azizbek Xakimov*")
    await state.set_state(ResumeForm.full_name)

# 1. Ism validatsiyasi
@router.message(ResumeForm.full_name)
async def process_name(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 3 or any(char.isdigit() for char in text):
        await message.answer("❌ Noto'g'ri ism kiritdingiz! Ism faqat harflardan iborat bo'lishi va kamida 3 ta belgidan tashkil topishi kerak.")
        return
    
    await state.update_data(full_name=text)
    await message.answer("Telefon raqamingizni kiriting:\n\n*Misol: +998901234567*")
    await state.set_state(ResumeForm.phone)

# 2. Telefon validatsiyasi
@router.message(ResumeForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    if not re.match(r'^\+?[0-9]{9,13}$', clean_phone):
        await message.answer("❌ Noto'g'ri telefon raqami! Iltimos, raqamni to'g'ri shaklda kiriting (masalan: +998901234567).")
        return

    await state.update_data(phone=clean_phone)
    await message.answer("Email manzilingizni kiriting:\n\n*Misol: example@gmail.com*")
    await state.set_state(ResumeForm.email)

# 3. Email validatsiyasi
@router.message(ResumeForm.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        await message.answer("❌ Noto'g'ri email formati! Iltimos, haqiqiy email kiriting (masalan: name@gmail.com).")
        return

    await state.update_data(email=email)
    await message.answer("Ma'lumotingiz (Qaysi universitet/kollej va yo'nalish) haqida yozing:")
    await state.set_state(ResumeForm.education)

# 4. Ta'lim
@router.message(ResumeForm.education)
async def process_education(message: types.Message, state: FSMContext):
    if len(message.text.strip()) < 5:
        await message.answer("❌ Iltimos, ta'lim joyingiz haqida batafsilroq yozing.")
        return

    await state.update_data(education=message.text.strip())
    await message.answer("Ko'nikmalaringiz va texnologiyalaringizni kiriting:\n\n*Misol: Python, SQL, Git, Linux*")
    await state.set_state(ResumeForm.skills)

# 5. Ko'nikmalar
@router.message(ResumeForm.skills)
async def process_skills(message: types.Message, state: FSMContext):
    await state.update_data(skills=message.text.strip())
    await message.answer("Ish tajribangiz haqida yozing (yoki 'Yo'q' deb yuboring):")
    await state.set_state(ResumeForm.experience)

# 6. Ish tajribasi va tasdiqlash
@router.message(ResumeForm.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text.strip())
    data = await state.get_data()

    summary = (
        "📋 **Kiritilgan ma'lumotlarni tekshiring:**\n\n"
        f"👤 **F.I.SH:** {data['full_name']}\n"
        f"📞 **Tel:** {data['phone']}\n"
        f"📧 **Email:** {data['email']}\n"
        f"🎓 **Ta'lim:** {data['education']}\n"
        f"🛠 **Ko'nikmalar:** {data['skills']}\n"
        f"💼 **Tajriba:** {data['experience']}\n\n"
        "PDF faylni yarataylikmi?"
    )

    await message.answer(summary, parse_mode="Markdown", reply_markup=get_confirm_keyboard())
    await state.set_state(ResumeForm.confirm)

# Callback: Qayta boshlash
@router.callback_query(F.data == "restart_form")
async def cb_restart(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Anketa qayta boshlandi. **To'liq ism-familiyangizni** kiriting:")
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

    await call.message.answer("⏳ PDF rezyumengiz tayyorlanmoqda, kuting...")
    
    pdf_path = f"resume_{call.from_user.id}.pdf"
    try:
        create_resume_pdf(data, pdf_path)
        
        doc = FSInputFile(pdf_path)
        await call.message.answer_document(
            document=doc,
            caption="🎉 **Sizning tayyor PDF rezyumengiz!**\n\nYangi rezyume yaratish uchun /start bosing."
        )
        await state.clear()
    except Exception as e:
        await call.message.answer(f"❌ PDF yaratishda xatolik yuz berdi: {str(e)}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    await call.answer()