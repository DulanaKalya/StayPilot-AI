from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.infrastructure.llm import get_llm
from src.prompts.concierge import CONCIERGE_SYSTEM_PROMPT


class ChatService:

    def __init__(self):

        self.llm = get_llm()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CONCIERGE_SYSTEM_PROMPT),
            ("human", "{message}")
        ])

        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )

    def chat(self, message: str) -> str:

        return self.chain.invoke({
            "message": message
        })

    async def achat(self, message: str) -> str:

        return await self.chain.ainvoke({
            "message": message
        })

    def stream(self, message: str):

        yield from self.chain.stream({
            "message": message
        })

    async def astream(self, message: str):

        async for chunk in self.chain.astream({
            "message": message
        }):
            yield chunk