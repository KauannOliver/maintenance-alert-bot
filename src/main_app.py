from src.telegram.bot_app import BotApp

class OMSentinelApp:
    def __init__(self):
        self.bot = BotApp()

    def run(self):
        self.bot.run()
