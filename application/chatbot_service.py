from typing import List, Optional
from ports.chatbot_port import ChatbotPort
from ports.knowledge_base_port import KnowledgeBasePort
from domain.models import ChatMessage
from infrastructure.config import config

class ChatbotService:
    def __init__(self, chatbot: ChatbotPort, knowledge_base: KnowledgeBasePort):
        self.chatbot = chatbot
        self.knowledge_base = knowledge_base
        self.conversation_history: List[ChatMessage] = []
        
    async def chat(self, user_message: str) -> str:
        config.log_debug(f"User message: {user_message}")
        
        self.conversation_history.append(ChatMessage(role="user", content=user_message))
        
        response = await self.chatbot.process_message(
            user_message, 
            context=self.conversation_history[-10:]
        )
        
        self.conversation_history.append(ChatMessage(role="assistant", content=response))
        
        config.log_debug(f"Assistant response: {response}")
        return response
    
    async def get_stats(self) -> dict:
        data = await self.knowledge_base.get_all_data()
        return {
            'total_products': data['total_products'],
            'total_categories': data['total_categories'],
            'conversation_length': len(self.conversation_history)
        }
    
    def clear_history(self):
        self.conversation_history.clear()
        config.log_debug("Conversation history cleared")