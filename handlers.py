from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from states import ResumeForm

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Salom! Men sizga professional Rezyume (CV) tayyorlashda yordam beraman.\n\n"
        "Boshlash uchun **Ism va Familiyangizni** kiriting:"
    )
    await state.set_state(ResumeForm.full_name)

@router.message(ResumeForm.full_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Ajoyib! Endi **telefon raqamingizni** kiriting (masalan: +998901234567):")
    await state.set_state(ResumeForm.phone)

@router.message(ResumeForm.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Qayerda tahsil olasiz/olgansiz? (**Ta'lim muassasasi, yo'nalish va bosqich**):")
    await state.set_state(ResumeForm.education)

@router.message(ResumeForm.education)
async def process_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer("Asosiy **ko'nikmalaringizni (Skills)** kiriting (masalan: Python, SQL, Git, Linux):")
    await state.set_state(ResumeForm.skills)

@router.message(ResumeForm.skills)
async def process_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await message.answer("Qilgan **tajribangiz yoki loyihalaringiz** haqida qisqacha ma'lumot bering:")
    await state.set_state(ResumeForm.projects)

@router.message(ResumeForm.projects)
async def process_projects(message: Message, state: FSMContext):
    await state.update_data(projects=message.text)
    
    data = await state.get_data()
    
    resume_text = (
        f"📄 **RESUME / CURRICULUM VITAE**\n\n"
        f"👤 **Ism-Familiya:** {data['full_name']}\n"
        f"📞 **Aloqa:** {data['phone']}\n\n"
        f"🎓 **Ta'lim:**\n{data['education']}\n\n"
        f"🛠 **Texnik Ko'nikmalar:**\n{data['skills']}\n\n"
        f"🚀 **Tajriba va Loyihalar:**\n{data['projects']}\n\n"
        f"---"
    )
    
    await message.answer("Sizning tayyor Rezyume shabloningiz:\n")
    await message.answer(resume_text, parse_mode="Markdown")
    await state.clear()