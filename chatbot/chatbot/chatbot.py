"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
from pcconfig import config

import openai
import pynecone as pc
from pynecone.base import Base

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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 내 친구니깐 나랑 대화할 때 반말을 해도 돼."},
                {"role": "user", "content": self.text},
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        print(response)

        self.chatList.append(
            Message(role="assistant", content=response.choices[0].message.content)
        )


## view


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
