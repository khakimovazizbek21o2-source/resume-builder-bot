from aiogram.fsm.state import State, StatesGroup

class ResumeForm(StatesGroup):
    full_name = State()
    phone = State()
    education = State()
    skills = State()
    projects = State()