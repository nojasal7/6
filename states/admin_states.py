from aiogram.fsm.state import State, StatesGroup
class AdminCreateTicket(StatesGroup):
    operator_name = State()
    title = State()
    description = State()
    target = State()
class AdminBroadcast(StatesGroup):
    text = State()
    target = State()

