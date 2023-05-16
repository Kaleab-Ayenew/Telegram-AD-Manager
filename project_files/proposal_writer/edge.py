import asyncio
from EdgeGPT import Chatbot, ConversationStyle
import time
import os


async def main(prompt, multiple=False):
    cookie_path = os.path.join(os.path.dirname(
        __file__), 'other_files/cookie.json')
    bot = await Chatbot.create(cookie_path=cookie_path)
    print("Generating response")
    if not multiple:
        response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, wss_link="wss://sydney.bing.com/sydney/ChatHub")
        text_rsp = response.get('item').get('messages')[1].get('text')
        await bot.close()
        return text_rsp
    else:
        final_rsp = ""
        for p in prompt:
            response = await bot.ask(prompt=p, conversation_style=ConversationStyle.creative, wss_link="wss://sydney.bing.com/sydney/ChatHub")
            text_rsp = response.get('item').get('messages')[1].get('text')
            final_rsp = text_rsp
            print(text_rsp)
        await bot.close()
        return final_rsp
