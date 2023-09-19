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
from langchain.chains import SequentialChain
import os
os.environ["OPENAI_API_KEY"] = open("appkey.txt", "r").read()
openai.api_key = open("appkey.txt", "r").read()

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"

STEP_1 = """
#시작하기
이 문서는 카카오싱크에 대해 소개하고, 카카오싱크 도입에 필요한 검수 및 설정에 대해 안내합니다.

위 시작하기에 대한 내용을 잘 숙지하고 유저가 물어보면 대답해줄 수 있도록 해줘.
"""

STEP_2 = """
#기능 소개
카카오싱크는 소셜 로그인인 카카오 로그인을 통해 보다 편리하게 서비스에 가입할 수 있도록 도와주는 비즈니스 솔루션입니다. 카카오싱크가 제공하는 핵심 기능은 다음 두 가지입니다.

  기능 | 설명 | 효과
  간편가입 | 동의 화면에서 서비스 약관까지 한 번에 동의받을 수 있습니다. | 서비스 약관 동의 절차 생략 가능
   더 다양한 사용자 정보 활용 | 서비스 회원 가입 시 필요한 다양한 사용자 정보를 제공받을 수 있습니다. 이름, 이메일, 전화번호, 연령대, 생일, 성별, 출생연도, 배송지 등 정보를 제공합니다. | 회원 정보 입력 절차 생략 가능

   위 기능 소개에 대한 내용을 잘 숙지하고 유저가 물어보면 대답해줄 수 있도록 해줘.
"""

STEP_3 = """
# 과정 예시
1. 카카오로 시작하기 버튼 : 사용자가 카카오싱크 도입 서비스에서 [카카오로 시작하기] 버튼을 눌러 로그인을 요청합니다. 카카오싱크 도입 서비스에서 사용자는 서비스 회원 ID와 비밀번호 입력 대신 카카오톡을 통해 손쉽게 로그인할 수 있습니다. 카카오톡 실행이 불가능한 환경이라도 카카오계정을 사용해 별도 서비스 회원 가입 절차 없이 로그인할 수 있습니다.

2. 동의하고 계속하기 : 사용자는 카카오톡 또는 카카오계정으로 로그인한 후, 동의 화면에서 정보 제공 동의 항목과 서비스 약관 모두 한 번에 동의할 수 있습니다. 카카오싱크 도입 서비스의 동의 화면은 서비스 약관 동의를 포함해, 한 화면에서 회원 가입에 필요한 동의를 모두 받을 수 있도록 지원합니다. 사용자는 동의 화면에서 서비스의 카카오톡 채널을 친구로 추가할 수도 있습니다.

3. 반갑습니다! 회원이 되신 것을 환영합니다.(문구) : 서비스는 카카오에 로그인한 사용자의 사용자 정보 제공을 요청합니다. 카카오싱크 도입 서비스는 일반적인 회원 가입 시 필요한 사용자 정보들을 카카오로부터 제공받을 수 있습니다. 서비스는 제공받은 사용자 정보로 별도 회원 정보 입력 과정을 거치지 않고 즉시 회원가입 처리를 완료할 수 있습니다.

상세 내용:위와 같이 카카오싱크는 사용자가 한 번의 동의 과정만으로도 서비스의 신규 회원으로 가입할 수 있도록 지원합니다. 또한 카카오싱크 간편가입 사용자는 가입 이후에도 ID 및 비밀번호를 입력하는 대신 카카오 로그인을 통해 서비스에 손쉽게 로그인할 수 있습니다.

서비스는 카카오가 제공하는 API를 통해 회원가입에 필요한 계정 입력 방식의 로그인 과정이나 사용자 정보 입력 절차 등을 최대한 간소화하여 보다 손쉽게 모객을 할 수 있습니다.

이밖에, 카카오싱크 서비스는 카카오톡 채널, 카카오 비즈보드, 챗봇 등 다양한 카카오 마케팅 설루션을 더욱 효과적으로 사용할 수 있습니다. 자세한 안내는 마케팅 가이드를 참고합니다. 카카오비즈니스에서도 카카오싱크에 대한 자세한 소개를 만나볼 수 있습니다. 

위 과정 예시에 대한 내용을 잘 숙지하고 유저가 물어보면 대답해줄 수 있도록 해줘.
"""

STEP_4 = """
#도입 안내
서비스에 카카오싱크를 도입하는 과정을 안내합니다.

1. 카카오싱크 신청 시작 : 카카오비즈니스 관리자센터에서 서비스의 사업자 계정으로 로그인한 후, [카카오싱크 신청] 메뉴를 선택합니다. 카카오싱크 도입 서비스의 오류 발생 시 빠른 지원을 위한 연락처를 입력해야 합니다. 카카오계정에 인증된 연락처가 없는 경우 아래와 같이 연락처 인증 및 등록 절차가 진행됩니다. 인증된 연락처가 등록되어 있는 경우에는 바로 카카오싱크 신청이 가능합니다.

2. 쇼핑몰 호스팅 서비스 사용 여부 선택: 쇼핑몰 호스팅 서비스(이하 호스팅사) 사용 여부를 선택합니다. 호스팅사 사용 여부는 최초 선택 이후 변경 불가이므로 유의합니다. 호스팅사를 이용하지 않고 자체적으로 사이트를 개발 및 운영하고 있다면 [호스팅사에 속하지 않는 독립몰]을 선택합니다. 호스팅사를 이용 중인 경우, [호스팅사를 이용하고 있는 경우]를 선택하고, 사용 중인 호스팅사를 선택합니다. 사용 중인 호스팅사가 카카오와 직접 연동되어 있는 제휴사라면 카카오싱크 간편 설정 팝업을 통해 카카오싱크 도입이 가능하므로, 카카오비즈니스 관리자센터에서는 CI에 대한 검수만 필요에 따라 진행합니다. 이 외 호스팅사의 경우 카카오싱크가 지원되지 않으므로, 해당 호스팅사에 카카오싱크 도입 가능 시점을 문의합니다.

3. 개인정보제공 항목 검수: 카카오싱크를 처음 도입한다면 개인정보제공 항목 검수를 통해 서비스에 필요한 사용자 정보 사용을 신청합니다. 일부 사용자 정보는 반드시 검수를 거쳐야 제공받을 수 있습니다. 카카오는 뚜렷한 용도 없이 지나치게 많은 사용자 정보를 제공하는 것을 지양하며, 사용자 정보 보호를 위해 사용자 정보 제공 전 검수를 진행합니다. 검수 완료 후, 서비스 앱에 필요한 사용자 정보를 [필수] 또는 [선택] 동의 항목으로 설정할 수 있는 권한을 부여합니다. 동의 항목은 사용자 정보를 제공받기 위한 앱 설정입니다. [선택] 사용자 정보는 사용자가 동의하지 않아도 카카오싱크 간편가입을 완료할 수 있는 항목에 해당합니다. [선택]인 사용자 정보는 사용자 동의 여부에 따라 카카오로부터 제공받을 수 없는 경우가 있으므로, 서비스 가입 및 이용에 꼭 필요한 사용자 정보는 [선택]으로 설정하지 않아야 합니다. [필수] 및 [선택] 여부는 신중히 판단하고 사용 신청해야 합니다. 사용 신청된 사용자 정보의 용도가 명확하지 않거나 부적절다면 검수 시 반려될 수 있습니다. 예를 들어 배송지 정보를 의류 등 물건을 파는 쇼핑몰에서 사용 신청한다면 문제가 없지만, 배송지 정보가 불필요한 서비스에서 사용 신청한다면 검수 시 반려됩니다. 카카오는 검수 시 서비스에서 각 사용자 정보가 어떤 용도로 쓰이는지 확인하므로, 수집 사유를 반드시 입력해야 합니다. 서비스 회원가입 시 수집하는 항목을 확인할 수 있는 서비스 회원가입 페이지의 URL, 수집 사유를 증빙할 수 있는 확인 자료를 함께 첨부합니다. 사이트 개발 등으로 확인 자료 첨부가 어려울 경우, 기획안 또는 디자인 시안으로 대체할 수 있습니다. 모든 항목을 설정 완료한 후 [신청하기]를 눌러 검수를 요청합니다. 검수에 소요되는 기간은 영업일 기준 3~5일입니다. 카카오는 검수 시 입력된 정보와 추가 자료는 물론, 현재 서비스의 회원 가입 기준이나 정보 활용 범위가 사용 신청 내역과 일치하는지 두루 확인합니다.
위 도입 안내에 대한 내용을 잘 숙지하고 유저가 물어보면 대답해줄 수 있도록 해줘.
"""

STEP_5 = """
#설정 안내
카카오싱크 신청 및 검수 완료 후, 다음 설정을 완료해야 카카오싱크 연동 개발을 진행할 수 있습니다.

항목 | 설명 | 참고
기본 정보 | 카카오싱크 간편가입 동의 화면에 노출할 서비스 정보 설정. 앱 이름, 아이콘, 회사명이 실제 서비스와 일치하도록 설정. 설정 경로: [내 애플리케이션] > [일반] | 애플리케이션
테스트 환경 | 이미 카카오 로그인을 이용 중인 서비스인 경우, 서비스 환경에 영향을 주지 않도록 테스트 앱, 개발자용 채널을 생성하여 카카오싱크 연동 개발 가능. 아직 카카오 로그인을 이용 중이지 않은 서비스라도 필요에 따라 테스트 앱 생성 및 사용 가능. 설정 경로: [내 애플리케이션] > [카카오 로그인]	| 테스트 앱  개발자용 채널
카카오 로그인 | 카카오싱크 간편가입을 사용하기 위해 카카오 로그인 활성화 필요. 이미 카카오 로그인을 사용 중인 서비스는 활성화 상태로 유지. 네이티브 앱이 아닌 웹 서비스인 경우, 카카오 로그인 Redirect URI 등록 필요. 설정 경로: [내 애플리케이션] > [카카오 로그인] | 카카오 로그인 활성화 설정. Redirect URI 등록
간편가입 | 카카오싱크 간편가입 사용 및 서비스 약관 설정. 간편가입 사용하도록 설정 시 동의 화면에 서비스 약관 동의 항목 노출. 카카오싱크 간편가입 동의 화면에 노출해 사용자로부터 동의받을 서비스 약관 등록 및 관리. 설정 경로: [내 애플리케이션] > [카카오 로그인] > [간편가입] | 간편가입 간편가입 사용 설정
동의 항목 | 카카오로부터 제공받고자 하는 사용자 정보 및 기능에 대한 동의 항목 설정. 동의 화면에 노출할 동의 항목 설정을 통해 사용자 동의를 거쳐 카카오로부터 정보를 제공받을 수 있음. 각 동의 항목의 설정 권한은 카카오싱크 도입 시 사용 신청한 내역 반영. 일부 동의 항목은 별도 검수가 필요하므로, 참고 문서에서 설정 권한 획득 방법 확인 설정 경로: [내 애플리케이션] > [카카오 로그인] | 동의 항목
대표 채널 | 카카오싱크 간편가입 동의 화면에 노출할 대표 채널 설정. 설정 경로: [내 애플리케이션] > [카카오 로그인] > [카카오톡 채널] | 대표 채널 설정
위 설정 안내에 대한 내용을 잘 숙지하고 유저가 물어보면 대답해줄 수 있도록 해줘.
"""

QUESTION = """
유저가 질문한 "{question}"에 대해 앞선 내용을 참고하여 답변해주세요.
"""

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

def create_chain(llm, template, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=template,
        ),
        output_key=output_key,
        verbose=True,
    )

def generate_answer(question) -> dict[str, str]:
  writer_llm = ChatOpenAI(temperature=0.1, max_tokens=2000, model='gpt-3.5-turbo')

  step1 = create_chain(writer_llm, STEP_1, "step1")
  step2 = create_chain(writer_llm, STEP_2, "step2")
  step3 = create_chain(writer_llm, STEP_3, "step3")
  step4 = create_chain(writer_llm, STEP_4, "step4")
  step5 = create_chain(writer_llm, STEP_5, "step5")
  questionSTEP = create_chain(writer_llm, QUESTION, "answer")

  preprocess_chain = SequentialChain(
      chains=[
          step1,
          step2,
          step3,
          step4,
          step5,
          questionSTEP
      ],
      input_variables=["question"],
      output_variables=["answer"],
      verbose=True,
  )

  context = dict(
      question=question,
  )
  context = preprocess_chain(context)
  return context['answer']


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
