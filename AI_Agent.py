from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class AI_Agent():
    def __init__(self, models : list[tuple[str, int]]) -> None:
        self.models = models 
        if len(self.models) == 0:
            self.index : int = - 1
        else:
            self.index : int = 0
            self.current_model = ChatGoogleGenerativeAI(
                model= self.models[self.index][0],
                temperature=0.7,
            )

    def get_model(self) -> str:
        if self.index >= len(self.models) or self.index < 0:
            return 'ERROR RAN OUT OF MODELS'
        return self.models[self.index][0]

    def next_index(self) -> int:
        if self.index >= len(self.models) - 1 or self.index < 0:
            self.index = -1
        else:
            self.index += 1
            self.current_model = ChatGoogleGenerativeAI(
                model= self.models[self.index][0],
                temperature=0.7,
            )

        return self.index

    def remaining_tokens(self) -> int:
        if self.index >= len(self.models) or self.index < 0:
            return -1
        return self.models[self.index][1]

    def update_model(self, prompt) -> None:
        tokens = self.current_model.get_num_tokens_from_messages(prompt)
        while tokens > self.models[self.index][1] and self.index != -1:
            self.next_index()
        if self.index == -1:
            raise Exception('Ran out of API tokens')
    def invoke(self, prompt) -> AIMessage:
        self.update_model(prompt)
        while self.index < len(self.models):
            try:
                response = self.current_model.invoke(prompt)
                return response
            except:
                self.next_index()
        raise Exception('Ran out of API calls')

    def stream(self, prompt):
        self.update_model(prompt)
        while self.index < len(self.models):
            try:
                response = self.current_model.stream(prompt)
                return response
            except:
                self.next_index()
        raise Exception('Ran out of API calls')