import slack_sdk
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import pandas as pd
import numpy as np
import re

palavras_df = pd.read_excel('palavras.xlsx')
du = np.asarray(palavras_df[['Palavras']])
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SLACK_SIGNING_SECRET'], '/slack/events', app)

client = slack_sdk.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    user_id = event.get('user')
    text = event.get('text').lower()
    badword = text.split()

    for i in badword:
        if i in du:
            motivo = np.asarray(palavras_df.loc[palavras_df['Palavras'] == i, ['Motivo']])
            rsp = re.sub("\[|\]|\'|", "", str(motivo))
            rsp = re.sub(";", '\n', str(rsp))
            if BOT_ID != user_id:
                client.chat_postMessage(channel=user_id, text=rsp)
            break


if __name__ == "__main__":
    app.run(debug=True)
