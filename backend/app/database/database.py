import json
import os
import pathlib
from typing import Dict

from langchain_core.load import dumps

from backend.app.core.constants import CONVERSATIONS_DIRECTORY, USER_STATUSES_DIRECTORY


class HistoryWriter:
    def __init__(self):
        self._conversation_directory = CONVERSATIONS_DIRECTORY
        self._user_status_directory = USER_STATUSES_DIRECTORY
        self.create_directories()

    def create_directories(self) -> None:
        self.create_directory(self._conversation_directory)
        self.create_directory(self._user_status_directory)

    @staticmethod
    def create_directory(file_path) -> None:
        try:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
        except Exception as e:
            print(f"Error creating directory: {e}")

    @staticmethod
    def write_json(file_path: pathlib.Path, data: dict) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing to JSON file: {e}")

    @staticmethod
    def read_json(file_path: pathlib.Path) -> Dict:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading from JSON file: {e}")
            return {}

    def load_user_conversations(self) -> Dict:
        return self.load_all_files(self._conversation_directory)

    def load_user_statuses(self) -> Dict:
        return self.load_all_files(self._user_status_directory)

    def load_all_files(self, directory: pathlib.Path) -> Dict:
        data = {}
        for file_path in directory.glob("*.json"):
            file_data = self.read_json(file_path)
            data.update(file_data)
        return data

    def save_user_conversation(self, user_id: str, conversation: str) -> None:
        file_path = pathlib.Path(self._conversation_directory, f"{user_id}.json")
        data = self.read_json(file_path)
        data[user_id] = conversation
        self.write_json(file_path, data)

    def update_user_status(self, user_id: str, status: dict) -> None:
        file_path = pathlib.Path(self._user_status_directory, f"{user_id}.json")
        data = self.read_json(file_path)
        data[user_id] = status
        self.write_json(file_path, data)

    def save_user_conversations(self, conversations: dict) -> None:
        for user_id, conversation in conversations.items():
            conversation_json = dumps(conversation, ensure_ascii=False, indent=4, pretty=True)
            self.save_user_conversation(user_id, conversation_json)

    def save_user_statuses(self, statuses: dict) -> None:
        for user_id, status in statuses.items():
            self.update_user_status(user_id, status)

    @staticmethod
    def create_json_file(user_id: str) -> None:
        from backend.app.core.constants import CONVERSATIONS_DIRECTORY, USER_STATUSES_DIRECTORY
        conversation_file = os.path.join(CONVERSATIONS_DIRECTORY, f"{user_id}.json")
        status_file = os.path.join(USER_STATUSES_DIRECTORY, f"{user_id}.json")
        with open(conversation_file, "w") as file:
            json.dump({user_id: {"messages": [], "summary": ""}}, file)
        with open(status_file, "w") as file:
            json.dump({user_id: {"role": "", "animal": ""}}, file)

