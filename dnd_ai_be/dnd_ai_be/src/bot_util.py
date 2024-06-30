from  langchain.schema import Document
from langchain_community.document_loaders.mongodb import MongodbLoader
import json
from typing import Iterable

def save_docs_to_jsonl(array:Iterable[Document], file_path:str)->None:
    ''' Save a list of Document objects to a JSONL file.
    '''
    with open(file_path, 'w') as jsonl_file:
        for doc in array:
            jsonl_file.write(doc.json() + '\n')

def load_docs_from_jsonl(file_path)->Iterable[Document]:
    ''' Load a list of Document objects from a JSONL file.
    '''
    array = []
    with open(file_path, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            obj = Document(**data)
            array.append(obj)
    return array