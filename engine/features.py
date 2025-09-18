from email.utils import quote
import os
# from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
import speech_recognition as sr
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine
import requests

from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat
# Import contact management functions
from engine.scan_contacts import add_contact_by_voice, search_contact

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)
    return "ok"  # Always return a value for eel

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip().lower().replace('  ', ' ')

    if app_name:
        try:
            # 1. Check sys_apps (scanned desktop apps) with flexible LIKE match
            cursor.execute('SELECT location, extension FROM sys_apps WHERE LOWER(name) LIKE ?', (f'%{app_name}%',))
            results = cursor.fetchall()
            if not results:
                # Try removing spaces for even more flexibility
                app_name_nospace = app_name.replace(' ', '')
                cursor.execute('SELECT location, extension FROM sys_apps WHERE REPLACE(LOWER(name), " ", "") LIKE ?', (f'%{app_name_nospace}%',))
                results = cursor.fetchall()
            if results:
                location, extension = results[0]
                speak("Opening " + app_name)
                if extension == '.uwp':
                    # Launch UWP app using explorer.exe shell:appsFolder\AppUserModelId
                    try:
                        subprocess.Popen(["explorer.exe", f"shell:appsFolder\\{location}"])
                    except Exception as e:
                        speak("Failed to open UWP app")
                        return f"error: {e}"
                else:
                    os.startfile(location)
                return "ok"

            # 2. Fallback: sys_command (legacy)
            cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) LIKE ?', (f'%{app_name}%',))
            results = cursor.fetchall()
            if results:
                speak("Opening "+app_name)
                os.startfile(results[0][0])
                return "ok"

            # 3. Fallback: web_command
            cursor.execute('SELECT url FROM web_command WHERE LOWER(name) LIKE ?', (f'%{app_name}%',))
            results = cursor.fetchall()
            if results:
                speak("Opening "+app_name)
                webbrowser.open(results[0][0])
                return "ok"

            # 4. Fallback: try to open by name
            speak("Opening "+app_name)
            try:
                os.system('start '+app_name)
                return "ok"
            except:
                speak("not found")
                return "not found"
        except Exception as e:
            speak("something went wrong")
            return f"error: {e}"
    return "ok"

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if not search_term:
        speak("Sorry, I couldn't understand the song name to play on YouTube.")
        return "error: no song name found"
    speak("Playing "+str(search_term)+" on YouTube")
    kit.playonyt(search_term)
    return "ok"


def hotword():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Adjust for ambient noise once
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    # Get the current wake word from settings
    current_wake_word = "lumina"  # Default fallback
    try:
        from engine.settings_manager import settings_manager
        current_wake_word = settings_manager.get_setting("assistant", "wake_word", "lumina")
    except:
        pass
    
    print(f"Wake word detection started. Listening for '{current_wake_word}'...")
    
    while True:
        try:
            # Get the current wake word (in case it changed during runtime)
            try:
                from engine.settings_manager import settings_manager
                current_wake_word = settings_manager.get_setting("assistant", "wake_word", "lumina")
            except:
                current_wake_word = "lumina"
            
            # Check continuous listening setting
            continuous_listening = False
            try:
                # Try to import the global CONTINUOUS_LISTENING from main
                import main
                continuous_listening = getattr(main, 'CONTINUOUS_LISTENING', False)
            except (ImportError, AttributeError):
                # Fallback to checking settings directly
                try:
                    from engine.settings_manager import settings_manager
                    continuous_listening = settings_manager.get_setting('assistant', 'continuous_listening')
                except:
                    continuous_listening = False
            
            with microphone as source:
                # Listen for audio with timeout and phrase time limit
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
            
            try:
                # Recognize speech
                text = recognizer.recognize_google(audio, language='en-in').lower()
                print(f"Heard: {text}")
                
                # Check if we should activate based on settings
                should_activate = False
                
                if continuous_listening:
                    # In continuous mode, any clear speech activates the assistant
                    should_activate = True
                    print("Continuous listening mode - activating assistant")
                elif current_wake_word.lower() in text:
                    # Normal mode - only activate on wake word
                    should_activate = True
                    print(f"Wake word '{current_wake_word}' detected!")
                
                if should_activate:
                    # Simulate pressing Win+J (same as original hotword function)
                    # This will trigger the UI in Process 1
                    import pyautogui as autogui
                    autogui.keyDown("win")
                    autogui.press("j")
                    time.sleep(2)
                    autogui.keyUp("win")
                    
                    # Brief pause after activation
                    time.sleep(1)
                    
            except sr.UnknownValueError:
                # Speech was unintelligible, continue listening
                pass
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                time.sleep(1)
                
        except sr.WaitTimeoutError:
            # No speech detected within timeout, continue listening
            pass
        except Exception as e:
            print(f"Wake word detection error: {e}")
            time.sleep(1)



# find contacts
def findContact(query):
    
    # More comprehensive word removal for contact name extraction
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video', 'sms']
    
    # Use the helper function to remove words
    cleaned_query = remove_words(query, words_to_remove)
    
    # Additional cleaning - remove extra spaces and common remaining words
    cleaned_query = cleaned_query.strip().lower()
    cleaned_query = ' '.join(cleaned_query.split())  # Remove extra spaces
    
    # Remove any remaining single characters and common words
    words = cleaned_query.split()
    contact_words = [word for word in words if len(word) > 1 and word not in ['an', 'the', 'for', 'with']]
    final_query = ' '.join(contact_words)
    
    print(f"Original query: '{query}' -> Cleaned: '{final_query}'")

    try:
        # Updated to use the new contacts table structure
        print(f"Searching database for contact: '{final_query}'")
        cursor.execute("SELECT phone_number, name FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + final_query + '%', final_query + '%'))
        results = cursor.fetchall()
        print(f"Database query results: {results}")
        
        if results:
            phone_number = str(results[0][0])
            contact_name = str(results[0][1])
            print(f"Found contact: {contact_name} - {phone_number}")
            
            # Ensure phone number format is correct
            if not phone_number.startswith('+'):
                # If it's a 10-digit number, assume it's Indian (+91)
                if len(phone_number) == 10 and phone_number.isdigit():
                    phone_number = '+91' + phone_number
                    print(f"Formatted phone number: {phone_number}")
                # If it doesn't start with +, add + if it's a valid international format
                elif phone_number.isdigit() and len(phone_number) > 10:
                    phone_number = '+' + phone_number
                    print(f"Formatted phone number: {phone_number}")

            print(f"Returning: {phone_number}, {contact_name}")
            return phone_number, contact_name
        else:
            # If no contact found, suggest adding it
            print(f"No contact found for query: '{final_query}'")
            speak(f'Contact {final_query} does not exist in contacts. You can add it by saying add contact {final_query} with number and then the phone number')
            return 0, 0
    except Exception as e:
        print(f"Error finding contact: {e}")
        speak('Error finding contact in database')
        return 0, 0
        speak('Error finding contact in database')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 20
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 14
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 13
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)
    return "ok"

# chat bot 
def chatBot(query):
    """
    Uses Google Gemini API to get a response for the user's query.
    Set your Gemini API key in the GEMINI_API_KEY variable below.
    """
    GEMINI_API_KEY = "AIzaSyDJoTMLGw-jqAjeFLtZGqXm8NXQVMwhRgY"  # <-- Set your Gemini API key here
    # Use a valid model name for your API key. You may need to check your Google AI Studio for available models.
    GEMINI_MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro" if available for your key
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key=" + GEMINI_API_KEY

    headers = {"Content-Type": "application/json"}
    # Use 'user' role for user input, and optionally 'model' for system prompt
    system_prompt = (
        "You are JARVIS, a smart, fast, and helpful AI assistant. "
        "Respond quickly and concisely. If a short paragraph is needed, provide it, but keep answers brief and to the point. "
        "Always be conversational and clear."
    )
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt + " " + query}]}
        ]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            answer = result["candidates"][0]["content"]["parts"][0]["text"]
            print(answer)
            speak(answer)
            return answer
        else:
            error_msg = f"Gemini API error: {response.status_code} {response.text}"
            print(error_msg)
            speak("Sorry, I couldn't get an answer from Gemini.")
            return error_msg
    except Exception as e:
        print(f"Gemini API exception: {e}")
        speak("Sorry, I couldn't connect to Gemini.")
        return str(e)

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)
    return "ok"


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(136, 2220)
    #start chat
    tapEvents(819, 2192)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(601, 574)
    # tap on input
    tapEvents(390, 2270)
    #message
    adbInput(message)
    #send
    tapEvents(957, 1397)
    speak("message send successfully to "+name)
    return "ok"

def addContact(query):
    """
    Voice-based contact addition function
    Usage: "add contact John with number 1234567890" or "add contact Mom with number plus one two three four five six seven eight nine zero"
    """
    try:
        # Parse the command to extract name and phone number
        query = query.lower().replace("add contact", "").strip()
        
        # Look for patterns like "name with number phone" or "name number phone"
        if "with number" in query:
            parts = query.split("with number")
            name = parts[0].strip()
            phone_part = parts[1].strip()
        elif "number" in query:
            parts = query.split("number")
            name = parts[0].strip()
            phone_part = parts[1].strip()
        else:
            speak("Please say the contact name followed by 'with number' and then the phone number")
            return "format_error"
        
        if not name:
            speak("Please provide a contact name")
            return "no_name"
        
        # Convert spoken numbers to digits
        phone_number = convert_spoken_to_digits(phone_part)
        
        if not phone_number or len(phone_number) < 10:
            speak("Please provide a valid phone number with at least 10 digits")
            return "invalid_phone"
        
        # Add the contact using the scan_contacts module
        result = add_contact_by_voice(name.title(), phone_number)
        
        if result['status'] == 'success':
            speak(f"Contact {name} has been added successfully with number {phone_number}")
            return "success"
        else:
            speak(result['message'])
            return "error"
            
    except Exception as e:
        speak("Sorry, I couldn't add the contact. Please try again.")
        return f"error: {e}"

def convert_spoken_to_digits(spoken_number):
    """
    Convert spoken numbers to digit string
    Handles: "one two three" -> "123", "plus one" -> "+1", etc.
    """
    # Number word to digit mapping
    word_to_digit = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'plus': '+', 'dash': '-', 'hyphen': '-'
    }
    
    # Clean the input
    spoken_number = spoken_number.lower().strip()
    words = spoken_number.split()
    
    # Convert words to digits
    digits = []
    for word in words:
        if word in word_to_digit:
            digits.append(word_to_digit[word])
        elif word.isdigit():
            digits.append(word)
        # Skip unknown words
    
    result = ''.join(digits)
    
    # If no conversion worked, try to extract existing digits
    if not result:
        import re
        result = re.sub(r'[^\d+]', '', spoken_number)
    
    return result

def deleteAllContacts(query=None):
    """
    Voice-based function to delete all contacts
    Usage: "delete all contacts" or "clear all contacts"
    """
    try:
        from engine.scan_contacts import delete_all_contacts, get_contacts_count
        from engine.command import takecommand
        
        # Get current count before deletion
        current_count = get_contacts_count()
        
        if current_count == 0:
            speak("No contacts found in the database")
            return "no_contacts"
        
        # Confirm deletion
        speak(f"Are you sure you want to delete all {current_count} contacts? Say yes to confirm or no to cancel")
        confirmation = takecommand()
        
        if "yes" in confirmation.lower():
            result = delete_all_contacts()
            speak(f"Successfully deleted {current_count} contacts from the database")
            return "success"
        else:
            speak("Contact deletion cancelled")
            return "cancelled"
            
    except Exception as e:
        speak("Sorry, I couldn't delete the contacts. Please try again.")
        return f"error: {e}"