class MiniMaxProvider:
    def __init__(self):
        self.active = False

    async def chat(self, prompt: str, system_prompt: str):
        return None


minimax = MiniMaxProvider()
