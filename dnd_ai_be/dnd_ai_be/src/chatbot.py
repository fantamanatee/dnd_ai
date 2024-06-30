import bs4
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dnd_ai_be.src.bot_util import save_docs_to_jsonl, load_docs_from_jsonl

class ChatbotConfig:
    '''
    Configuration class for the Chatbot class. 
        Provides default fields and updates based on the input config.
    '''
    def __init__(self, config):
        self.config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
        } # default config
        if config:
            for key in config:
                if key in config:
                    self.config[key] = config[key]
                else:
                    print(f"Ignoring update for key '{key}' because it does not exist in base_dict.")


class Chatbot:
    '''
    Chatbot class that wraps the OpenAI API and provides a simple interface for interacting with it.
    Each chatbot has a unique ID and can be associated with an entity (NPC, Player, or Entity).

    FIXME: For now, it uses JSON to store the chat history, but this could be changed to a database in the future.
    '''
    def __init__(self, ID:str, ENTITY_ID:str = None, config:dict = None) -> None:
        ''' Initialize the Chatbot object.
        Args:
            ID: A unique identifier for the chatbot.
            config: A dictionary containing the configuration for the chatbot.
            ENTITY_ID: A unique identifier for the entity. 
                The entity may be an instance of Entity, NPC, or Player.
                Ex: E_1, NPC_7, P_4
        '''
        self.ID = ID
        self.ENTITY_ID = ENTITY_ID
        self.config = ChatbotConfig(config)

    def set_entity_id(self, ENTITY_ID):
        ''' Set the entity ID for the chatbot. These can be interchanged for the same bot.
        Args:
            ENTITY_ID: A unique identifier for the entity. 
                The entity may be an instance of Entity, NPC, or Player.
                Ex: E_1, NPC_7, P_4
        '''
        self.ENTITY_ID = ENTITY_ID
    
    def __str__(self) -> str:
        ''' Returns a string representation of the chatbot. '''
        return f"Chatbot {self.ID}, Entity: {self.ENTITY_ID}, Config: {self.config}"
    
        

    
        