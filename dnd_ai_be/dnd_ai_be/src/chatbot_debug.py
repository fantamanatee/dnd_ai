from langchain.chains import create_history_aware_retriever
# from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from bson import ObjectId
from pprint import pprint
from dnd_ai_be.src.db_util import DB, URI, DB_NAME
from dnd_ai_be.src.characters import Entity, Player, NPC
from dnd_ai_be.src.util import timer

"""Chain that combines documents by stuffing into context."""
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document
from langchain_core.language_models import LanguageModelLike
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.prompts import BasePromptTemplate, format_document
from langchain_core.pydantic_v1 import Extra, Field, root_validator
from langchain_core.runnables import Runnable, RunnablePassthrough

from langchain.chains.combine_documents.base import (
    DEFAULT_DOCUMENT_PROMPT,
    DEFAULT_DOCUMENT_SEPARATOR,
    DOCUMENTS_KEY,
    BaseCombineDocumentsChain,
    _validate_prompt,
)
from langchain.chains.llm import LLMChain


from typing import Any, Dict, Union

from langchain_core.retrievers import (
    BaseRetriever,
    RetrieverOutput,
)
from langchain_core.runnables import Runnable, RunnablePassthrough
from pprint import pprint
import sys
import trace

# Modify print_me to accept *args and **kwargs
def print_me(*args, **kwargs):
    inputs = args[0]  # Assuming only one argument is passed for simplicity
    print()
    pprint(inputs)
    print()
    breakpoint()
    return inputs

def create_retrieval_chain(
    retriever: Union[BaseRetriever, Runnable[dict, RetrieverOutput]],
    combine_docs_chain: Runnable[Dict[str, Any], str],
) -> Runnable:
    """Create retrieval chain that retrieves documents and then passes them on.

    Args:
        retriever: Retriever-like object that returns list of documents. Should
            either be a subclass of BaseRetriever or a Runnable that returns
            a list of documents. If a subclass of BaseRetriever, then it
            is expected that an `input` key be passed in - this is what
            is will be used to pass into the retriever. If this is NOT a
            subclass of BaseRetriever, then all the inputs will be passed
            into this runnable, meaning that runnable should take a dictionary
            as input.
        combine_docs_chain: Runnable that takes inputs and produces a string output.
            The inputs to this will be any original inputs to this chain, a new
            context key with the retrieved documents, and chat_history (if not present
            in the inputs) with a value of `[]` (to easily enable conversational
            retrieval.

    Returns:
        An LCEL Runnable. The Runnable return is a dictionary containing at the very
        least a `context` and `answer` key.

    Example:
        .. code-block:: python

            # pip install -U langchain langchain-community

            from langchain_community.chat_models import ChatOpenAI
            from langchain.chains.combine_documents import create_stuff_documents_chain
            from langchain.chains import create_retrieval_chain
            from langchain import hub

            retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
            llm = ChatOpenAI()
            retriever = ...
            combine_docs_chain = create_stuff_documents_chain(
                llm, retrieval_qa_chat_prompt
            )
            retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

            chain.invoke({"input": "..."})

    """
    if not isinstance(retriever, BaseRetriever):
        retrieval_docs: Runnable[dict, RetrieverOutput] = retriever
    else:
        retrieval_docs = (lambda x: x["input"]) | retriever

    retrieval_chain = (
        RunnablePassthrough.assign(
            context=print_me(retrieval_docs).with_config(run_name="retrieve_documents"),
        ).assign(answer=print_me(combine_docs_chain))
    ).with_config(run_name="retrieval_chain")

    return retrieval_chain

def create_stuff_documents_chain(
    llm: LanguageModelLike,
    prompt: BasePromptTemplate,
    *,
    output_parser: Optional[BaseOutputParser] = None,
    document_prompt: Optional[BasePromptTemplate] = None,
    document_separator: str = DEFAULT_DOCUMENT_SEPARATOR,
) -> Runnable[Dict[str, Any], Any]:
    """Create a chain for passing a list of Documents to a model.

    Args:
        llm: Language model.
        prompt: Prompt template. Must contain input variable "context", which will be
            used for passing in the formatted documents.
        output_parser: Output parser. Defaults to StrOutputParser.
        document_prompt: Prompt used for formatting each document into a string. Input
            variables can be "page_content" or any metadata keys that are in all
            documents. "page_content" will automatically retrieve the
            `Document.page_content`, and all other inputs variables will be
            automatically retrieved from the `Document.metadata` dictionary. Default to
            a prompt that only contains `Document.page_content`.
        document_separator: String separator to use between formatted document strings.

    Returns:
        An LCEL Runnable. The input is a dictionary that must have a "context" key that
        maps to a List[Document], and any other input variables expected in the prompt.
        The Runnable return type depends on output_parser used.

    Example:
        .. code-block:: python

            # pip install -U langchain langchain-community

            from langchain_community.chat_models import ChatOpenAI
            from langchain_core.documents import Document
            from langchain_core.prompts import ChatPromptTemplate
            from langchain.chains.combine_documents import create_stuff_documents_chain

            prompt = ChatPromptTemplate.from_messages(
                [("system", "What are everyone's favorite colors:\\n\\n{context}")]
            )
            llm = ChatOpenAI(model="gpt-3.5-turbo")
            chain = create_stuff_documents_chain(llm, prompt)

            docs = [
                Document(page_content="Jesse loves red but not yellow"),
                Document(page_content = "Jamal loves green but not as much as he loves orange")
            ]

            chain.invoke({"context": docs})
    """  # noqa: E501

    _validate_prompt(prompt)
    _document_prompt = document_prompt or DEFAULT_DOCUMENT_PROMPT
    _output_parser = output_parser or StrOutputParser()

    def format_docs(inputs: dict) -> str:
        return document_separator.join(
            format_document(doc, _document_prompt) for doc in inputs[DOCUMENTS_KEY]
        )

    return (
        RunnablePassthrough.assign(**{DOCUMENTS_KEY: format_docs}).with_config(
            run_name="format_inputs"
        )
        | print_me
        | prompt
        | print_me
        | llm
        | print_me
        | _output_parser
        | print_me
    ).with_config(run_name="stuff_documents_chain")



class Chatbot:
    '''
    Chatbot class that wraps the OpenAI API and provides a simple interface for interacting with it.
    '''
    def __init__(self, name:str=None, contextualize_q_system_prompt:str=None, qa_system_prompt:str=None, config:dict=None, ID:str=None) -> None:
        ''' Initialize the Chatbot object.
        Args:
            contextualize_q_system_prompt: A system prompt for contextualizing questions.
            qa_system_prompt: A system prompt for the QA system.
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
        cur_session_id = str(prompter.ID) + str(responder.ID)
        NEW_SESSION = False
        if self.session_id is None or self.session_id != cur_session_id:
            self.session_id = cur_session_id
            NEW_SESSION = True

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
        
        
        if self.history_aware_retriever is None or NEW_SESSION:
            self.history_aware_retriever = create_retriever()

        rag_chain = create_retrieval_chain(self.history_aware_retriever, self.question_answer_chain)
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history=lambda session_id : MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=URI,
                database_name=DB_NAME,
                collection_name="Sessions",
            ),
            input_messages_key="input",
            history_messages_key="history",
            output_messages_key="answer"
        )
    
        @timer()
        def do_invoke():
            res = conversational_rag_chain.invoke(
                {"input": input},
                config = {"configurable": {"session_id": self.session_id}}
            )
            return res
        
        res = do_invoke()
        answer = res["answer"]

        return answer

    def to_dict(self):
        data = self.col.find_one({'_id': self.ID})
        return data


if __name__ == '__main__':
    bot_args =   {
    'name': 'default_bot_no_context_q_sys_prompt2',
    'contextualize_q_system_prompt': 'Given a chat history and the latest prompt which might reference context in the chat history, formulate a standalone prompt which can be understood without the chat history. Do NOT answer the prompt, just reformulate it if needed and otherwise return it as is.',
    'qa_system_prompt': 'You are a role playing chatbot for a Dungeons and Dragons game. There are two fictional characters: a prompter and a responder. You must respond to the prompt as if you are the responder. Use the following pieces of retrieved context to answer the prompt. If the context does not apply, respond in a way that makes sense. Use three sentences maximum, and keep the answer concise.\n' +
      '\n' +
      '{context}',
    'config': { 'model': 'gpt-3.5-turbo', 'temperature': 0 }
    }
    bot = Chatbot(**bot_args)

    print('bot:',bot.get_name())

    prompter = Player(ID=ObjectId('668b02bdf19ba1d40bb92630'))
    responder = NPC(ID=ObjectId('668ca09b8b1a765fbab94e9c'))

    while True:
        prompt = input('Prompt: ')
        ans = bot.qa(prompt, prompter, responder)
        print(ans)