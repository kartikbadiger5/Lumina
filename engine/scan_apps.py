
import os
import json
import eel

import sqlite3
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jarvis.db')

import subprocess

def scan_uwp_apps():
    uwp_apps = []
    try:
        ps_command = (
            'Get-StartApps | Select-Object Name, AppID | ConvertTo-Json'
        )
        result = subprocess.run([
            'powershell', '-Command', ps_command
        ], capture_output=True, text=True, check=True)
        apps_json = result.stdout
        if apps_json:
            try:
                apps = json.loads(apps_json)
                if isinstance(apps, dict):
                    apps = [apps]
                for app in apps:
                    name = app.get('Name')
                    appid = app.get('AppID')
                    if name and appid:
                        uwp_apps.append({
                            'name': name,
                            'filename': name,
                            'extension': '.uwp',
                            'location': appid,
                            'type': 'uwp'
                        })
            except Exception:
                pass
    except Exception:
        pass
    return uwp_apps

def scan_applications():
    found_apps = []
    seen = set()
    for base_dir in SCAN_DIRS:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in APP_EXTENSIONS:
                    app_path = os.path.join(root, file)
                    app_name = os.path.splitext(file)[0]
                    key = (app_name.lower(), ext, app_path.lower())
                    if key not in seen:
                        found_apps.append({
                            'name': app_name,
                            'filename': file,
                            'extension': ext,
                            'location': app_path,
                            'type': 'classic'
                        })
                        seen.add(key)

    # Scan Start Menu for all .lnk files (including UWP/Store apps)
    for root, dirs, files in os.walk(START_MENU):
        for file in files:
            if file.lower().endswith('.lnk'):
                app_path = os.path.join(root, file)
                app_name = os.path.splitext(file)[0]
                key = (app_name.lower(), '.lnk', app_path.lower())
                if key not in seen:
                    found_apps.append({
                        'name': app_name,
                        'filename': file,
                        'extension': '.lnk',
                        'location': app_path,
                        'type': 'shortcut'
                    })
                    seen.add(key)

    # Add UWP apps
    uwp_apps = scan_uwp_apps()
    for app in uwp_apps:
        key = (app['name'].lower(), app['extension'], app['location'].lower())
        if key not in seen:
            found_apps.append(app)
            seen.add(key)
    return found_apps

@eel.expose
def scan_desktop_apps():
    """Eel-exposed version for frontend use. Always scan, and store only new apps in DB."""
    apps = scan_applications()
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT name, extension, location FROM sys_apps')
    existing = set((row[0].lower(), row[1], row[2].lower()) for row in cursor.fetchall())
    new_apps = [app for app in apps if (app['name'].lower(), app['extension'], app['location'].lower()) not in existing]
    for app in new_apps:
        cursor.execute('INSERT INTO sys_apps (name, extension, location) VALUES (?, ?, ?)',
                       (app['name'], app['extension'], app['location']))
    con.commit()
    con.close()
    
    total_count = len(apps)
    if new_apps:
        return {'success': True, 'status': 'new_scanned', 'count': total_count, 'new_count': len(new_apps)}
    else:
        return {'success': True, 'status': 'already_scanned', 'count': total_count, 'new_count': 0}

def reset_and_scan():
    """Clear all existing apps from database and rescan"""
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        
        # Clear existing apps
        cursor.execute('DELETE FROM sys_apps')
        con.commit()
        
        # Rescan all applications
        apps = scan_applications()
        
        # Insert all apps
        for app in apps:
            cursor.execute('INSERT INTO sys_apps (name, extension, location) VALUES (?, ?, ?)',
                           (app['name'], app['extension'], app['location']))
        
        con.commit()
        con.close()
        
        return {'success': True, 'count': len(apps)}
    except Exception as e:
        print(f"Error in reset_and_scan: {e}")
        return {'success': False, 'count': 0}

# Directories to scan for desktop applications (Windows typical locations)
PROGRAM_FILES = os.environ.get('ProgramFiles', r'C:\Program Files')
PROGRAM_FILES_X86 = os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')
DESKTOP = os.path.join(os.environ['USERPROFILE'], 'Desktop')
START_MENU = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs')

SCAN_DIRS = [PROGRAM_FILES, PROGRAM_FILES_X86, DESKTOP, START_MENU]


# File extensions considered as desktop applications
APP_EXTENSIONS = ['.exe', '.lnk', '.bat', '.cmd', '.msi']

