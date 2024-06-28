from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
import os
from src.characters import NPC, Player, Character

def generate_response(prompter : Character, responder : Character, query_text):
    ''' Generate a response to a query using lore and memory from both characters
    args:
        prompter: the Person generating the prompt
        responder: the Person generating the response
        query_text: the text to query the responder with
    returns:
        response: the response from the responder
    '''
    prompter_lore = [prompter.get_lore()]
    # Split documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.create_documents(lore)
    # Select embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
    # Create a vectorstore from documents
    db = Chroma.from_documents(texts, embeddings)
    # Create retriever interface
    retriever = db.as_retriever()
    # Create QA chain
    qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key=os.getenv('OPENAI_API_KEY')), chain_type='stuff', retriever=retriever)
    return qa.run(query_text)

def main():
    '''
    Start a new game of DnD
    '''

    print("Welcome to the DnD AI!")

    npc = NPC("Gandalf", "A wise wizard", "Wizard")
    player = Player("Aragorn", "A ranger from the North", "Ranger", 5)

    while True:
        # get input from user
        query_text = input("What would you like to ask Gandalf?")
        generate_response()
    
