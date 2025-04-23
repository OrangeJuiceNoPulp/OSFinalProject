import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.prompts import PromptTemplate

from langchain_huggingface.llms import HuggingFacePipeline

from transformers import AutoTokenizer, AutoModelForCausalLM,pipeline
from transformers.utils import logging

# Prevents unnecessary output to command line.
# Only displays errors.
# Was displaying "Device set to use CPU" or other unwanted text before
logging.set_verbosity_error()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Use the TinyLlama as the LLM
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

pipe = pipeline(
    "text-generation", model=model, tokenizer=tokenizer, max_new_tokens=128
)

llm = HuggingFacePipeline(pipeline=pipe)

# Load the vector store for retrieval
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

chroma_client = chromadb.PersistentClient(path='os_search_chroma_db', settings=Settings(allow_reset=True, anonymized_telemetry=False))
collection = chroma_client.get_or_create_collection(name="os_search")

vector_store = Chroma(
    client=chroma_client,
    collection_name="os_search",
    embedding_function=embeddings,
)

# Define prompt for question-answering
template = """
<|system|>
You are an assistant for question-answering tasks. Only use the following pieces of retrieved context to answer the question. Avoid using outside knowledge. If the answer cannot be determined, simply say that it cannot be determined. Answer concisely, using two or three sentences maximum.  Context: {context}</s>
<|user|>
{question}</s>
<|assistant|>
"""
prompt_template = PromptTemplate.from_template(template)

query = input("Query: ")
while True:
    if query.lower() == 'exit' or query.lower() == 'quit':
        break

    results = vector_store.similarity_search(query, k=1)

    print('Context from: ' + results[0].metadata['source'])

    docs_content = "\n\n".join(doc.page_content for doc in results)
    messages = prompt_template.invoke({"question": query, "context": docs_content})

    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    for chunk in llm.stream(messages):
        print(chunk, end="", flush=True)
    print('\n')
    query = input("Query: ")


