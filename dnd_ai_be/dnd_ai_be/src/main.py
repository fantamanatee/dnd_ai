from langchain_openai import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
import os
from dnd_ai_be.src.characters import NPC, Player, Entity, Character
from dnd_ai_be.src.db_util import db_insert_one

# FIXME replace this simple function with one using MongoDBLoader and chat history
def generate_response(prompter : Character, responder : Character, query_text):
    ''' Generate a response to a query using lore and memory from both characters
    args:
        prompter: the Person generating the prompt
        responder: the Person generating the response
        query_text: the text to query the responder with
    returns:
        response: the response from the responder
    '''
    lore = [prompter.get_description(), responder.get_description()]
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.create_documents(lore)
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
    db = Chroma.from_documents(texts, embeddings)
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key=os.getenv('OPENAI_API_KEY')), chain_type='stuff', retriever=retriever)

    return qa.run(query_text)

def main():
    '''
    Start a new game of DnD
    '''

    print("Welcome to the DnD AI!")

    npc = NPC(role="Wizard", name="Gandalf", race="human", tags=["friendly", "magic"], description="A wise wizard")
    player = Player("Ranger", 3, "Aragorn", "human", ["friendly", "ranged"], "A skilled ranger.")

    querier = player
    responder = npc

    while True:
        # get input from user -- TODO: deal with keyboard interrupt, saving state
        query_text = input(f"{querier.name}, What would you like to ask {responder.name}?\n")
        if query_text == "exit" or query_text == "EXIT":
            break
        
        response = generate_response(player, npc, query_text)
        print(response)

    
if __name__ == '__main__':
    # main()
    # Example NPCs
    npc1 = NPC(role="Merchant", name="Gimble", race="Halfling", tags=["Friendly", "Trader"], description="A jovial halfling merchant.")
    npc2 = NPC(role="Guard", name="Thorn", race="Human", tags=["Friendly", "Guard", "City Watch"], description="A vigilant human guard.")

    # Example Players
    player1 = Player(player_class="Wizard", level=5, name="Elowen", race="Elf", tags=["Adventurer"], description="A wise elven wizard.")
    player2 = Player(player_class="Fighter", level=3, name="Garrick", race="Human", tags=["Mercenary"], description="A skilled human fighter.")

    # Example Entities
    entity1 = Entity(race="Dragonborn", tags=["Friendly", "Mythical", "Dragon"], description="A majestic dragonborn warrior.")
    entity2 = Entity(race="Human", tags=["Hostile", "Commoner"], description="A humble human villager.")

    for entity in [npc1, npc2, player1, player2, entity1, entity2]:
        db_insert_one(entity)