import telepot.aio


class BaseNotifier:
    async def notify(self, message, idx=None, loop=None):
        pass

    async def notify_fail(self, message, idx=None, loop=None):
        pass


class TelegramNotifier(BaseNotifier):
    def __init__(self, loop, token=None, chat_id=None):
        self.bot = telepot.aio.Bot(token, loop)
        self.chat_id = chat_id

    async def notify(self, message, idx=None, loop=None):
        await self.bot.sendMessage(self.chat_id, message,parse_mode='markdown')

    async def notify_fail(self, message, idx=None, loop=None):
        await self.bot.sendMessage(self.chat_id, message,parse_mode='markdown')
