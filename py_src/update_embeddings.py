import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Default directories to add to the database
DIRS_TO_ADD = [os.path.expanduser('~') + '/Desktop',
               os.path.expanduser('~') + '/Documents',
               os.path.expanduser('~') + '/Downloads']

# Determine if the user has specified a custom list of directories to add to the database
MAX_READ_LENGTH = 2**12
if os.path.exists(os.path.expanduser('~') + '/os_search/custom_dirs.txt'):
    fd = os.open(os.path.expanduser('~') + '/os_search/custom_dirs.txt', os.O_RDONLY)
    try:
        data = os.read(fd, MAX_READ_LENGTH)

        DIRS_TO_ADD = data.decode('utf-8').split('\n')

        # Remove any blank entries and remove leading/trailing whitespace
        DIRS_TO_ADD = [i.strip() for i in DIRS_TO_ADD if i.strip() != '']

        # If the filepath is not absolute, insert the home directory to the front
        DIRS_TO_ADD = [(os.path.expanduser('~') + '/' + i[2:]) if i[:2] == './' 
                       else (os.path.expanduser('~') + '/' + i) if i[0] != '/' 
                       else i for i in DIRS_TO_ADD]

    except:
        print('Could not read file: ' + os.path.expanduser('~') + '/os_search/custom_dirs.txt')

    finally:
        os.close(fd)
               
# Determine the chunk sizes for the text to be embedded
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
SUPPORTED_FILE_EXTENSIONS = ['.txt', '.pdf']

# Set the embedding model as Sentence Transformer's all-mpnet-base-v2
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Create a chroma client instance
chroma_client = chromadb.PersistentClient(path='os_search_chroma_db', settings=Settings(allow_reset=True, anonymized_telemetry=False))
collection = chroma_client.get_or_create_collection(name="os_search")

vector_store = Chroma(
    client=chroma_client,
    collection_name="os_search",
    embedding_function=embeddings,
)

def remove_deleted_files():
    
    list_of_document_metadata = collection.get(include=['metadatas'])['metadatas']

    for doc in list_of_document_metadata:
        file_path = doc.get('source')
        if not os.path.exists(file_path):
            # The file has been moved or deleted
            # Remove the entry from the vector db
            collection.delete(where={"source":file_path})
            
def add_doc_to_db(file_path, file_type='.txt'):

    # Determine the time the file was last modified
    modification_time = os.path.getmtime(file_path)
    
    # Check if the file already exists in the database
    results = collection.get(include=['metadatas'], where={"source":file_path})
    
    # If there is a resulting document already in the database
    if len(results['metadatas']) > 0:
        # If the file has not been modified
        if results['metadatas'][0]['last_modified'] == modification_time:
            # Return to avoid recalculating embeddings
            return
        # If the file has been modified, delete old embeddings
        else:
            collection.delete(where={"source":file_path})

    
    # Load the file
    if file_type == '.pdf':
        loader = PyPDFLoader(file_path, extract_images=False, mode='single')
        document_text = loader.load()
    elif file_type == '.txt':
        loader = TextLoader(file_path)
        document_text = loader.load()
    else:
        # If the filetype is not supported, do nothing (return)
        return

    # Add metadata to keep track of file modification
    for text in document_text:
        text.metadata['last_modified'] = modification_time

    # Split the file's text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs = text_splitter.split_documents(document_text)

    # Add the text chunks into the Chroma vector database
    try:
        ids = vector_store.add_documents(documents=docs)
    except:
        pass

def directory_scanner(base_dir):
    # Get the contents of the directory
    directory_contents = os.scandir(base_dir)
    # Loop through all of the directory's contents
    for file_or_dir in directory_contents:
        # If the current item is a directory
        if file_or_dir.is_dir():
            # Recursively scan through the directory
            directory_scanner(file_or_dir.path)
        # If the current item is a file
        elif file_or_dir.is_file():
            # Determine the file extension
            file_type = os.path.splitext(file_or_dir.path)[-1]
            # If the file type is supported
            if file_type in SUPPORTED_FILE_EXTENSIONS:
                # Add the file to the vector database
                add_doc_to_db(file_or_dir.path, file_type=file_type)
                
                

# Remove deleted files from database             
remove_deleted_files()

# Scan through the directories to add any new or modified files to the database
for DIR_NAME in DIRS_TO_ADD:
    if os.path.exists(DIR_NAME):
        directory_scanner(DIR_NAME)
