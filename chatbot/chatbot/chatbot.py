"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
from pcconfig import config

import openai
import pynecone as pc
from pynecone.base import Base

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.document_loaders import (
    NotebookLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import SequentialChain
import os
os.environ["OPENAI_API_KEY"] = open("appkey.txt", "r").read()
openai.api_key = open("appkey.txt", "r").read()

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class Message(Base):
    role: str
    content: str


class State(pc.State):
    text: str = "Type something..."
    chatList: list[Message] = []

    def post_chat(self):
        self.chatList.append(
            Message(role="user", content=self.text)
        )
        response = generate_answer(self.text)

        self.chatList.append(
            Message(role="assistant", content=str(response))
        )

    def upload(self):
        upload_embeddings_from_dir(INPUT_FILE_PATH)

    def query(self):
        print(query_db(self.text))
        print()
        print()

LOADER_DICT = {
    "txt": TextLoader,
    "md": UnstructuredMarkdownLoader,
    "ipynb": NotebookLoader,
}

ORIGIN_DIR = os.getcwd()
CHROMA_PERSIST_DIR = os.path.join(ORIGIN_DIR, "chroma")
CHROMA_COLLECTION_NAME = "kakao-bot"
INPUT_FILE_PATH = os.path.join(ORIGIN_DIR, "inputData")

def upload_embedding_from_file(file_path):
    loader = LOADER_DICT.get(file_path.split(".")[-1])
    if loader is None:
        raise ValueError("Not supported file type")
    documents = loader(file_path).load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print(docs, end='\n\n\n')

    Chroma.from_documents(
        docs,
        OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print('db success')

def upload_embeddings_from_dir(dir_path):
    print("test")
    failed_upload_files = []

    for root, dirs, files in os.walk(dir_path):
        print(files)
        for file in files:
            if file.endswith(".txt") or file.endswith(".md") or file.endswith(".ipynb"):
                file_path = os.path.join(root, file)
                print("test2")
                try:
                    upload_embedding_from_file(file_path)
                    print("SUCCESS: ", file_path)
                except Exception as e:
                    print("FAILED: ", file_path + f"by({e})")
                    failed_upload_files.append(file_path)

_db = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=OpenAIEmbeddings(),
    collection_name=CHROMA_COLLECTION_NAME,
)
_retriever = _db.as_retriever()

def query_db(query: str, use_retriever: bool = False) -> list[str]:
    if use_retriever:
        docs = _retriever.get_relevant_documents(query)
    else:
        docs = _db.similarity_search(query)

    str_docs = [doc.page_content for doc in docs]
    return str_docs

def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template

def create_chain(llm, template_path, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=read_prompt_template(template_path),
        ),
        output_key=output_key,
        verbose=True,
    )

def generate_answer(question) -> dict[str, str]:
    context = dict(user_message=question)
    context["input"] = context["user_message"]
    context["related_documents"] = query_db(context["user_message"])

    answer = inform_chain.run(context)
    
    return {"answer": answer}

# 서버 시작전 전처리 단계
INFORM_PROMPT_TEMPLATE = os.path.join(ORIGIN_DIR, "prompt/inform.txt")
llm = ChatOpenAI(temperature=0.1, max_tokens=1024, model="gpt-3.5-turbo")
upload_embeddings_from_dir(INPUT_FILE_PATH)
inform_chain = create_chain(
    llm=llm,
    template_path=INFORM_PROMPT_TEMPLATE,
    output_key="output",
)


#### view
def message(message):
    return pc.box(
        pc.text(message.role + " : " + message.content, float="left")
    )


def index() -> pc.Component:
    return pc.fragment(
        pc.input(
            placeholder="봇이랑 대화해보세요.",
            on_blur=State.set_text,
        ),
        pc.button("Post", on_click=State.post_chat, margin_top="1rem"),
        pc.vstack(
            pc.foreach(State.chatList, message),
        ),
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.compile()
