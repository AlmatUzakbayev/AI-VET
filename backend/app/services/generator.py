import os
from typing import Dict
from dotenv import load_dotenv
from langchain_core.load import loads
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

from backend.app.core.constants import TEXT_PROMPT

load_dotenv()


class AiVeterinarian:
    def __init__(self, model_name="gemini-2.5-flash", max_messages=6):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY не найден в .env")
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.messages = []
        self.summary = ""
        self.max_messages = max_messages
        self.system_prompt = TEXT_PROMPT

    def _summarize_conversation(self):
        if self.summary:
            summary_prompt = f"Это краткое содержание разговора: {self.summary}\n\nДобавь к нему новые сообщения."
        else:
            summary_prompt = "Суммаризируй разговор выше."
        messages_for_summary = self.messages + [HumanMessage(content=summary_prompt)]
        response = self.model.invoke(messages_for_summary)
        self.summary = response.content
        self.messages = self.messages[-2:]

    def ask(self, user_input: str, user_config: Dict[str, str], conversation_state) -> Dict:
        role = user_config.get("role", "неизвестная роль")
        animal = user_config.get("animal", "неизвестное животное")
        modified_user_input = f"Роль: {role}, Животное: {animal}, Пользователь говорит: {user_input}"

        if isinstance(conversation_state, str):
            try:
                conversation_state = loads(conversation_state)
                logging.debug(f"Deserialized conversation_state: {conversation_state}")
            except Exception as e:
                logging.error(f"Failed to deserialize conversation_state: {e}")
                conversation_state = {"messages": [], "summary": ""}
        if not isinstance(conversation_state, dict):
            logging.warning(f"conversation_state is not a dict, resetting: {type(conversation_state)}")
            conversation_state = {"messages": [], "summary": ""}

        user_conversation = conversation_state.get("messages", [])
        summary = conversation_state.get("summary", "")

        user_conversation.append(HumanMessage(content=modified_user_input))

        if summary:
            system_message = SystemMessage(content=f"Суммаризация: {summary}")
            messages_to_send = [system_message] + user_conversation
        else:
            messages_to_send = user_conversation

        response = self.model.invoke(messages_to_send)
        user_conversation.append(AIMessage(content=response.content))

        if len(user_conversation) > self.max_messages:
            self.messages = user_conversation
            self.summary = summary
            self._summarize_conversation()
            conversation_state["summary"] = self.summary
            conversation_state["messages"] = self.messages[-2:]
        else:
            conversation_state["messages"] = user_conversation

        return conversation_state

