"""
    A.I.VOICE Editor API Playback binding

        VOICE PLAYBACK ONLY.

    CAUTION:
        PLEASE READ THE "A.I. VOICE EDITOR API" TERMS OF USE (JAPANESE)
        CAREFULLY AND COMPLY WITH THE TERMS OF USE BEFORE USE.
        SEE: https://aivoice.jp/manual/editor/api.html#termsandconditions (JAPANESE)

        ANY PROBLEMS THAT OCCUR WITH THIS LIBRARY ARE TO BE RESOLVED
        BY THE USER OF THE LIBRARY. THE AUTHOR ASSUMES NO RESPONSIBILITY.

    LICENSE:
        aivoicepb.py
            This software is released under the MIT License.
            Copyright (c) 2023 Tinatsu Nomy
            http://opensource.org/licenses/mit-license.php

    Reference Documentation:
        https://aivoice.jp/manual/editor/api.html (Japanese)

        Exception is not wrapped, See official documentation.
        Checking the exception message generally solves the problem.
        The message is in Japanese, though. And then see this source.

    Required Libraries:
        pythonnet

    Quick Start:
        PowerShell environment with python, etc.
            python -m pip install pythonnet
            python -c "import aivoicepb as aivoice;
                        v=aivoice.AiVoicePlayback();
                            v.speech('はろーわーるど')"

    Tested:
        Windows 10 (Japanese edition).
        Python 3.10.9
        pythonnet 3.0.1
        AI.Talk.Editor.Api.dll 1.3.2.0
        AI.Talk.Editor 1.4.5.0
"""
import time
import os
import json

# load A.I.VOICE Editor DLL (.NET library)
"""
    "A.I. VOICE Editor" is installed in a non-standard location,
    specify the installation directory in the environment variable
    "AIVOICE_EDITOR_DIR".
    Example:
        import os
        os.environ['AIVOICE_EDITOR_DIR'] = "<installed directory>"
        import aivoicepb as aivoice
"""
import clr
DLL_NAME = 'AI.Talk.Editor.Api.dll'
DLL_PATH = os.path.join(
        os.environ.get('AIVOICE_EDITOR_DIR', None) or
        os.path.join(os.environ['ProgramFiles'],
                        'AI\AIVoice\AIVoiceEditor'),
        DLL_NAME
    )
clr.AddReference(DLL_PATH)
from AI.Talk.Editor.Api import TtsControl, HostStatus, TextEditMode

"""
    A.I.VOICE Editor API Playback binding

    (little attention)
    The connection with "A.I. VOICE Editor" will be disconnected after 10 minutes
    of inactivity. For this reason, the connection operation is performed every time
    the "A.I. VOICE Editor" is operated.
    If an operation is performed during audio playback (Play()) in "A.I. VOICE Editor",
    an exception will occur, so please check with #is_busy() before performing the operation.
"""
class AiVoicePlayback:
    
    def __init__(self) -> None:
        """
            constructor
            
            Initialization of instances
        """
        # wrapper class initialization
        self.is_connect = False
        self.preset_names = []
        self.tts_control = TtsControl()
        # Coupling with A.I.VOICE Editor
        self.__start_up()

    def __del__(self) -> None:
        """
            destructor

            May not be necessary.
        """
        try:
            self.__disconnect()
        except:
            pass

    def __start_up(self) -> None:
        """
            Confirmation of the existence of the "A.I. VOICE Editor" and its activation.
        """
        self.hosts = self.tts_control.GetAvailableHostNames()
        if len(self.hosts) < 1:
                raise Exception('The A.I.VOICE Editor is not yet installed.')
        self.current_host = self.hosts[0]
        # API initialization
        self.tts_control.Initialize(self.current_host)
        # Launch with application program
        self.__start_host()
        # Connect to the application program
        self.__connect()
        # set TextEditMode Text
        self.tts_control.TextEditMode = TextEditMode.Text
        self.is_connect = True

    def __start_host(self):
        """
            Launch with application program
            Wait 300 seconds for startup.
        """
        round = 0
        wait_time = 300.0
        while True:
            status = self.tts_control.Status
            if status == HostStatus.NotConnected:
                break
            elif round == 0:
                self.tts_control.StartHost()
            time.sleep(0.01)
            round += 1
            if (round > wait_time/0.01):
                raise Exception(f'Failed to start up the A.I.VOICE Editor. Waited {wait_time} seconds.')

    def __connect(self) -> None:
        """
            The connection with "A.I. VOICE Editor" will be disconnected after 10 minutes
            of inactivity. For this reason, the connection operation is performed every time
            the "A.I. VOICE Editor" is operated.
            If a connection (Idle or Busy) cannot be made within 10 seconds,
            the "A.I. VOICE Editor" is considered to be in a hang-up state.
        """
        round = 0
        wait_time = 10.0
        while True:
            status = self.tts_control.Status
            if status == HostStatus.NotRunning:
                raise Exception('The A.I.VOICE Editor is not running.')
            elif status == HostStatus.NotConnected:
                if round == 0:
                    self.tts_control.Connect()
            elif status == HostStatus.Idle:
                break
            elif status == HostStatus.Busy:
                break
            time.sleep(0.01)
            round += 1
            if (round > wait_time/0.01):
                raise Exception(f'Failed to connect with the A.I.VOICE Editor. Waited {wait_time} seconds.')

    def __disconnect(self) -> None:
        """
            Disconnect, but "A.I. VOICE Editor" does not stop.
        """
        if not self.is_connect:
            return
        status = self.tts_control.Status
        if (status):
            if status == HostStatus.NotRunning:
                pass
            elif status == HostStatus.NotConnected:
                pass
            else:
                self.tts_control.Disconnect()

    def get_host_version(self) -> str:
        """
            Get the version of the "A.I. VOICE Editor".
        """
        return self.tts_control.Version

    def get_presets(self) -> list:
        """
            Get a list of presets in the "A.I. VOICE Editor".
            It contains standard voice presets and user voice presets.
        """
        self.__connect()
        self.preset_names = self.tts_control.VoicePresetNames
        return list([str(n) for n in self.preset_names])

    def get_current_preset(self) -> str:
        """
            Get the name of the preset currently in use.
        """
        self.__connect()
        return str(self.tts_control.CurrentVoicePresetName)

    def set_current_preset(self, name) -> None:
        """
            Set presets to be used for playback
            Set from the presets obtained by #get_presets().
        """
        self.__connect()
        self.tts_control.CurrentVoicePresetName = name

    def get_voice_preset_params(self, name) -> dict:
        """
            Get the parameters set in the voice preset.
        """
        self.__connect()
        json_params = self.tts_control.GetVoicePreset(name)
        dict_params = json.loads(json_params)
        return dict_params

    def create_voice_preset_params(self, parmas:dict, duplicate2rename=False) -> None:
        """
            Create and set up a new voice preset.
            And switch to new preset.
            Note that voice presets can only be deleted in "A.I. VOICE Editor".
            If duplicate2rename=True, duplicate preset names are renamed. (<preset name>_nnn).
        """
        self.__connect()
        if duplicate2rename:
            names = self.get_presets()
            sub_number = 0
            new_name = parmas['PresetName']
            while new_name in names:
                sub_number += 1
                new_name = parmas['PresetName'] + "_{:03d}".format(sub_number)
            parmas['PresetName'] = new_name
        json_params = json.dumps(parmas)
        self.tts_control.AddVoicePreset(json_params)
        self.set_current_preset(parmas['PresetName'])

    def replace_voice_preset_params(self, parmas:dict) -> None:
        """
            Rewrites the parameters of an existing voice preset.
            Use with caution as temporary rewriting is not possible.
            Backups are important.
        """
        self.__connect()
        json_params = json.dumps(parmas)
        self.tts_control.SetVoicePreset(json_params)

    def speech(self, message, get_playback_time=True, with_wait=False) -> int:
        """
            Voice Playback
        """
        self.__connect()
        self.tts_control.Text = message
        if not get_playback_time:
            self.tts_control.Play()
            return 0 if not with_wait else self.wait() or 0

        """
            Once all text is selected. This is to obtain the playback time.
            When the playback time can be obtained, the selection state is released.
            Playback time is in microseconds.
        """
        self.tts_control.TextSelectionStart = 0
        self.tts_control.TextSelectionLength = len(message)
        playback_time = self.tts_control.GetPlayTime()
        self.tts_control.TextSelectionLength = 0
        self.tts_control.Play()
        return playback_time if not with_wait else self.wait() or playback_time

    def stop_speech(self) -> None:
        """
            Stops the voice playing.
        """
        self.__connect()
        self.tts_control.Stop()

    def is_busy(self) -> bool:
        """
           Check during voice playback.

               True - Voice playing (Busy)
               False - Voice playback stop (Idle)
        """
        return self.tts_control.Status == HostStatus.Busy

    def wait(self) -> None:
        """
            Wait for playback to complete.
        """
        while True:
            time.sleep(0.01)
            if not self.is_busy():
                return None
