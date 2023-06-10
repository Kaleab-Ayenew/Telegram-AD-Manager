
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny


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

                    if utils.check_feed_limit(user_id):
                        if not chat.get('username'):
                            utils.send_message(user_id=user.get(
                            'id'), text=f"⛔️ የፈጠሩት ቻናል username የለውም። ⛔️\n\n❇️ እባክዎን ለቻናሉ username ሰጥተው ቦቱን እንደገና add ያድርጉት።\n\n")
                            return Response(data='Done')
                        new_ch = utils.add_feed_channel(user.get('id'), chat.get(
                            'id'), chat.get('title'), chat.get('username'))
                        buttons = data.BUTTON_LIST[0]
                        utils.send_message(user_id=user.get(
                            'id'), text=f"❇️ {new_ch.feed_channel_name} በስኬት ወደ Super Channel ዝርዝር ተጨምሯል።", buttons=buttons)
                        return Response(data='Done')
                    else:
                        utils.send_message(
                            user_id=user_id, text=f"⛔️ መጨመር የሚችሉትን የSuper Channel ገደብ አልፈዋል።\n\n❇️ ተጨማሪ Super Channelኦችን ለማካተት 'ልዩ ፓኬጅ ለመግዛት' የሚለውን ተጭነው Basic ወይንም Advanced ፓኬጅ ይግዙ።\n\n", buttons=data.SEE_SUB_BUTTON)
                        return Response(data='Done')
                else:
                    return Response(data='Done')

                # elif utils.get_user(user_id) and utils.get_user(user_id).feed_channel_id:
                #     buttons = data.BUTTON_LIST[0]
                #     utils.send_message(user_id=user.get(
                #         'id'), text="Sorry, you cannot add more than one channel.", buttons=buttons)
                #     return Response(data='Done')

            elif update.get('new_chat_member') and update.get('new_chat_member').get('status') == 'left':
                if utils.get_feed_channel_by_id(user.get('id'), chat.get('id')):
                    fd_ch_nm = utils.get_feed_channel_by_id(user.get('id'), chat.get('id')).feed_channel_name
                    utils.remove_feed_channel(user.get('id'), chat.get('id'))
                    utils.send_message(user_id=user.get(
                        'id'), text=f"❇️ {fd_ch_nm} የተሰኘው Super Channel በስኬት ተወግዷል።", buttons=data.BUTTON_LIST[0])
                    return Response(data='Done')

    if request.data.get('message'):
        user_id = request.data.get('message').get('from').get('id')
        first_name = request.data.get('message').get('from').get('first_name')
        message = request.data.get('message').get('text')

        # If the user is not registered
        if not utils.get_user(user_id):
            utils.create_user(user_id=user_id, first_name=first_name)
            text = f"እንኳን ደህና መጡ 💖{first_name}💖.\n\nአዲስ ቻናል ከፍተው ይሄን ቦት የቻናሉ admin ያድርጉት።\n\n🛑 ማሳሰቢያ: አዲሱ ቻናል username ያለው ወይንም public ሊሆን ይገባል።"
            utils.send_message(user_id, text)
            return Response(data='Done')

        # If the user didn't add a channel
        if not utils.list_feed_channels(user_id):
            text = "እባክዎን አዲስ ቻናል ከፍተው ይሄን ቦት የቻናሉ admin ያድርጉት።\n\n🛑 ማሳሰቢያ: አዲሱ ቻናል username ያለው ወይንም public ሊሆን ይገባል።"
            utils.send_message(user_id, text)
            return Response(data='Done')

        if utils.get_user(user_id) and utils.list_feed_channels(user_id):
            
            

            if not utils.get_temp_data(user_id):

                if message == '🏠 ዋና ማውጫ 🏠' or message == '🤠 የእርስዎ መረጃ 🤠':
                    text = utils.get_homepage_info(user_id)
                    utils.send_message(
                        user_id, text, buttons=data.BUTTON_LIST[0])
                    return Response(data='Done')

                #######################
                #### ADD A CHANNEL ####
                if message == '🆕 ቻናል ለመጨመር':
                    temp_data = utils.create_temp_data(
                        user_id, form_name='add_channel')
                    active_question = "ቻናሉን የሚጨምሩት ወደ የትኛው Super Channel ነው?\n\n❇️ ከታች ከተዘረዘሩት አንዱን ይምረጡ:"
                    user_feed_channels = [
                        ch.feed_channel_name for ch in utils.list_feed_channels(user_id)]
                    buttons = utils.normal_list_to_button(user_feed_channels)
                    buttons.append(data.BACK_TO_HOME_BUTTON)
                    utils.send_message(
                        user_id, active_question, buttons)


                ##########################
                #### REMOVE A CHANNEL ####
                elif message == '🗑 ቻናል ለመቀነስ':
                    temp_data = utils.create_temp_data(
                        user_id, form_name='remove_channel')

                    active_question = "ቻናሉን የሚቀንሱት ከየትኛው Super Channel ነው?\n\n❇️ ከታች ከተዘረዘሩት Super Channelኦች አንዱን ይምረጡ:"
                    user_feed_channels = [
                        ch.feed_channel_name for ch in utils.list_feed_channels(user_id)]
                    buttons = utils.normal_list_to_button(user_feed_channels)
                    buttons.append(data.BACK_TO_HOME_BUTTON)
                    utils.send_message(
                        user_id, active_question, buttons)
                    return Response(data='Done')
                
                elif message == "❇️ Super Channel ለመጨመር":
                    text = "❇️ Super Channel ለመጨመር አዲስ ቻናል ፈጥረው ይሄንን ቦት ቻናሉ ላይ add ብለው admin ያድርጉት።\n\n🛑 ማሳሰቢያ: አዲሱ ቻናል username ያለው ወይንም public ሊሆን ይገባል።"
                    utils.send_message(
                        user_id, text)
                    return Response(data='Done')
                
                elif message == "❌ Super Channel ለመቀነስ":
                    temp_data = utils.create_temp_data(
                        user_id, form_name='disconnect_super_channel')
                    active_question = "የትኛውን Super Channel ነው የሚያስወግዱት?\n\n❇️ ከታች ከተዘረዘሩት Super Channelኦች አንዱን ይምረጡ:"
                    user_feed_channels = [
                        ch.feed_channel_name for ch in utils.list_feed_channels(user_id)]
                    buttons = utils.normal_list_to_button(user_feed_channels)
                    buttons.append(data.BACK_TO_HOME_BUTTON)
                    utils.send_message(
                        user_id, active_question, buttons)
                    return Response(data='Done')
                    

                elif message == '🔥 ልዩ ፓኬጅ ለመግዛት 🔥':
                    utils.send_subscription_info(user_id)
                    return Response(data='Done')

                elif message == '⭐️ Basic Plan ለመግዛት':
                    utils.send_subscription(user_id, 'basic')
                    return Response(data='Done')

                elif message == '🌟 Advanced Plan ለመግዛት':
                    utils.send_subscription(user_id, 'advanced')
                    return Response(data='Done')
                
                else:
                    text = utils.get_homepage_info(user_id)
                    utils.send_message(
                        user_id, text, buttons=data.BUTTON_LIST[0])
                    return Response(data='Done')

            else:
                temp_data = utils.get_temp_data(user_id)

                if message == '🏠 ዋና ማውጫ 🏠' or message == '🤠 የእርስዎ መረጃ 🤠':
                    temp_data.delete()
                    text = utils.get_homepage_info(user_id)
                    utils.send_message(
                        user_id, text, buttons=data.BUTTON_LIST[0])
                    return Response(data='Done')

                # ADD_CHANNEL: If the user wants to add a channel
                if temp_data.form_name == 'add_channel':

                    if temp_data.active_question == 0:
                        if utils.get_feed_channel_by_name(user_id, message):
                            _feed_ch_id = utils.get_feed_channel_by_name(
                                user_id, message).feed_channel_id
                            if utils.check_connection_limit(user_id, _feed_ch_id):

                                temp_data.data = utils.get_feed_channel_by_name(
                                    user_id, message).feed_channel_id
                                temp_data.active_question = temp_data.active_question + 1
                                temp_data.save()
                                
                                utils.send_message(
                                    user_id, "❇️ የሚጨምሩትን ቻናል username ወይንም link ይላኩ።\n\n👉 ለምሳሌ: `https://t.me/tikvahethiopia` or `tikvahethiopia`")
                                return Response(data='Done')
                            else:
                                _feed_ch_name = utils.get_feed_channel_by_name(
                                    user_id, message).feed_channel_name
                                utils.send_message(
                                    user_id, f"🙂 {_feed_ch_name} ውስጥ መጨመር የሚችሉትን የቻናል ገደብ ጨርሰዋል። [{_feed_ch_name}]\n\n😃 ተጨማሪ ቻናሎችን ለመጨመር Basic ወይንም Advanced ልዩ ፓኬጅ ይግዙ።", buttons=data.SEE_SUB_BUTTON)
                                temp_data.delete()
                                return Response(data="Done")
                        else:
                            utils.send_message(
                                user_id, f"{message} የሚባል Super Channel አልፈጠሩም።\n\nእባክዎ ቻናሉን ይፍጠሩ እና ይሄን ቦት የቻናሉ አድሚን ያድርጉት።\n\n⛔️ ማሳሰቢያ: የሚፈጥሩት Super Channel username ሊኖረው ይገባል።", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data="Done")

                    if temp_data.active_question == 1:
                        message = utils.extract_username(message)
                        if utils.get_connected_channel(user_id, message, temp_data.data):
                            utils.send_message(
                                user_id, "⛔️ ይህን ቻናል ከዚህ በፊት ጨምረውታል።", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data='Done')

                        if utils.check_channel(message):
                            feed_ch_id = str(temp_data.data)
                            feed_ch_name = utils.get_feed_channel_by_id(user_id, feed_ch_id)
                            utils.add_connected_channel(
                                user_id, feed_ch_id, message)
                            buttons = data.BUTTON_LIST[0]
                            utils.send_message(
                                user_id, f"❇️ ቻናሉ ወደ {feed_ch_name} Super Channel በስኬት ተጨምሯል።", buttons=buttons)
                            temp_data.delete()
                            return Response(data='Done')

                        else:
                            buttons = data.BUTTON_LIST[0]
                            utils.send_message(
                                user_id, "⛔️ ይህን ቻናል ማግኘት አልተቻለም። እባክዎን ያስገቡት username ወይንም link ትክክለኛ መሆኑን ያረጋግጡ።", buttons=buttons)
                            temp_data.delete()
                            return Response(data='Done')

                # REMOVE_CHANNEL: If the user wants to remove a channel
                elif temp_data.form_name == 'remove_channel':

                    if temp_data.active_question == 0:

                        if utils.get_feed_channel_by_name(user_id, message):
                            _feed_ch_id = utils.get_feed_channel_by_name(
                                user_id, message).feed_channel_id

                            temp_data.data = _feed_ch_id

                            channel_list = utils.list_connected_channel_by_feed(
                                user_id, _feed_ch_id)

                            if channel_list is not None:
                                temp_data.active_question = temp_data.active_question + 1
                                buttons = utils.list_to_button(channel_list)
                                buttons.append(data.BACK_TO_HOME_BUTTON)
                                utils.send_message(
                                    user_id, '🗑 ለማስወገድ የሚፈልጉትን ቻናል ከታች ካለው ዝርዝር ይምረጡ:', buttons=buttons)
                                temp_data.save()
                                return Response(data='Done')
                            else:
                                utils.send_message(
                                    user_id, '⛔️ ይህ Super Channel ምንም ቻናል የለውም።', buttons=data.BUTTON_LIST[0])
                                temp_data.delete()
                                return Response(data='Done')

                        else:
                            utils.send_message(
                                user_id, "⛔️ ይህንን ቻናል በመረጡት Super Channel ውስጥ ማግኘት አልተቻለም። የቻናሉን username አረጋግጠው እንደገና ይሞክሩ።", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data="Done")

                    elif temp_data.active_question == 1:

                        ###########################
                        ###### More Channels ######
                        if message == 'More Channels':
                            temp_data.active_question = temp_data.active_question + 1
                            temp_data.save()
                            channel_list = utils.list_connected_channel_by_feed(
                                user_id, temp_data.data)
                            if channel_list is not None:
                                buttons = utils.list_to_button(
                                    channel_list, temp_data.active_question)
                                buttons.append(data.BACK_TO_HOME_BUTTON)
                                utils.send_message(
                                    user_id, '🗑 ለማስወገድ የሚፈልጉትን ቻናል ከታች ካለው ዝርዝር ይምረጡ:', buttons=buttons)
                                return Response(data='Done')
                            else:
                                utils.send_message(
                                    user_id, '⛔️ ይህ Super Channel ምንም ቻናል የለውም።', buttons=data.BUTTON_LIST[0])
                                return Response(data='Done')

                        elif message == "Previous Channels":
                            print("I am at previous channels")
                            temp_data.active_question = temp_data.active_question - 1
                            temp_data.save()
                            channel_list = utils.list_connected_channel_by_feed(
                                user_id, temp_data.data)

                            if channel_list is not None:
                                buttons = utils.list_to_button(
                                    channel_list, temp_data.active_question)
                                buttons.append(data.BACK_TO_HOME_BUTTON)
                                utils.send_message(
                                    user_id, '🗑 ለማስወገድ የሚፈልጉትን ቻናል ከታች ካለው ዝርዝር ይምረጡ:', buttons=buttons)
                                return Response(data='Done')
                            else:
                                utils.send_message(
                                    user_id, '⛔️ ይህ Super Channel ምንም ቻናል የለውም።', buttons=data.BUTTON_LIST[0])
                                return Response(data='Done')

                        ###########################
                        ###### Delete Channel #####
                        if utils.get_connected_channel(user_id, message, feed_channel_id=temp_data.data):
                            utils.remove_connected_channel(user_id, message, feed_channel_id=temp_data.data)
                            utils.send_message(
                                user_id, f'❇️ {message} የተሰኘው ቻናል በስኬት ተወግዷል።', buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data='Done')
                        else:
                            utils.send_message(
                                user_id, "⛔️ የመረጡትን ቻናል ማኝየት አልተቻለም።\n\nእባክዎን የመረጡትን username አረጋግጠው እንደገና ይሞክሩ።", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data='Done')
                        ##########################

                # Disconnect Super Channel
                elif temp_data.form_name == 'disconnect_super_channel':
                    if temp_data.active_question == 0:
                        if utils.get_feed_channel_by_name(user_id, message):
                            _feed_ch_id = utils.get_feed_channel_by_name(
                                user_id, message).feed_channel_id
                            utils.remove_feed_channel(user_id=user_id, ch_id=_feed_ch_id)
                            utils.send_message(
                                user_id, f'❇️ {message} የተሰኘው Super Channel በስኬት ተወግዷል።', buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data='Done')
                            
                        else:
                            utils.send_message(
                                user_id, f"⛔️ {message} የሚባል Super Channel አልፈጠሩም።", buttons=data.BUTTON_LIST[0])
                            temp_data.delete()
                            return Response(data="Done")
                        
                else:
                    utils.send_message(
                        user_id, utils.get_homepage_info(user_id), buttons=data.BUTTON_LIST[0])
                    temp_data.delete()
                    return Response(data='Done')

    return Response(data='Done')
