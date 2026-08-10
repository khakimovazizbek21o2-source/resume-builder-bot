from aiogram.fsm.state import State, StatesGroup

class ResumeForm(StatesGroup):
    full_name = State()   # F.I.SH
    phone = State()       # Telefon raqami
    email = State()       # Email
    education = State()   # Ta'lim
    skills = State()      # Ko'nikmalar
    experience = State()  # Ish tajribasi
    photo = State()       # 📸 Rasm (Photo)
    confirm = State()     # Tasdiqlash