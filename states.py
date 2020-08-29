from aiogram.dispatcher.filters.state import StatesGroup, State


class JobForm(StatesGroup):
    job = State()
    area = State()
    
class GoogleForm(StatesGroup):
	query = State()

class WikiForm(StatesGroup):
	query = State()

class WethaForm(StatesGroup):
	city = State()

class SetCityForm(StatesGroup):
	city = State()

class CooperationForm(StatesGroup):
	name = State()
	connect = State()
	deal_text = State()
	deal_doc_y_n = State()
	deal_doc = State()
	money = State()
	send_y_n = State()