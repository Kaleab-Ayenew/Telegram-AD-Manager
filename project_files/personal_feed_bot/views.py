
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
                buttons = data.BUTTON_LIST[0]
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

                ##########################
                #### ADD A CHANNEL ####
                if message == 'Add Channels':
                    temp_data = utils.create_temp_data(
                        user_id, form_name='add_channel')
                    active_question = data.ADD_CHANNEL_FORM[temp_data.active_question]
                    utils.send_message(
                        user_id, active_question)

                ##########################
                #### LIST CHANNELS ####
                elif message == 'List Channels':
                    temp_data = utils.create_temp_data(
                        user_id, form_name='list_channels')
                    channel_list = utils.list_connected_channel(user_id)

                    if channel_list is not None:
                        buttons = utils.list_to_button(channel_list)
                        print('Buttons first', buttons)
                        print(buttons, 'There are the buttons')
                        utils.send_message(
                            user_id, 'Here is a list of your channels', buttons=buttons)
                        temp_data.save()
                        return Response(data='Done')
                    else:
                        utils.send_message(
                            user_id, 'No channels to show [List Channel]', buttons=data.BUTTON_LIST[0])
                        temp_data.delete()
                        return Response(data='Done')

                ##########################
                #### REMOVE A CHANNEL ####
                elif message == 'Remove a Channel':
                    temp_data = utils.create_temp_data(
                        user_id, form_name='remove_channel')
                    channel_list = utils.list_connected_channel(
                        user_id)
                    print("I was here")

                    if channel_list is not None:
                        buttons = utils.list_to_button(channel_list)
                        print('Buttons first', buttons)
                        print(buttons, 'There are the buttons')
                        utils.send_message(
                            user_id, 'Choose the channel you want to delete[1]', buttons=buttons)
                        temp_data.save()
                        return Response(data='Done')
                    else:
                        utils.send_message(
                            user_id, 'No channels to remove [1]', buttons=data.BUTTON_LIST[0])
                        temp_data.delete()
                        return Response(data='Done')

            else:
                temp_data = utils.get_temp_data(user_id)

                if message == 'Back to Home':
                    utils.send_message(
                        user_id, 'Welcome to FeedGram ETH bot!\nWhat do you want to do?', buttons=data.BUTTON_LIST[0])
                    temp_data.delete()
                    return Response(data='Done')

                # ADD_CHANNEL: If the user wants to add a channel
                if temp_data.form_name == 'add_channel':

                    if temp_data.active_question == 0:

                        if utils.get_connected_channel(user_id, message):
                            utils.send_message(
                                user_id, "This channel already exists. [ADD_CHANNEL]", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data='Done')

                        if utils.check_channel(message):
                            utils.add_connected_channel(user_id, message)
                            buttons = data.BUTTON_LIST[0]
                            utils.send_message(
                                user_id, "A new channel was succesfully added. [ADD_CHANNEL]", buttons=buttons)
                            temp_data.delete()
                            return Response(data='Done')

                        else:
                            buttons = data.BUTTON_LIST[0]
                            utils.send_message(
                                user_id, "This channel doesn't exist. [ADD_CHANNEL]", buttons=buttons)
                            temp_data.delete()
                            return Response(data='Done')

                # REMOVE_CHANNEL: If the user wants to remove a channel
                elif temp_data.form_name == 'remove_channel':

                    ###########################
                    ###### More Channels ######
                    if message == 'More Channels':
                        temp_data.active_question = temp_data.active_question + 1
                        temp_data.save()
                        channel_list = utils.list_connected_channel(
                            user_id)
                        if channel_list is not None:
                            buttons = utils.list_to_button(
                                channel_list, temp_data.active_question)
                            utils.send_message(
                                user_id, 'Choose the channel you want to delete', buttons=buttons)
                            return Response(data='Done')
                        else:
                            utils.send_message(
                                user_id, 'No channels to remove', buttons=data.BUTTON_LIST[0])
                            return Response(data='Done')

                    elif message == "Previous Channels":
                        print("I am at previous channels")
                        temp_data.active_question = temp_data.active_question - 1
                        temp_data.save()
                        channel_list = utils.list_connected_channel(
                            user_id)

                        if channel_list is not None:
                            buttons = utils.list_to_button(
                                channel_list, temp_data.active_question)
                            utils.send_message(
                                user_id, 'Choose the channel you want to delete', buttons=buttons)
                            return Response(data='Done')
                        else:
                            utils.send_message(
                                user_id, 'No channels to remove', buttons=data.BUTTON_LIST[0])
                            return Response(data='Done')

                    ###########################
                    ###### Delete Channel #####
                    if utils.get_connected_channel(user_id, message):
                        utils.remove_connected_channel(user_id, message)
                        utils.send_message(
                            user_id, f'Channel {message} was removed succesfully. [REMOVE_CHANNEL]', buttons=data.BUTTON_LIST[0])
                        temp_data.delete()
                        return Response(data='Done')
                    else:
                        utils.send_message(
                            user_id, "This channel doesn't exist. [REMOVE_CHANNEL]", buttons=data.BUTTON_LIST[0])
                        temp_data.delete()
                        return Response(data='Done')
                    ##########################

                # LIST_CHANNEL: If the user wants to list a channels
                elif temp_data.form_name == 'list_channels':

                    if message == 'More Channels':
                        temp_data.active_question = temp_data.active_question + 1
                        temp_data.save()
                        channel_list = utils.list_connected_channel(
                            user_id)
                        if channel_list is not None:
                            buttons = utils.list_to_button(
                                channel_list, temp_data.active_question)
                            utils.send_message(
                                user_id, 'Here is a list of your channels', buttons=buttons)
                            return Response(data='Done')
                        else:
                            utils.send_message(
                                user_id, 'No channels to show', buttons=data.BUTTON_LIST[0])
                            return Response(data='Done')

                    elif message == "Previous Channels":
                        print("I am at previous channels - LIST CHANNEL")
                        temp_data.active_question = temp_data.active_question - 1
                        temp_data.save()
                        channel_list = utils.list_connected_channel(
                            user_id)

                        if channel_list is not None:
                            buttons = utils.list_to_button(
                                channel_list, temp_data.active_question)
                            utils.send_message(
                                user_id, 'Here is a list of your channels', buttons=buttons)
                            return Response(data='Done')
                        else:
                            utils.send_message(
                                user_id, 'No channels to show', buttons=data.BUTTON_LIST[0])
                            return Response(data='Done')

    return Response(data='Done')
