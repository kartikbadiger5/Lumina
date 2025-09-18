import os
import re
import time
import platform
import subprocess
import ctypes
import pyautogui


def extract_yt_term(command):
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None


def remove_words(input_string, words_to_remove):
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string



# key events like receive call, stop call, go back
def keyEvent(key_code):
    command =  f'adb shell input keyevent {key_code}'
    os.system(command)
    time.sleep(1)

# Tap event used to tap anywhere on screen
def tapEvents(x, y):
    command =  f'adb shell input tap {x} {y}'
    os.system(command)
    time.sleep(1)

# Input Event is used to insert text in mobile
def adbInput(message):
    command =  f'adb shell input text "{message}"'
    os.system(command)
    time.sleep(1)

# to go complete back
def goback(key_code):
    for i in range(6):
        keyEvent(key_code)

# To replace space in string with %s for complete message send
def replace_spaces_with_percent_s(input_string):
    return input_string.replace(' ', '%s')


# Media Controller Class for handling media controls
class MediaController:
    def __init__(self):
        self.os_type = platform.system()
        # Virtual-Key codes for Windows media keys
        self.VK_MEDIA_NEXT_TRACK   = 0xB0
        self.VK_MEDIA_PREV_TRACK   = 0xB1
        self.VK_MEDIA_PLAY_PAUSE   = 0xB3
        self.VK_VOLUME_MUTE        = 0xAD
        self.VK_VOLUME_DOWN        = 0xAE
        self.VK_VOLUME_UP          = 0xAF
        self.KEYEVENTF_EXTENDEDKEY = 0x0001
        self.KEYEVENTF_KEYUP       = 0x0002

    def _send_windows_key(self, vk_code: int):
        """Send Windows virtual key event"""
        ctypes.windll.user32.keybd_event(vk_code, 0, self.KEYEVENTF_EXTENDEDKEY, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, self.KEYEVENTF_EXTENDEDKEY | self.KEYEVENTF_KEYUP, 0)

    def toggle_playback(self):
        """Play/Pause media"""
        if self.os_type == "Windows":
            self._send_windows_key(self.VK_MEDIA_PLAY_PAUSE)
            pyautogui.hotkey('k')  # Additional YouTube hotkey
        elif self.os_type == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 16'])
        elif self.os_type == "Linux":
            subprocess.run(["xdotool", "key", "XF86AudioPlay"])
        return "Media playback toggled"

    def next_track(self):
        """Skip to next track"""
        if self.os_type == "Windows":
            self._send_windows_key(self.VK_MEDIA_NEXT_TRACK)
            pyautogui.hotkey('shift', 'n')  # Additional YouTube hotkey
        elif self.os_type == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 17'])
        elif self.os_type == "Linux":
            subprocess.run(["xdotool", "key", "XF86AudioNext"])
        return "Played next song"

    def previous_track(self):
        """Skip to previous track"""
        if self.os_type == "Windows":
            self._send_windows_key(self.VK_MEDIA_PREV_TRACK)
            pyautogui.hotkey('shift', 'p')  # Additional YouTube hotkey
        elif self.os_type == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 18'])
        elif self.os_type == "Linux":
            subprocess.run(["xdotool", "key", "XF86AudioPrev"])
        return "Played previous song"

    def volume_up(self):
        """Increase volume"""
        if self.os_type == "Windows":
            self._send_windows_key(self.VK_VOLUME_UP)
        elif self.os_type == "Darwin":
            subprocess.run([
                "osascript", "-e",
                'set volume output volume ((output volume of (get volume settings)) + 10)'
            ])
        elif self.os_type == "Linux":
            subprocess.run(["xdotool", "key", "XF86AudioRaiseVolume"])
        return "Volume increased"

    def volume_down(self):
        """Decrease volume"""
        if self.os_type == "Windows":
            self._send_windows_key(self.VK_VOLUME_DOWN)
        elif self.os_type == "Darwin":
            subprocess.run([
                "osascript", "-e",
                'set volume output volume ((output volume of (get volume settings)) - 10)'
            ])
        elif self.os_type == "Linux":
            subprocess.run(["xdotool", "key", "XF86AudioLowerVolume"])
        return "Volume decreased"

    def mute(self):
        """Mute/Unmute volume"""
        if self.os_type == "Windows":
            self._send_windows_key(self.VK_VOLUME_MUTE)
        elif self.os_type == "Darwin":
            subprocess.run([
                "osascript", "-e",
                'set volume with output muted'
            ])
        elif self.os_type == "Linux":
            subprocess.run(["xdotool", "key", "XF86AudioMute"])
        return "Volume muted/unmuted"

    def set_volume(self, level: int):
        """Set volume to specific level (0-100)"""
        level = max(0, min(100, level))
        if self.os_type == "Windows":
            try:
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
                )
                volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
                scalar = level / 100.0
                volume_interface.SetMasterVolumeLevelScalar(scalar, None)
            except Exception:
                return "Volume control not available"
        elif self.os_type == "Darwin":
            subprocess.run([
                "osascript", "-e",
                f"set volume output volume {level}"
            ])
        else:  # Linux
            subprocess.run([
                "pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"
            ])
        return f"Volume set to {level}%"


# Create global media controller instance
media_controller = MediaController()


# Media control helper functions
def pause_media():
    """Pause/Play media"""
    return media_controller.toggle_playback()

def next_song():
    """Skip to next song"""
    return media_controller.next_track()

def previous_song():
    """Skip to previous song"""
    return media_controller.previous_track()

def increase_volume():
    """Increase system volume"""
    return media_controller.volume_up()

def decrease_volume():
    """Decrease system volume"""
    return media_controller.volume_down()

def mute_volume():
    """Mute/Unmute system volume"""
    return media_controller.mute()

def set_volume_level(level):
    """Set volume to specific level"""
    return media_controller.set_volume(level)
