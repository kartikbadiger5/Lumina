import os
import eel
import threading
import winreg
import sys
import pystray
from PIL import Image, ImageDraw, ImageFont
import webbrowser

from engine.features import *
from engine.command import *
import engine.scan_apps  # Register scan_desktop_apps with eel
import engine.db        # Register store_scanned_apps with eel
from engine.settings_manager import settings_manager
## from engine.auth import recoganize  # Face authentication removed

# Global variables for settings
SPEECH_ENABLED = True
CONTINUOUS_LISTENING = False

# System Tray Management
class JarvisTray:
    def __init__(self):
        self.tray = None
        self.is_running = False
        self.tray_thread = None
        
    def create_image(self):
        """Create a simple icon for the system tray"""
        try:
            # Try to load an existing icon first
            icon_path = os.path.join("www", "assets", "img", "logo.ico")
            if os.path.exists(icon_path):
                print(f"📁 Loading icon from: {icon_path}")
                image = Image.open(icon_path)
                # Convert to RGBA for better compatibility
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                print("✅ Icon loaded and converted to RGBA")
                return image
        except Exception as e:
            print(f"Could not load icon file: {e}")
        
        # Create a more robust fallback icon
        try:
            print("🎨 Creating custom fallback icon...")
            # Create a 32x32 RGBA image for better Windows compatibility
            width = height = 32
            
            # Create image with transparent background
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw a filled circle
            margin = 2
            circle_color = (0, 170, 255, 255)  # Blue with full alpha
            draw.ellipse([margin, margin, width-margin, height-margin], 
                        fill=circle_color, outline=(255, 255, 255, 255), width=1)
            
            # Add a simple "J" in the center
            try:
                # Try to get a system font
                font = ImageFont.truetype("arial.ttf", 18)
            except:
                try:
                    font = ImageFont.truetype("calibri.ttf", 18) 
                except:
                    font = ImageFont.load_default()
            
            text = "J"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2 - 2
            
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            
            print(f"✅ Created custom {width}x{height} RGBA icon")
            return image
            
        except Exception as e:
            print(f"Could not create custom icon: {e}")
            try:
                # Last resort - simple solid icon
                print("🔴 Creating minimal fallback...")
                image = Image.new('RGBA', (16, 16), (0, 170, 255, 255))
                print("✅ Created minimal icon")
                return image
            except Exception as e2:
                print(f"Could not create minimal icon: {e2}")
                return None
    
    def show_window(self, icon, item):
        """Show the Jarvis window"""
        try:
            print("🏠 Show window called from tray")
            # Try to call the EEL restore function
            try:
                eel.restore_from_tray()
            except:
                pass
            # Also open in browser as fallback
            webbrowser.open('http://localhost:8000')
            print("✅ Window restore initiated")
        except Exception as e:
            print(f"Error opening window: {e}")
    
    def open_settings(self, icon, item):
        """Open settings page"""
        try:
            print("⚙️ Settings called from tray")
            # Try to call the EEL function first
            try:
                eel.open_settings()
            except:
                pass
            # Also open in browser as fallback  
            webbrowser.open('http://localhost:8000/settings.html')
            print("✅ Settings window initiated")
        except Exception as e:
            print(f"Error opening settings: {e}")
    
    def quit_application(self, icon, item):
        """Quit the application"""
        try:
            print("❌ Quit application called from tray")
            self.stop_tray()
            print("🚪 Exiting application...")
            os._exit(0)
        except Exception as e:
            print(f"Error quitting: {e}")
            os._exit(1)
    
    def start_tray(self):
        """Start the system tray"""
        print(f"🎯 start_tray called. Current is_running: {self.is_running}")
        
        if self.is_running:
            print("⚠️  Tray already running, skipping")
            return True
        
        try:
            print("🖼️  Creating tray image...")
            image = self.create_image()
            if not image:
                print("❌ Could not create tray image")
                return False
            print("✅ Tray image created")
            
            print("📋 Creating tray menu...")
            menu = pystray.Menu(
                pystray.MenuItem("🏠 Show Jarvis", self.show_window, default=True),
                pystray.MenuItem("⚙️ Settings", self.open_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Quit", self.quit_application)
            )
            print("✅ Menu created successfully")
            
            print("🖼️  Creating tray icon...")
            self.tray = pystray.Icon(
                "Jarvis",  # Name
                image,     # Icon
                "Jarvis AI Assistant - Click to show",  # Tooltip
                menu       # Menu
            )
            print("✅ Tray icon created successfully")
            
            # Mark as running before starting thread
            self.is_running = True
            
            print("🚀 Starting tray thread...")
            def run_tray():
                try:
                    print("🔄 Tray thread started, making icon visible...")
                    self.tray.visible = True  # Explicitly make visible
                    print("👁️ Tray icon set to visible")
                    self.tray.run()
                    print("🏁 Tray run completed")
                except Exception as e:
                    print(f"❌ Error in tray thread: {e}")
                    import traceback
                    traceback.print_exc()
                    self.is_running = False
            
            # Run tray in a separate daemon thread
            self.tray_thread = threading.Thread(target=run_tray, daemon=True)
            self.tray_thread.start()
            print("✅ Tray thread started successfully")
            
            # Give the tray a moment to initialize
            import time
            time.sleep(0.5)
            print(f"🔍 After startup delay - is_running: {self.is_running}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting system tray: {e}")
            import traceback
            traceback.print_exc()
            self.is_running = False
            return False
    
    def stop_tray(self):
        """Stop the system tray"""
        print(f"🛑 stop_tray called. Current is_running: {self.is_running}")
        
        if not self.is_running:
            print("⚠️  Tray not running")
            return True
            
        try:
            if self.tray:
                print("🛑 Stopping tray...")
                self.tray.stop()
                print("✅ Tray stopped successfully")
            
            self.is_running = False
            self.tray = None
            
            if self.tray_thread and self.tray_thread.is_alive():
                print("⏳ Waiting for tray thread to finish...")
                # Don't join daemon threads, just mark as stopped
            
            return True
            
        except Exception as e:
            print(f"❌ Error stopping tray: {e}")
            import traceback
            traceback.print_exc()
            self.is_running = False
            return False

# Global tray instance
jarvis_tray = JarvisTray()

def on_close_callback(page, sockets):
    """Callback function when the application window is closed"""
    print("Application window closed")
    # Check if minimize to tray is enabled
    try:
        tray_enabled = settings_manager.get_setting("display", "minimize_to_tray", False)
        if tray_enabled and jarvis_tray.is_running:
            print("🔽 Minimizing to tray instead of closing...")
            # Don't actually exit, just hide the window
            return
    except Exception as e:
        print(f"Error checking tray setting: {e}")
    
    # If tray is not enabled or not running, exit normally
    print("🚪 Exiting application...")
    # Perform any cleanup operations here if needed
    if jarvis_tray.is_running:
        jarvis_tray.stop_tray()
    os._exit(0)  # Force exit the application

@eel.expose
def open_settings():
    """Open the settings window in a new eel window"""
    import threading
    
    def start_settings_window():
        try:
            # Kill any existing settings windows first
            try:
                eel.closeAllBut(['index.html'])  # Close all windows except main
            except:
                pass
                
            eel.start('settings.html', 
                      size=(800, 700),
                      position=(800, 200),  # Position next to main window
                      mode='edge',
                      host='localhost',
                      block=False,  # Non-blocking so main window stays open
                      close_callback=lambda page, sockets: print("Settings window closed"))
        except Exception as e:
            print(f"Error opening settings window: {e}")
    
    # Start settings window in a separate thread
    settings_thread = threading.Thread(target=start_settings_window, daemon=True)
    settings_thread.start()
    return "Settings window opened"

@eel.expose 
def minimize_to_tray():
    """Minimize the current window to system tray"""
    print("🔽 minimize_to_tray called")
    try:
        tray_enabled = settings_manager.get_setting("display", "minimize_to_tray", False)
        print(f"Tray enabled: {tray_enabled}, Tray running: {jarvis_tray.is_running}")
        
        if tray_enabled and jarvis_tray.is_running:
            print("✅ Minimizing to tray...")
            # Just return success - the actual hiding will be handled by the frontend
            return {"success": True, "message": "Window minimized to tray"}
        else:
            print("❌ Tray not available")
            return {"success": False, "message": "Tray not available"}
    except Exception as e:
        print(f"Error minimizing to tray: {e}")
        return {"success": False, "error": str(e)}

@eel.expose
def restore_from_tray():
    """Restore window from system tray"""
    print("🔼 restore_from_tray called")
    try:
        # This will be called from the tray menu
        return {"success": True, "message": "Window restored from tray"}
    except Exception as e:
        print(f"Error restoring from tray: {e}")
        return {"success": False, "error": str(e)}

@eel.expose
def clear_all_contacts():
    """Clear all contacts from the database"""
    try:
        from engine.features import deleteAllContacts
        result = deleteAllContacts("delete all contacts")
        return "ok" if result else "error"
    except Exception as e:
        print(f"Error clearing contacts: {e}")
        return "error"

@eel.expose
def reset_and_scan_apps():
    """Reset and scan applications"""
    try:
        import engine.scan_apps
        # Clear existing apps and scan again
        result = engine.scan_apps.reset_and_scan()
        return result
    except Exception as e:
        print(f"Error in reset and scan: {e}")
        return {"success": False, "count": 0}

# ==================== SETTINGS MANAGEMENT ====================

@eel.expose
def get_all_settings():
    """Get all current settings"""
    try:
        return {"success": True, "settings": settings_manager.get_all_settings()}
    except Exception as e:
        print(f"Error getting settings: {e}")
        return {"success": False, "settings": {}}

@eel.expose
def save_setting(category, key, value):
    """Save a specific setting"""
    try:
        global SPEECH_ENABLED, CONTINUOUS_LISTENING
        
        # Update global variables for immediate effect
        if category == "assistant" and key == "voice_feedback_enabled":
            SPEECH_ENABLED = value
        elif category == "assistant" and key == "continuous_listening":
            CONTINUOUS_LISTENING = value
            
        result = settings_manager.set_setting(category, key, value)
        return {"success": result}
    except Exception as e:
        print(f"Error saving setting: {e}")
        return {"success": False}

@eel.expose
def reset_all_settings():
    """Reset all settings to defaults"""
    try:
        global SPEECH_ENABLED, CONTINUOUS_LISTENING
        result = settings_manager.reset_to_defaults()
        
        # Reset global variables
        SPEECH_ENABLED = True
        CONTINUOUS_LISTENING = False
        
        return {"success": result}
    except Exception as e:
        print(f"Error resetting settings: {e}")
        return {"success": False}

# ==================== ASSISTANT SETTINGS ====================

@eel.expose
def set_wake_word(word):
    """Set the wake word for voice activation"""
    try:
        # Validate wake word
        if not word or len(word.strip()) < 2:
            return {"success": False, "error": "Wake word must be at least 2 characters long"}
        
        word = word.strip().lower()
        
        # Save to settings
        result = settings_manager.set_setting("assistant", "wake_word", word)
        
        if result:
            message = f"Wake word set to '{word}'. Restart may be required for changes to take effect."
            return {"success": True, "message": message, "wake_word": word}
        else:
            return {"success": False, "error": "Failed to save wake word setting"}
            
    except Exception as e:
        print(f"Error setting wake word: {e}")
        return {"success": False, "error": str(e)}

@eel.expose
def get_wake_word():
    """Get the current wake word setting"""
    try:
        wake_word = settings_manager.get_setting("assistant", "wake_word", "lumina")
        return {"success": True, "wake_word": wake_word}
    except Exception as e:
        print(f"Error getting wake word: {e}")
        return {"success": False, "error": str(e), "wake_word": "lumina"}

@eel.expose
def set_wake_word_enabled(enabled):
    """Enable/disable wake word detection"""
    try:
        result = settings_manager.set_setting("assistant", "wake_word_enabled", enabled)
        
        if result:
            status = "enabled" if enabled else "disabled"
            message = f"Wake word detection {status}. Restart may be required for changes to take effect."
            return {"success": True, "message": message}
        else:
            return {"success": False, "error": "Failed to save wake word detection setting"}
            
    except Exception as e:
        print(f"Error setting wake word detection: {e}")
        return {"success": False, "error": str(e)}

@eel.expose
def get_wake_word_enabled():
    """Get the current wake word detection status"""
    try:
        enabled = settings_manager.get_setting("assistant", "wake_word_enabled", True)
        return {"success": True, "enabled": enabled}
    except Exception as e:
        print(f"Error getting wake word detection status: {e}")
        return {"success": False, "error": str(e), "enabled": True}

# ==================== APPLICATION CONTROL ====================

@eel.expose
def shutdown_application():
    """Shutdown the entire application and all processes"""
    print("🔴 Shutdown application requested")
    
    def force_shutdown():
        """Force shutdown after delay"""
        import time
        time.sleep(0.5)  # Brief delay
        
        try:
            # Stop the tray if running
            if jarvis_tray.is_running:
                print("🛑 Stopping system tray...")
                jarvis_tray.stop_tray()
        except:
            pass
        
        try:
            # Try to terminate any hotword processes
            import subprocess
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, timeout=3)
        except:
            pass
        
        print("🚪 Force exiting application...")
        os._exit(0)
    
    try:
        # Start force shutdown in a separate thread
        import threading
        shutdown_thread = threading.Thread(target=force_shutdown, daemon=True)
        shutdown_thread.start()
        
        # Try to close EEL gracefully first
        try:
            # Close all EEL windows
            import eel
            print("🔲 Closing EEL windows...")
            
            # Try to call the frontend function to close window
            try:
                eel.forceCloseWindow()
            except:
                pass
            
            # This should close the browser windows
            for window in eel._websockets:
                try:
                    window.close()
                except:
                    pass
                    
        except Exception as e:
            print(f"Error closing EEL windows: {e}")
        
        return {"success": True, "message": "Shutdown initiated"}
        
    except Exception as e:
        print(f"Error during shutdown: {e}")
        # Force exit if anything fails
        os._exit(1)

@eel.expose  
def restart_application():
    """Restart the current application instance (refresh)"""
    print("🔄 Restart application requested")
    try:
        # Don't actually restart the whole process, just refresh the EEL interface
        # This keeps the same process but reloads the web interface
        
        # Reset any application state if needed
        global SPEECH_ENABLED, CONTINUOUS_LISTENING
        SPEECH_ENABLED = True
        CONTINUOUS_LISTENING = False
        
        # Reload settings
        try:
            # Refresh settings from file
            settings_manager.settings = settings_manager.load_settings()
            
            # Apply any updated settings
            SPEECH_ENABLED = settings_manager.get_setting("assistant", "voice_feedback_enabled", True)
            CONTINUOUS_LISTENING = settings_manager.get_setting("assistant", "continuous_listening", False)
            
            # Restart tray if needed
            tray_enabled = settings_manager.get_setting("display", "minimize_to_tray", False)
            if tray_enabled and not jarvis_tray.is_running:
                jarvis_tray.start_tray()
            elif not tray_enabled and jarvis_tray.is_running:
                jarvis_tray.stop_tray()
                
        except Exception as e:
            print(f"Error refreshing settings: {e}")
        
        print("✅ Application refreshed successfully")
        return {"success": True, "message": "Application refreshed"}
        
    except Exception as e:
        print(f"Error during restart: {e}")
        return {"success": False, "error": str(e)}

# ==================== SYSTEM INTEGRATION ====================

@eel.expose
def set_startup_enabled(enabled):
    """Enable/disable startup with Windows"""
    try:
        app_name = "Jarvis Assistant"
        app_path = sys.executable + " " + os.path.abspath(__file__)
        
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                            0, winreg.KEY_SET_VALUE)
        
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass  # Key doesn't exist, which is fine
                
        winreg.CloseKey(key)
        
        # Save to settings
        settings_manager.set_setting("system", "start_with_windows", enabled)
        return {"success": True}
    except Exception as e:
        print(f"Error setting startup: {e}")
        return {"success": False, "error": str(e)}

@eel.expose
def check_microphone_access():
    """Check microphone access permissions"""
    try:
        import pyaudio
        
        # Try to access microphone
        p = pyaudio.PyAudio()
        
        # Check if we can list audio devices
        device_count = p.get_device_count()
        has_input = False
        
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                has_input = True
                break
        
        p.terminate()
        
        if has_input:
            # Try to actually record a sample
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
            return {"success": True, "access": True, "message": "Microphone access granted"}
        else:
            return {"success": True, "access": False, "message": "No input devices found"}
            
    except Exception as e:
        return {"success": True, "access": False, "message": f"Microphone access denied: {str(e)}"}

@eel.expose
def set_always_on_top(enabled):
    """Set window always on top (placeholder - requires advanced eel modification)"""
    try:
        # This is a limitation of eel - we can save the setting but can't apply it to existing window
        settings_manager.set_setting("display", "always_on_top", enabled)
        return {"success": True, "message": "Setting saved. Restart required for effect."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def set_theme_color(color):
    """Set the theme color for the interface"""
    try:
        settings_manager.set_setting("display", "theme_color", color)
        return {"success": True, "message": "Theme color saved successfully.", "color": color}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def updateMainPageTheme(color):
    """Update the main page theme"""
    try:
        # This will call the JavaScript function on the main page
        eel.updateThemeColor(color)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def get_theme_color():
    """Get the current theme color"""
    try:
        color = settings_manager.get_setting("display", "theme_color", "#00AAFF")
        return {"success": True, "color": color}
    except Exception as e:
        return {"success": False, "error": str(e), "color": "#00AAFF"}

@eel.expose
def set_minimize_to_tray(enabled):
    """Set minimize to tray functionality"""
    print(f"🔧 set_minimize_to_tray called with: {enabled}")
    try:
        print("💾 Saving setting to manager...")
        result = settings_manager.set_setting("display", "minimize_to_tray", enabled)
        print(f"💾 Settings save result: {result}")
        
        if enabled:
            print("🚀 Starting system tray...")
            # Start the system tray
            tray_result = jarvis_tray.start_tray()
            print(f"🚀 Tray start result: {tray_result}, Is running: {jarvis_tray.is_running}")
            
            if jarvis_tray.is_running:
                message = "Minimize to tray enabled. Tray icon is now active in your system notification area."
            else:
                message = "Minimize to tray enabled, but tray icon failed to start. Check console for errors."
        else:
            print("🛑 Stopping system tray...")
            # Stop the system tray
            tray_result = jarvis_tray.stop_tray()
            print(f"🛑 Tray stop result: {tray_result}, Is running: {jarvis_tray.is_running}")
            message = "Minimize to tray disabled. Tray icon removed."
        
        print(f"✅ Returning success: {message}")
        return {"success": True, "message": message}
    except Exception as e:
        print(f"❌ Exception in set_minimize_to_tray: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@eel.expose
def get_minimize_to_tray():
    """Get the current minimize to tray setting"""
    try:
        enabled = settings_manager.get_setting("display", "minimize_to_tray", False)
        
        # Ensure tray is running if enabled
        if enabled and not jarvis_tray.is_running:
            jarvis_tray.start_tray()
        elif not enabled and jarvis_tray.is_running:
            jarvis_tray.stop_tray()
            
        return {"success": True, "enabled": enabled}
    except Exception as e:
        return {"success": False, "error": str(e), "enabled": False}

# ==================== MEDIA SETTINGS ====================

@eel.expose
def toggle_media_setting(setting_name, enabled):
    """Toggle media control settings"""
    try:
        settings_manager.set_setting("media", setting_name, enabled)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== CONTACT SETTINGS ====================

@eel.expose
def toggle_contact_setting(setting_name, enabled):
    """Toggle contact management settings"""
    try:
        settings_manager.set_setting("contacts", setting_name, enabled)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def start():
    
    eel.init("www")

    # playAssistantSound()  # Commented out to fix startup error
    
    # Initialize tray if minimize to tray is enabled
    try:
        tray_enabled = settings_manager.get_setting("display", "minimize_to_tray", False)
        if tray_enabled:
            print("🚀 Starting system tray on app start...")
            jarvis_tray.start_tray()
    except Exception as e:
        print(f"Error initializing tray: {e}")
    
    @eel.expose
    def init():
        # subprocess.call([r'device.bat'])  # Mobile-related code commented out
        eel.hideStart()  # Show main UI
        # speak("Ready for Face Authentication")
        # flag = recoganize.AuthenticateFace()  # Face authentication removed
        # if flag == 1:
        #     eel.hideFaceAuth()
        #     speak("Face Authentication Successful")
        #     eel.hideFaceAuthSuccess()
        #     speak("Hello, Welcome Sir, How can i Help You")
        #     eel.hideStart()
        #     playAssistantSound()
        # else:
        #     speak("Face Authentication Fail")
        return "ok"  # Always return a value for eel
    
    # Define close callback to handle tray properly
    def close_callback(page, sockets):
        """Enhanced close callback with tray handling"""
        print(f"🔽 Window close event for page: {page}")
        try:
            tray_enabled = settings_manager.get_setting("display", "minimize_to_tray", False)
            print(f"Tray enabled: {tray_enabled}, Tray running: {jarvis_tray.is_running}")
            
            if tray_enabled and jarvis_tray.is_running:
                print("📥 Minimizing to tray instead of closing...")
                # Don't exit, just minimize to tray
                return False  # Return False to prevent window from closing
            else:
                print("🚪 Normal close - stopping tray and exiting...")
                if jarvis_tray.is_running:
                    jarvis_tray.stop_tray()
                
                # Force exit all processes
                import subprocess
                try:
                    subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                                 capture_output=True, timeout=2)
                except:
                    pass
                
                os._exit(0)
        except Exception as e:
            print(f"Error in close callback: {e}")
            os._exit(1)
    
    # os.system('start msedge.exe --app="http://localhost:8000/index.html"')  # Mobile-related code commented out
    # os.system('start msedge.exe --app="http://localhost:8000/index.html"')
    try:
        print("🌐 Starting EEL application...")
        eel.start('index.html', 
                  size=(450, 800),
                  position=(1500, 370),  # Left side positioning
                  mode='edge',
                  host='localhost',
                  block=True,
                  close_callback=close_callback)
    except Exception as e:
        print(f"Error starting EEL: {e}")
        if jarvis_tray.is_running:
            jarvis_tray.stop_tray()
        raise

if __name__ == "__main__":
    start()