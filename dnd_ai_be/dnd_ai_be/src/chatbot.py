from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from bson import ObjectId

from dnd_ai_be.src.db_util import DB, URI, DB_NAME
from dnd_ai_be.src.characters import Entity
from dnd_ai_be.src.util import timer

import logging
logging.basicConfig(level=logging.DEBUG)

class Chatbot:
    '''
    Chatbot class that wraps the OpenAI API and provides a simple interface for interacting with it.
    '''
    def __init__(self, name:str=None, contextualize_q_system_prompt:str=None, qa_system_prompt:str=None, config:dict=None, ID:str=None) -> None:
        ''' Initialize the Chatbot object.
        Args:
            contextualize_q_prompt: A prompt for contextualizing questions.
            qa_system_prompt: A prompt for the QA system.
            config: A ChatbotConfig object containing the configuration for the chatbot.
            ID: A unique identifier for the chatbot.
        '''
        ID = ObjectId(ID) if ID else None
        DEFAULT_CONFIG = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
        } # default config

        self.name = name
        if config is None:
            config = DEFAULT_CONFIG
        self.config = config
        self.col = DB.Bots
        self.history_aware_retriever = None
        self.rag_chain = None
        self.session_id = None

        if not ID is None:
            if self.col.find_one({"_id": ObjectId(ID)}) is None:
                raise ValueError("BOT_ID does not exist in database.")
            else:
                self.ID = ID
                contextualize_q_system_prompt = self.col.find_one({"_id": ObjectId(ID)})['contextualize_q_system_prompt']
                qa_system_prompt = self.col.find_one({"_id": ObjectId(ID)})['qa_system_prompt']
                config = self.col.find_one({"_id": ObjectId(ID)})['config']
                print('Chatbot loaded with BOT_ID:', ID)
        else:
            chatbot_data = {
            'name': name,
            'contextualize_q_system_prompt': contextualize_q_system_prompt,
            'qa_system_prompt': qa_system_prompt,
            'config': config
            }
            result = self.col.insert_one(chatbot_data)
            self.ID = result.inserted_id

        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("history"),
            ("human", "{input}")
        ])
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
        ])
        print(self.contextualize_q_prompt)
        print(self.qa_prompt)

        self.llm = ChatOpenAI(model=self.config['model'], temperature=self.config['temperature'])
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
    

    def get_name(self) -> str:
        return self.col.find_one({'_id': self.ID})['name']
    
    def qa(self, input:str, prompter:Entity, responder:Entity) -> str:
        ''' Perform QA chain. 
        Args:
            prompter_input: The input for the prompter.
            responder_input: The input for the responder.
        '''
        print(f"Prompter: {prompter.get_name()}, Responder: {responder.get_name()}")
        

        prompter_context = f"PROMPTER_CONTEXT:\n{prompter.get_context_str()}"   
        responder_context = f"RESPONDER_CONTEXT:\n{responder.get_context_str()}"

        @timer()
        def create_retriever():
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.create_documents([prompter_context, responder_context])
            vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
            retriever = vectorstore.as_retriever()
            history_aware_retriever = create_history_aware_retriever(self.llm, retriever, self.contextualize_q_prompt)       
            return history_aware_retriever
        
        if self.history_aware_retriever is None:
            self.history_aware_retriever =  create_retriever()

        @timer()
        def create_rag_chain(session_id:str):
            rag_chain = create_retrieval_chain(self.history_aware_retriever, self.question_answer_chain)
            conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                lambda : MongoDBChatMessageHistory(
                    session_id=session_id,
                    connection_string=URI,
                    database_name=DB_NAME,
                    collection_name="Sessions",
                ),
                input_messages_key="input",
                history_messages_key="history",
                output_messages_key="answer"
            )
            return conversational_rag_chain
        
        cur_session_id = str(prompter.ID) + str(responder.ID)
        if self.session_id is None or self.session_id != cur_session_id:
            self.session_id = cur_session_id
            conversational_rag_chain = create_rag_chain(cur_session_id)
    
        @timer()
        def do_invoke():
            res = conversational_rag_chain.invoke(
                {"input": input},
                config = {"configurable": {"session_id": cur_session_id}}
            )
            return res
        
        res = do_invoke()
        answer = res["answer"]

        print()
        return answer

    def to_dict(self):
        data = self.col.find_one({'_id': self.ID})
        return data


if __name__ == '__main__':
    bot = Chatbot(ID='66860333855efbe743f85ad1')
    print(bot.to_dict())
    print(bot.get_name())