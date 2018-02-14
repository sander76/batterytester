import telepot.aio

H1_FORMAT = '<h1>{}</h1>'
P_FORMAT = '<p>{}</p>'


def notify_format(test_name, message, idx, loop):
    message = [H1_FORMAT.format(test_name), P_FORMAT.format(message)]
    if idx is not None:
        message.append(P_FORMAT.format(idx))
    if loop is not None:
        message.append(P_FORMAT.format(loop))
    return ''.join(message)


def notify_fail(test_name, message, idx, loop):
    _message = H1_FORMAT.format('fail') + notify_format(test_name, message,
                                                        idx, loop)
    return _message


class BaseNotifier:
    def __init__(self, test_name=None):
        self._test_name = test_name

    async def notify(self, message, idx=None, loop=None):
        pass

    async def notify_fail(self, message, idx=None, loop=None):
        pass


class TelegramNotifier(BaseNotifier):
    def __init__(self, loop, token=None, chat_id=None, test_name=None):
        super().__init__(test_name)
        self.bot = telepot.aio.Bot(token, loop)
        self.chat_id = chat_id

    async def notify(self, message, idx=None, loop=None):
        await self.bot.sendMessage(self.chat_id,
                                   notify_format(self._test_name, message, idx,
                                                 loop),
                                   parse_mode='html')

    async def notify_fail(self, message, idx=None, loop=None):
        await self.bot.sendMessage(self.chat_id,
                                   notify_fail(self._test_name, message, idx,
                                               loop),
                                   parse_mode='html')
