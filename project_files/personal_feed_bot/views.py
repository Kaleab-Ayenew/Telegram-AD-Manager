
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
        user_id = user.get('id')
        if chat.get('type') == 'channel' and utils.get_user(user.get('id')):
            if update.get('new_chat_member') and update.get('new_chat_member').get('status') == 'administrator':
                # if utils.get_user(user_id) and not utils.get_user(user_id).feed_channel_id:
                if utils.get_user(user_id):
                    utils.add_feed_channel(user.get('id'), chat.get(
                        'id'), chat.get('title'), chat.get('username'))
                    buttons = data.BUTTON_LIST[0]
                    utils.send_message(user_id=user.get(
                        'id'), text="The bot was successfully added to your channel.", buttons=buttons)
                    return Response(data='Done')
                else:
                    return Response(data='Done')

                # elif utils.get_user(user_id) and utils.get_user(user_id).feed_channel_id:
                #     buttons = data.BUTTON_LIST[0]
                #     utils.send_message(user_id=user.get(
                #         'id'), text="Sorry, you cannot add more than one channel.", buttons=buttons)
                #     return Response(data='Done')

            elif update.get('new_chat_member') and update.get('new_chat_member').get('status') == 'left':
                user_feed_channels = [
                    int(ch.feed_channel_id) for ch in utils.list_feed_channels(user.get('id'))]
                if str(chat.get('id')) in user_feed_channels:
                    utils.remove_feed_channel(user.get('id'), chat.get('id'))
                    utils.send_message(user_id=user.get(
                        'id'), text="The bot was successfully removed from your channel.")
                    return Response(data='Done')

    if request.data.get('message'):
        user_id = request.data.get('message').get('from').get('id')
        first_name = request.data.get('message').get('from').get('first_name')
        message = request.data.get('message').get('text')

        # If the user is not registered
        if not utils.get_user(user_id):
            utils.create_user(user_id=user_id, first_name=first_name)
            text = f"Welcome {first_name}.\n\nPlease create a new public channel, and add this bot as an admin."
            utils.send_message(user_id, text)
            return Response(data='Done')

        # If the user didn't add a channel
        if not utils.list_feed_channels(user_id):
            text = "Please create a new channel and add this bot as an admin!"
            utils.send_message(user_id, text)
            return Response(data='Done')

        if utils.get_user(user_id) and utils.list_feed_channels(user_id):

            if not utils.get_temp_data(user_id):

                #######################
                #### ADD A CHANNEL ####
                if message == 'Add Channels':
                    temp_data = utils.create_temp_data(
                        user_id, form_name='add_channel')
                    active_question = "Choose a feed channel:"
                    user_feed_channels = [
                        ch.feed_channel_name for ch in utils.list_feed_channels(user_id)]
                    buttons = utils.list_to_button(user_feed_channels)
                    utils.send_message(
                        user_id, active_question, buttons)

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
                        if utils.get_feed_channel_by_name(user_id, message):
                            temp_data.data = utils.get_feed_channel_by_name(
                                user_id, message).feed_channel_id
                            temp_data.save()
                            utils.send_message(
                                user_id, "Send the username of the channel you want to add to your feed.\nExample: `tikvahethiopia`")
                            return Response(data='Done')
                        else:
                            utils.send_message(
                                user_id, "This channel is not in your feed.", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data="Done")

                    if temp_data.active_question == 1:

                        if utils.get_connected_channel(user_id, message):
                            utils.send_message(
                                user_id, "This channel already exists.", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data='Done')

                        if utils.check_channel(message):
                            feed_ch_id = str(temp_data.data)
                            utils.add_connected_channel(
                                user_id, feed_ch_id, message)
                            buttons = data.BUTTON_LIST[0]
                            utils.send_message(
                                user_id, f"A new channel was succesfully added to channel: {feed_ch_id}", buttons=buttons)
                            temp_data.delete()
                            return Response(data='Done')

                        else:
                            buttons = data.BUTTON_LIST[0]
                            utils.send_message(
                                user_id, "This channel doesn't exist.", buttons=buttons)
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
                    else:
                        utils.send_message(
                            user_id, 'Welcome to FeedGram ETH bot!\nWhat do you want to do?', buttons=data.BUTTON_LIST[0])
                        temp_data.delete()
                        return Response(data='Done')

                    ###########################
                    ###### Delete Channel #####
                    if utils.get_connected_channel(user_id, message):
                        utils.remove_connected_channel(user_id, message)
                        utils.send_message(
                            user_id, f'Channel {message} was removed succesfully.', buttons=data.BUTTON_LIST[0])
                        temp_data.delete()
                        return Response(data='Done')
                    else:
                        utils.send_message(
                            user_id, "This channel doesn't exist.", buttons=data.BUTTON_LIST[0])
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
                    else:
                        utils.send_message(
                            user_id, 'Welcome to FeedGram ETH bot!\nWhat do you want to do?', buttons=data.BUTTON_LIST[0])
                        temp_data.delete()
                        return Response(data='Done')
                else:
                    utils.send_message(
                        user_id, 'Welcome to FeedGram ETH bot!\nWhat do you want to do?', buttons=data.BUTTON_LIST[0])
                    temp_data.delete()
                    return Response(data='Done')

    return Response(data='Done')
