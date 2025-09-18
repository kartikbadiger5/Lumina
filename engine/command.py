import pyttsx3
import speech_recognition as sr
import eel
import time

def speak(text):
    """Speak text using TTS, respecting speech enabled setting"""
    # Check if this is being imported in main.py context
    try:
        # Try to import the global SPEECH_ENABLED from main
        import main
        speech_enabled = getattr(main, 'SPEECH_ENABLED', True)
    except (ImportError, AttributeError):
        # Fallback to checking settings directly
        try:
            from engine.settings_manager import SettingsManager
            settings_manager = SettingsManager()
            speech_enabled = settings_manager.get_setting('assistant', 'voice_feedback_enabled')
        except:
            speech_enabled = True  # Default to enabled if can't check
    
    text = str(text)
    
    # Always update the UI regardless of speech setting
    eel.DisplayMessage(text)
    eel.receiverText(text)
    eel.js_updateSiriMessage(text)  # Update main Siri message area
    
    # Only use TTS if speech is enabled
    if speech_enabled:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices') 
        engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()


def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        eel.js_updateSiriMessage('Listening...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 6)
    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        eel.js_updateSiriMessage('Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        eel.js_updateSiriMessage(query)
        time.sleep(2)
    except Exception as e:
        eel.js_updateSiriMessage('Sorry, I did not catch that.')
        return ""
    return query.lower()

@eel.expose
def allCommands(message=1):
    eel.js_updateSiriMessage('Listening...')  # Reset UI for new command
    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    result = "ok"
    try:
        if "open" in query:
            from engine.features import openCommand
            result = openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            result = PlayYoutube(query)
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)
                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query: 
                        speak("what message to send")
                        message = takecommand()
                        result = sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        result = makeCall(name, contact_no)
                    else:
                        speak("please try again")
                        result = "please try again"
                elif "whatsapp" in preferance:
                    message = ""
                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()
                    elif "phone call" in query:
                        message = 'call'
                    else:
                        message = 'video call'
                    result = whatsApp(contact_no, query, message, name)
        elif "add contact" in query:
            from engine.features import addContact
            result = addContact(query)
        elif "delete all contacts" in query or "clear all contacts" in query:
            from engine.features import deleteAllContacts
            result = deleteAllContacts(query)
        # Media control commands
        elif any(cmd in query for cmd in ["pause", "pause song", "pause the song", "stop this song", "resume", "play again", "play pause"]):
            from engine.helper import pause_media
            result = pause_media()
            speak(result)
        elif any(cmd in query for cmd in ["next song", "next track", "skip song", "skip track", "skip this song", "play next", "next"]):
            from engine.helper import next_song
            result = next_song()
            speak(result)
        elif any(cmd in query for cmd in ["previous song", "previous track", "back song", "back track", "go back", "play previous", "previous"]):
            from engine.helper import previous_song
            result = previous_song()
            speak(result)
        elif any(cmd in query for cmd in ["volume up", "increase volume", "louder", "turn up volume", "make it louder"]):
            from engine.helper import increase_volume
            result = increase_volume()
            speak(result)
        elif any(cmd in query for cmd in ["volume down", "decrease volume", "lower volume", "quieter", "turn down volume", "make it quieter"]):
            from engine.helper import decrease_volume
            result = decrease_volume()
            speak(result)
        elif any(cmd in query for cmd in ["mute", "unmute", "mute volume", "silence", "turn off sound"]):
            from engine.helper import mute_volume
            result = mute_volume()
            speak(result)
        elif "set volume" in query:
            import re
            # Extract volume level from query like "set volume to 50" or "set volume 70"
            match = re.search(r'set volume(?:\s+to)?\s+(\d{1,3})', query)
            if match:
                level = int(match.group(1))
                from engine.helper import set_volume_level
                result = set_volume_level(level)
                speak(result)
            else:
                result = "Please specify a volume level between 0 and 100"
                speak(result)
        else:
            from engine.features import chatBot
            result = chatBot(query)
    except Exception as e:
        import traceback
        print('allCommands error:', e)
        traceback.print_exc()
        eel.receiverText('Sorry, an error occurred.')
        result = "error"
    eel.ShowHood()  # Return to hood after command
    if not isinstance(result, str):
        result = str(result) if result is not None else "ok"
    return result  # Always return a value for eel