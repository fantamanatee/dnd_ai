from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)
from langchain_core.messages.ai import AIMessage

from langchain_core.runnables.utils import (
    ConfigurableFieldSpec,
)

from dnd_ai_be.src.history import RunnableWithMessageHistory

# from langchain_core.runnables.history import RunnableWithMessageHistory

from dnd_ai_be.src.mongo_chat_history import MongoDBChatMessageHistory

# from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from bson import ObjectId
from pprint import pprint
from dnd_ai_be.src.db_util import DB, URI, DB_NAME
from dnd_ai_be.src.characters import Entity, Player, NPC, EntityLike
from dnd_ai_be.src.util import timer

import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable

# Auto-trace LLM calls in-context
client = wrap_openai(openai.Client())


class ChatBot:
    """
    Chatbot class that wraps the OpenAI API and provides a simple interface for interacting with it.
    """

    def __init__(
        self,
        name: str = None,
        contextualize_q_system_prompt: str = None,
        qa_system_prompt: str = None,
        config: dict = None,
        ID: str = None,
    ) -> None:
        """Initialize the Chatbot object.
        Args:
            contextualize_q_system_prompt: A system prompt for contextualizing questions.
            qa_system_prompt: A system prompt for the QA system.
            config: A ChatbotConfig object containing the configuration for the chatbot.
            ID: A unique identifier for the chatbot.
        """
        ID = ObjectId(ID) if ID else None
        DEFAULT_CONFIG = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
        }  # default config

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
                contextualize_q_system_prompt = self.col.find_one(
                    {"_id": ObjectId(ID)}
                )["contextualize_q_system_prompt"]
                qa_system_prompt = self.col.find_one({"_id": ObjectId(ID)})[
                    "qa_system_prompt"
                ]
                config = self.col.find_one({"_id": ObjectId(ID)})["config"]
                print("Chatbot loaded with BOT_ID:", ID)
        else:
            chatbot_data = {
                "name": name,
                "contextualize_q_system_prompt": contextualize_q_system_prompt,
                "qa_system_prompt": qa_system_prompt,
                "config": config,
            }
            result = self.col.insert_one(chatbot_data)
            self.ID = result.inserted_id
            print("ChatBot created with BOT_ID:", ID)

        self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("history"),
                ("human", "({input}"),
            ]
        )

        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("history"),
                ("human", "({input}"),
            ]
        )

        self.llm = ChatOpenAI(
            model=self.config["model"], temperature=self.config["temperature"]
        )
        self.question_answer_chain = create_stuff_documents_chain(
            self.llm, self.qa_prompt
        )

    def get_name(self) -> str:
        return self.col.find_one({"_id": self.ID})["name"]

    @traceable
    def generate_response(
        self, input_text: str, prompter: EntityLike, responder: EntityLike
    ) -> str:
        """Perform QA chain.
        Args:
            prompter_input: The input for the prompter.
            responder_input: The input for the responder.
        """
        print(f"Prompter: {prompter.get_name()}, Responder: {responder.get_name()}")
        cur_session_id = str(prompter.ID) + str(responder.ID)
        NEW_SESSION = False
        if self.session_id is None or self.session_id != cur_session_id:
            self.session_id = cur_session_id
            NEW_SESSION = True

        prompter_context = f"PROMPTER_CONTEXT:\n{prompter.get_context_str()}"
        responder_context = f"RESPONDER_CONTEXT:\n{responder.get_context_str()}"

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.create_documents([prompter_context, responder_context])
        vectorstore = Chroma.from_documents(
            documents=splits, embedding=OpenAIEmbeddings()
        )
        retriever = vectorstore.as_retriever()
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, self.contextualize_q_prompt
        )

        # if self.history_aware_retriever is None or NEW_SESSION:
        #     self.history_aware_retriever = create_retriever()

        rag_chain = create_retrieval_chain(
            self.history_aware_retriever, self.question_answer_chain
        )

        # with_message_history = RunnableWithMessageHistory(
        #     rag_chain,
        #     get_session_history=get_session_history,
        #     input_messages_key="question",
        #     history_messages_key="history",
        #     history_factory_config=[
        #         ConfigurableFieldSpec(
        #             id="user_id",
        #             annotation=str,
        #             name="User ID",
        #             description="Unique identifier for the user.",
        #             default="",
        #             is_shared=True,
        #         ),
        #         ConfigurableFieldSpec(
        #             id="conversation_id",
        #             annotation=str,
        #             name="Conversation ID",
        #             description="Unique identifier for the conversation.",
        #             default="",
        #             is_shared=True,
        #         ),
        #     ],
        # )

        print(f"session_id: {self.session_id}")
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history=lambda session_id: MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=URI,
                database_name=DB_NAME,
                collection_name="Sessions",
            ),
            input_messages_key="input",
            history_messages_key="history",
            output_messages_key="answer",
            input_prefix=prompter.get_name(),
            output_prefix=responder.get_name(),
        )

        res = conversational_rag_chain.invoke(
            input={"input": input_text, "name": prompter.get_name()},
            config={
                "configurable": {
                    "session_id": self.session_id,
                }
            },
        )
        answer = res["answer"]
        return answer

    def to_dict(self):
        data = self.col.find_one({"_id": self.ID})
        return data


class ReasoningBot:
    """
    ReasoningBot class that wraps the OpenAI API and provides a simple interface for interacting with it.
    """

    def __init__(
        self,
        name: str = None,
        reasoning_collection_name: str = None,
        reasoning_system_prompt: str = None,
        config: dict = None,
        ID: str = None,
    ) -> None:
        """Initialize the ReasoningBot object.
        Args:
            reasoning_system_prompt: A system prompt for the reasoning system.
            config: A ChatbotConfig object containing the configuration for the chatbot.
            ID: A unique identifier for the chatbot.
        """
        ID = ObjectId(ID) if ID else None
        DEFAULT_CONFIG = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
        }  # default config

        self.name = name
        if config is None:
            config = DEFAULT_CONFIG
        self.config = config
        self.col = DB.Bots
        self.mem_col = DB.Memories
        self.reasoning_collection_name = reasoning_collection_name
        self.session_id = None

        if not ID is None:
            if self.col.find_one({"_id": ObjectId(ID)}) is None:
                raise ValueError("BOT_ID does not exist in database.")
            else:
                self.ID = ID
                reasoning_system_prompt = self.col.find_one({"_id": ObjectId(ID)})[
                    "reasoning_system_prompt"
                ]
                config = self.col.find_one({"_id": ObjectId(ID)})["config"]
                print("ReasoningBot loaded with BOT_ID:", ID)
        else:
            reasoning_bot_data = {
                "name": name,
                "reasoning_system_prompt": reasoning_system_prompt,
                "config": config,
            }
            result = self.col.insert_one(reasoning_bot_data)
            self.ID = result.inserted_id
            print("ReasoningBot created with BOT_ID:", self.ID)

        self.reasoning_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", reasoning_system_prompt),
                ("human", "{input}"),
            ]
        )

        self.llm = ChatOpenAI(
            model=self.config["model"], temperature=self.config["temperature"]
        )
        self.question_answer_chain = create_stuff_documents_chain(
            self.llm, self.reasoning_prompt
        )

    def get_name(self) -> str:
        return self.col.find_one({"_id": self.ID})["name"]

    def generate_response(
        self, input_text: str, prompter: EntityLike, responder: EntityLike, k: int = 1
    ) -> str:
        """Perform reasoning chain.
        Args:
            input: The input for the prompter.
            prompter: The prompter entity.
            responder: The responder entity.
            k: The number of previous responses to consider for reasoning.
        """

        print(f"Prompter: {prompter.get_name()}, Responder: {responder.get_name()}")
        cur_session_id = str(prompter.ID) + str(responder.ID)
        NEW_SESSION = False
        if self.session_id is None or self.session_id != cur_session_id:
            self.session_id = cur_session_id
            NEW_SESSION = True

        @timer()
        def get_last_k_msgs(session_id, k):
            message_history = MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=URI,
                database_name=DB_NAME,
                collection_name=self.reasoning_collection_name,
            )
            history = message_history.messages
            return history[-2 * k :] if len(history) >= 2 * k else history

        last_k_msgs = get_last_k_msgs(self.session_id, k)
        reasoning_context = "\n".join([msg.content for msg in last_k_msgs])
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        context_documents = text_splitter.create_documents([reasoning_context])

        res = self.question_answer_chain.invoke(
            input={
                "input": input_text,
                "name": prompter.get_name(),
                "context": context_documents,
            },
            config={"configurable": {"session_id": self.session_id}},
        )

        # send response to Memories collection
        message = AIMessage(content=res)
        data = {
            "SessionId": self.session_id,
            "BotName": self.get_name(),
            "History": json.dumps(message_to_dict(message)),
        }
        self.mem_col.insert_one(data)
        return res

    def to_dict(self):
        data = self.col.find_one({"_id": self.ID})
        return data


if __name__ == "__main__":
    # bot_args = {
    #     "name": "default_bot_no_context_q_sys_prompt2",
    #     "contextualize_q_system_prompt": "Given a chat history and the latest prompt which might reference context in the chat history, formulate a standalone prompt which can be understood without the chat history. Do NOT answer the prompt, just reformulate it if needed and otherwise return it as is.",
    #     "qa_system_prompt": "You are a role playing chatbot for a Dungeons and Dragons game. There are two fictional characters: a prompter and a responder. You must respond to the prompt as if you are the responder. Use the following pieces of retrieved context to answer the prompt. If the context does not apply, respond in a way that makes sense. Use three sentences maximum, and keep the answer concise.\n"
    #     + "\n"
    #     + "{context}",
    #     "config": {"model": "gpt-3.5-turbo", "temperature": 0},
    # }
    # bot = ChatBot(**bot_args)

    # print("bot:", bot.get_name())

    # prompter = Player(ID=ObjectId("668b02bdf19ba1d40bb92630"))
    # responder = NPC(ID=ObjectId("668ca09b8b1a765fbab94e9c"))

    # while True:
    #     prompt = input("Prompt: ")
    #     ans = bot.generate_response(prompt, prompter, responder)
    #     print(ans)

    session_id = "66997d89afca9066c9e3180466997d86afca9066c9e31803"
    collection_name = "Memories"
    message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=URI,
        database_name=DB_NAME,
        collection_name=collection_name,
    )
    history = message_history.messages
    print(history)
