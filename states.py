from aiogram.fsm.state import State, StatesGroup

class ResumeForm(StatesGroup):
    full_name = State()
    phone = State()
    email = State()
    education = State()
    skills = State()
    experience = State()
    confirm = State()