
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.db import IntegrityError


from . import utils, data


@api_view(['POST', 'GET'])
@permission_classes((AllowAny,))
def user_bot_webhook(request):

    if request.data.get('my_chat_member'):
        update = request.data.get('my_chat_member')
        chat = update.get('chat')
        user = update.get('from')
        if chat.get('type') == 'channel' and utils.get_user(user.get('id')):
            if update.get('new_chat_member') and update.get('new_chat_member').get('status') == 'administrator':
                utils.add_feed_channel(user.get('id'), chat.get(
                    'id'), chat.get('title'), chat.get('username'))
                buttons = [[{'text': 'Add Channels'}, {
                    'text': 'List Current Channels'}]]
                utils.send_message(user_id=user.get(
                    'id'), text="The bot was successfully added to your channel.", buttons=buttons)
            elif update.get('new_chat_member') and update.get('new_chat_member').get('status') == 'left':
                user_object = utils.get_user(user.get('id'))
                if user_object.feed_channel_id == str(chat.get('id')):
                    utils.remove_feed_channel(user.get('id'))
                utils.send_message(user_id=user.get(
                    'id'), text="The bot was successfully removed from your channel.")

    if request.data.get('message'):
        user_id = request.data.get('message').get('from').get('id')
        first_name = request.data.get('message').get('from').get('first_name')
        message = request.data.get('message').get('text')

        # If the message is a '/start' message
        if message == '/start':
            if not utils.get_user(user_id):
                utils.create_user(user_id=user_id, first_name=first_name)
                text = f"Welcome {first_name}.\n\nPlease create a new public channel, and add this bot as an admin."
                utils.send_message(user_id, text)
        # If the message is Add Channels
        if utils.get_user(user_id) and utils.get_user(user_id).feed_channel_id:

            if not utils.get_temp_data(user_id):
                if message == 'Add Channels':
                    temp_data = utils.create_temp_data(user_id)
                    active_question = data.CHANNEL_FEED_FORM_QUESTIONS[temp_data.active_question]
                    utils.send_message(
                        user_id, active_question)
                elif message == 'List Channels':
                    utils.send_message(
                        user_id, 'Here is a list of your channels')
            else:
                temp_data = utils.get_temp_data(user_id)
                if temp_data.active_question == 0:
                    if utils.check_channel(message):
                        utils.populate_form(
                            temp_data.active_question, user_id, message)
                    else:
                        buttons = [[{'text': 'Add Channels'}, {
                            'text': 'List Current Channels'}]]
                        utils.send_message(
                            user_id, "This channel doesn't exist.", buttons=buttons)
                        temp_data.delete()
                        return Response(data='Done')
                if temp_data.active_question == len(data.CHANNEL_FEED_FORM_QUESTIONS) - 1:
                    buttons = [[{'text': 'Add Channels'}, {
                        'text': 'List Current Channels'}]]
                    utils.send_message(
                        user_id, "A new channel was succesfully added.", buttons=buttons)
                    temp_data.delete()
                elif temp_data.active_question != 0:
                    utils.populate_form(
                        temp_data.active_question, user_id, message)
                    temp_data.active_question = temp_data.active_question + 1
                    temp_data.save()
                    active_question = data.CHANNEL_FEED_FORM_QUESTIONS[temp_data.active_question]
                    utils.send_message(user_id, active_question)

    return Response(data='Done')
