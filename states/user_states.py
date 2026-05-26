from aiogram.fsm.state import State, StatesGroup
class UserMessageOperator(StatesGroup):
    waiting_message = State()
