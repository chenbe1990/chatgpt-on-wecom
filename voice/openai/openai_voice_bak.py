"""
google voice service
"""
import json

import openai

from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from voice.voice import Voice


class OpenaiVoice(Voice):
    def __init__(self,open_ai_api_base_Audio,open_ai_api_key_Audio):
        openai.api_key = open_ai_api_key_Audio
        openai.api_base = open_ai_api_base_Audio
    def voiceToText(self, voice_file):
        logger.debug("[Openai] voice file name={}".format(voice_file))
        try:
            file = open(voice_file, "rb")
            result = openai.Audio.transcribe("whisper-1", file)
            text = result["text"]
            reply = Reply(ReplyType.TEXT, text)
            logger.info("[Openai] voiceToText text={} voice file name={}".format(text, voice_file))
        except Exception as e:
            reply = Reply(ReplyType.ERROR, str(e))
        finally:
            return reply




openaivoice=OpenaiVoice(open_ai_api_base_Audio="http://38.6.172.103:9000/proxy/v1",open_ai_api_key_Audio="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")
result = openaivoice.voiceToText(r"C:\Users\Administrator\PycharmProjects\chatgpt-on-wechat\tmp\1DpDIixYB_zNzIA7U344FX5E_ecSluwjGWYdWNYJ0Wvwh8ifzgzakw3P29Bd0OE-P - 副本.wav")
print(result)