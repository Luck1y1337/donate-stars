from aiogram.fsm.state import State, StatesGroup


class DonateStates(StatesGroup):
    waiting_custom_amount = State()
    waiting_comment = State()


class AdminStates(StatesGroup):
    waiting_goal = State()
    waiting_broadcast = State()
    waiting_search = State()
    waiting_reply = State()
    waiting_restore_file = State()


class ContactStates(StatesGroup):
    waiting_message = State()
