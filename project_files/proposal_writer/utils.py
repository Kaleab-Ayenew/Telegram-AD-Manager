from modules.global_utils.utils import BotMessage, bot_request
from . import data
BOT_TOKEN = "6146233872:AAFUEzYZZV9mDgo5jML0eNQaRkJo8CPNu24"


def send_message(user_id, text, buttons=None):
    user_id = user_id
    message = BotMessage(user=user_id, message=text)
    if buttons:
        message.add_keyboard(keyboard_type='keyboard', data_array=buttons)
    rsp = message.send(BOT_TOKEN)
    print(rsp.json())
    return rsp


def edit_message(user_id, msg_id, text, buttons=None):
    rsp = bot_request(token=BOT_TOKEN, endpoint="editMessageText", data={
                      "chat_id": user_id, "text": text, "message_id": msg_id})
    print(rsp.json())
    return rsp.json()


def split_job(job):
    sentence_list = job.split(". ")
    list_len = len(sentence_list)

    p1 = sentence_list[:list_len//2]
    p2 = sentence_list[list_len//2:]

    sent_p1 = ". ".join(p1)
    sent_p2 = ". ".join(p2)
    return (sent_p1, sent_p2)


def get_proposal_prompt(job):

    prompt = f"""
    I want to apply for the following job position:
    
    ***
    {job}
    ***
    
    I have been asked to do the following by the recruiter to do the following:
    
    ***
    {data.RECRUITER_INSTRUCTION}
    ***
    
    Write me an application letter based on the recruiter's instructions.
    Don’t include anything in your response but the letter that I am going to send for my recruiter. 
    When you send me the letter, enclose the text in three quotes.
    """

    return prompt


def get_split_prompt(job):
    split_job_sent = split_job(job)
    prompt_1 = f"""
    Here is a job posting for a position that I want to apply for. I have attached the first part here. Next you will ask me for the second part, and I will send it to you.
    ***
    {split_job_sent[0]}
    ***
    """
    prompt_2 = f"""
    ***
    {split_job_sent[1]}
    ***
    
    I have been asked to do the following by the recruiter to do the following:
    
    ***
    {data.RECRUITER_INSTRUCTION}
    ***
    
    Write me an application letter based on the recruiter's instructions.
    Don’t include anything in your response but the letter that I am going to send for my recruiter. 
    When you send me the letter, enclose the text in three quotes.
    """

    return (prompt_1, prompt_2)
