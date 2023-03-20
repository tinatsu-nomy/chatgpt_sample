#
#   ANY PROBLEMS THAT OCCUR WITH THIS APPLICATION ARE TO BE RESOLVED
#   BY THE USER OF THE APPLICATION. THE AUTHOR ASSUMES NO RESPONSIBILITY.
#
#   LICENSE:
#     app.py
#       This software is released under the MIT License.
#       Copyright (c) 2023 Tinatsu Nomy
#       http://opensource.org/licenses/mit-license.php
#
import datetime
import os
import pprint
from html.parser import HTMLParser

import gradio as gr
import openai

import aivoicepb as aivoice

# OpenAI API Key Settings
#   Set REQUIRED VALUE to the environment variable.
openai.organization = os.environ['OPENAI_ORGANIZATION_ID']
openai.api_key = os.environ['OPENAI_API_KEY']

# Always grant prompts
PROMPT = "Input and Output should be Japanese."

# A.I.VOICE Editor API Playback binding library
voice = aivoice.AiVoicePlayback()


"""
    HTML parser class for removing HTML tags
"""
class RemoveHtmlTags(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.__data = ""
    def handle_starttag(self,tag, attrs):
        pass
    def handle_endtag(self,tag, attrs):
        pass
    def handle_data(self, data):
        self.__data += data
    def feed(self, data: str):
        super().feed(data)
        return self
    def get_no_tagged_data(self):
        return self.__data


# Define a function to call ChatGPT
def generate_response(prompt, max_tokens):
    if len(prompt.strip()) < 1:
        # Do not update Chatbot by throwing an Exception.
        raise gr.Error('No input.')

    print(f"prompt text: {prompt}")
    start_tm = datetime.datetime.now()
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{PROMPT}\n{prompt}",
        max_tokens=int(max_tokens),
        temperature=0.5,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0.6,
    )
    end_tm = datetime.datetime.now()
    delta_time = (end_tm-start_tm).total_seconds() * 1000

    message = response.choices[0].text
    pprint.pprint(response)
    print(f"Processing time: {delta_time} ms")
    return message.strip()


# speaking
def speech(message, char=None):
    if not char is None:
        voice.set_current_preset(char)
    delay_time = voice.speech(message)
    print(f"Speech text: {message}")
    print(f"Speech time: {delay_time} ms")


# chatbot
def history_update(input, max_tokens, char, history):
    if voice.is_busy():
        # Do not update Chatbot by throwing an Exception.
        raise gr.Error('Unable to execute while in process.')
    history = history or []
    response = generate_response(input, max_tokens)
    if response is None:
        return history
    history.append((f"👤 {input}", f"📣 {char}\n{response}"))
    speech(response, char)
    return history


# update input textbox and chatbot
def chat_update(history):
    return "", history


# replay speech
def chat_select(select, evt: gr.SelectData):
    if voice.is_busy():
        return
    # response
    # evt.index[0] : Rows, evt.index[1] : Columns(0: input, 1: response)
    if evt.index[1] != 1:
        return
    # When data is imported using select,
    # HTML tags are attached, so HTML tags are removed using HTML parser.
    response = evt.value.replace("📣 ","", 1)
    response = RemoveHtmlTags().feed(response).get_no_tagged_data()
    # Format is "<character>\n<message>""
    char,message = response.split("\n", 1)
    if len(char)>0 and len(message)>0:
        speech(message, char)


# abort speech
def speech_stop():
    voice.stop_speech()


def main():
    # voice
    voice_name = voice.get_current_preset()
    # Since temporary changes cannot be made from tpAPI,
    # the voice parameter is not changed.
    voice_params = voice.get_voice_preset_params(voice_name)
    voice.speech(f"{voice_name}です。こんにちは！", with_wait=True)

    # User Interface Definition
    with gr.Blocks(title="ChatGPT") as app:
        gr.Markdown(
            "ChatGPTを使用して自然な会話を行います。",
            )
        with gr.Row(variant='compact'):
            with gr.Column():
                chat_chars  = gr.Dropdown(choices=voice.get_presets(),
                                        value=voice.get_current_preset(),
                                        label="発声キャラクタ",
                                        interactive=True)
                max_tokens = gr.Slider(minimum=1, maximum=2048, value=16, label="最大トークン数")
                chat_input = gr.Textbox(label="貴方")
                with gr.Row():
                    stop_button = gr.Button("発声停止", variant='secondary')
                    chat_button = gr.Button("話す", variant='primary')
            """
                #
                # Since temporary changes cannot be made from tpAPI,
                # the voice parameter is not changed.
                #
                with gr.Accordion(label="音声パラメタ", open=False):
                    voice_volume = gr.Slider(
                        minimum=0.0, maximum=2.0, step=0.01, value=voice_params['Volume'], label="音量"
                    )
                    voice_speed = gr.Slider(
                        minimum=0.5, maximum=4.0, step=0.01, value=voice_params['Speed'], label="話速"
                    )
                    voice_pitch = gr.Slider(
                        minimum=0.5, maximum=2.0, step=0.01, value=voice_params['Pitch'], label="高さ"
                    )
                    voice_pitchrange = gr.Slider(
                        minimum=0.0, maximum=2.0, step=0.01, value=voice_params['PitchRange'], label="抑揚"
                    )
                    voice_middlepause = gr.Slider(
                        minimum=80, maximum=500, step=1, value=voice_params['MiddlePause'], label="短ポーズ[ms]"
                    )
                    voice_longpause = gr.Slider(
                        minimum=80, maximum=2000, step=1, value=voice_params['LongPause'], label="長ポーズ[ms]"
                    )
                    voice_styles = {}
                    if voice_params.get('Styles', None):
                        label_list = {'J':'喜び(ハイテンション)', 'A':'怒り', 'S':'悲しみ(ローテンション)'}
                        for sp in voice_params['Styles']:
                            voice_styles.update(
                                {sp['Name'] :
                                gr.Slider(
                                    minimum=0.0, maximum=1.0, step=0.01, value=sp['Value'], label=label_list[sp['Name']]
                                )}
                            )
            """
            chatbot_stats = gr.State()
            chatbot = gr.Chatbot(label="会話履歴").style(height=768)

        chat_chars.change(voice.set_current_preset, inputs=[chat_chars])
        chat_button.click(history_update,
                        inputs=[chat_input, max_tokens, chat_chars, chatbot_stats],
                        outputs=[chatbot_stats]
                        ).then(chat_update,
                                inputs=[chatbot_stats],
                                outputs=[chat_input, chatbot]
                                )
        chat_input.submit(history_update,
                        inputs=[chat_input, max_tokens, chat_chars, chatbot_stats],
                        outputs=[chatbot_stats]
                        ).then(chat_update,
                                inputs=[chatbot_stats],
                                outputs=[chat_input, chatbot]
                                )
        chatbot.select(chat_select, inputs=[chatbot])
        stop_button.click(speech_stop)
    
    voice.speech(f"ブラウザを起動します。", with_wait=True)

    # Launching Applications & Launch Browser
    app.launch(inbrowser=True)


if __name__ == "__main__":
    main()
