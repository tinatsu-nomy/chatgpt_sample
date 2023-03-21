# ChatGPT Sample
Simple Gradio application using ChatGPT API, operated from a web browser.  
This applicaton is linked with A.I.VOICE Editor, an product of AI, Inc., and responds to ChatGPT answers by voice.  
## LICENSE
This software is released under the MIT License.  
Copyright (c) 2023 Tinatsu Nomy  
http://opensource.org/licenses/mit-license.php  
## USAGE
ここから日本語w  
- OpenAIのサイトでAPI Key, openai,organization idを取得します。  
- 環境変数へAPI openai,organization idを設定します。  
  `OPENAI_API_KEY`へは`API Key`、`OPENAI_ORGANIZATION_ID`は`organization id`を設定します。  
- Python環境を用意します。  
  Python 3.10.9で動作確認済み。  
  ライブラリをインストールするのでvenvで仮想環境を作成することがお勧めです。  
- ライブラリをインストールします。  
　openai、Gradioとpythonnetをインストールします。  
  ```
  pip install openai gradio pythonnet
  ```
- A.I.VOICE Editorで喋らせたいキャラクタのプリセットを作成します。  
  <img src="https://github.com/tinatsu-nomy/chatgpt_sample/blob/main/images/aivoice.png" width="300px">
- app.pyを起動します。　　
  ```
  python app.py
  ```
  しばらくすると、Webブラウザが起動します。  
  <img src="https://github.com/tinatsu-nomy/chatgpt_sample/blob/main/images/chatgpt_sample.png" width="300px">
