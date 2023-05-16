from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from . import utils
from .edge import main
import asyncio


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_proposal(request):
    user = request.data.get('message').get('from').get('id')
    text = request.data.get('message').get('text')

    if text == "/start":
        utils.send_message(
            user, "✨Welcome to AI Proposal Writer Bot!✨\n\nForward me the job post to generate a proposal letter.")
        return Response(data="Done")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    utils.send_message(user, "Generating Job Proposal...")
    if len(utils.get_proposal_prompt(text)) <= 2000:
        prompt = utils.get_proposal_prompt(text)
        result = loop.run_until_complete(main(prompt))
        rsp = utils.send_message(user, result)
        print(rsp.json())
        return Response(data="Done")
    else:
        prompt = utils.get_split_prompt(text)
        result = loop.run_until_complete(main(prompt=prompt, multiple=True))
        rsp = utils.send_message(user, result)
        print(rsp.json())
        return Response(data="Done")
