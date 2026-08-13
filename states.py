from aiogram.fsm.state import StatesGroup, State

class ResumeForm(StatesGroup):
    full_name = State()
    profession = State()
    location = State()
    phone = State()
    email = State()
    salary = State()
    about = State()
    education = State()
    skills = State()
    languages = State()
    exp_company = State()
    exp_position = State()
    exp_period = State()
    exp_duties = State()
    photo = State()
    confirm = State()