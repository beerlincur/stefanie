import json
from aiogram import types


async def remember_user_start(message: types.Message) -> None:
    """Adds users info to file"""
    with open('users.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)
        
        data["users"][f"{message.chat.id}"] = {
			"first": message.from_user.first_name,
			"last": message.from_user.last_name,
			"username": message.from_user.username
		}

        file.seek(0)
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
        file.truncate()