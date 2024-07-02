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

class Chatbot:
    '''
    Chatbot class that wraps the OpenAI API and provides a simple interface for interacting with it.
    '''
    def __init__(self, contextualize_q_system_prompt:str, qa_system_prompt:str, config:dict=None, ID:str=None) -> None:
        ''' Initialize the Chatbot object.
        Args:
            contextualize_q_prompt: A prompt for contextualizing questions.
            qa_system_prompt: A prompt for the QA system.
            config: A ChatbotConfig object containing the configuration for the chatbot.
            ID: A unique identifier for the chatbot.
        '''
        DEFAULT_CONFIG = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
        } # default config
        if config is None:
            config = DEFAULT_CONFIG
        
        self.config = config
        self.col = DB.Bots

        if not ID is None:
            if self.col.find_one({"_id": ObjectId(ID)}) is None:
                raise ValueError("BOT_ID does not exist in database.")
            else:
                self.ID = ID
        else:
            ID = self._create_chatbot(contextualize_q_system_prompt, qa_system_prompt, config)
            self.ID = ID

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

        self.llm = ChatOpenAI(model=self.config['model'], temperature=0)
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
    
    def _create_chatbot(self, contextualize_q_system_prompt:str, qa_system_prompt:str, config:dict=None) -> ObjectId:
        ''' Create a new chatbot in the database.

        Returns:
            The ID of the inserted chatbot.
        '''
        chatbot_data = {
            'contextualize_q_system_prompt': contextualize_q_system_prompt,
            'qa_system_prompt': qa_system_prompt,
            'config': config
        }
        result = self.col.insert_one(chatbot_data)
        return result.inserted_id
    
    def qa(self, input:str, prompter:Entity, responder:Entity) -> str:
        ''' Perform QA chain. 
        Args:
            prompter_input: The input for the prompter.
            responder_input: The input for the responder.
        '''

        session_id = str(prompter.ID) + str(responder.ID)

        prompter_context = f"PROMPTER_CONTEXT:\n{prompter.get_context_str()}"   
        responder_context = f"RESPONDER_CONTEXT:\n{responder.get_context_str()}"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.create_documents([prompter_context, responder_context])
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()

        history_aware_retriever = create_history_aware_retriever(self.llm, retriever, self.contextualize_q_prompt)       
        rag_chain = create_retrieval_chain(history_aware_retriever, self.question_answer_chain)

    
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            lambda session_id: MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=URI,
                database_name=DB_NAME,
                collection_name="Sessions",
            ),
            input_messages_key="input",
            history_messages_key="history",
            output_messages_key="answer"
        )
        res = conversational_rag_chain.invoke(
            {"input": input},
            config = {"configurable": {"session_id": session_id}}
        )

        answer = res["answer"]
        # chat_history = res["history"]

        return answer


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

if __name__ == '__main__':
    # first_four_entries = DB.Entities.find({}, '_id').limit(4)
    id1 = ObjectId('66808f6bef8163e460149f49')
    id2 = ObjectId('668098230301684548252e44')
    id3 = ObjectId('6680991c899dbda52bf7b486')
    id4 = ObjectId('6680a731800bcda61b3c9b06')

    contextualize_q_system_prompt = "Given a chat history and the latest prompt which might reference context in the chat history, formulate a standalone prompt which can be understood without the chat history. Do NOT answer the prompt, just reformulate it if needed and otherwise return it as is."
    qa_system_prompt = "You are a role playing chatbot for a Dungeons and Dragons game. There are two fictional characters: a prompter and a responder. You must respond to the prompt as if you are the responder. Use the following pieces of retrieved context to answer the prompt. If the context does not apply, respond in a way that makes sense. Use three sentences maximum, and keep the answer concise.\n\n{context}"
    
    # Init Existing Entity1, Entity2
    entity1 = Entity(ID=id1)
    entity2 = Entity(ID=id2)

    print(entity1.to_dict())
    print(entity2.to_dict())

    # create a new chatbot
    bot = Chatbot(contextualize_q_system_prompt, qa_system_prompt, ID=None)
    print(f"created bot with BOT_ID {bot.ID}")

    # Start QAChain
    description1 = entity1.get_description()
    description2 = entity2.get_description()
    while True:
        userInput = input(f"You are {description1} What would you like to ask {description2}?\n")
        answer = bot.qa(userInput, entity1, entity2)
        print('ANSWER:', answer)
