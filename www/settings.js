// Settings Page JavaScript
console.log('Settings.js loaded');

// Settings Management Functions
window.loadSettings = async function() {
    try {
        console.log('loadSettings called');
        const response = await eel.get_all_settings()();
        console.log('Settings response:', response);
        if (response.success) {
            applySettingsToUI(response.settings);
            console.log('Settings applied to UI');
        } else {
            console.error('Failed to load settings:', response);
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
};

window.saveAllSettings = async function() {
    console.log('saveAllSettings called');
    const settings = gatherSettingsFromUI();
    console.log('Gathered settings:', settings);
    
    let savedCount = 0;
    let totalCount = 0;
    
    for (const [category, categorySettings] of Object.entries(settings)) {
        for (const [key, value] of Object.entries(categorySettings)) {
            totalCount++;
            try {
                console.log(`Saving ${category}.${key} = ${value}`);
                const result = await eel.save_setting(category, key, value)();
                console.log(`Save result for ${category}.${key}:`, result);
                if (result.success) {
                    savedCount++;
                }
            } catch (error) {
                console.error(`Error saving ${category}.${key}:`, error);
            }
        }
    }
    
    console.log(`Saved ${savedCount}/${totalCount} settings`);
    showNotification(`Settings saved (${savedCount}/${totalCount})!`, savedCount === totalCount ? 'success' : 'warning');
};

window.resetAllSettings = async function() {
    if (confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
        try {
            const response = await eel.reset_all_settings()();
            if (response.success) {
                await loadSettings(); // Reload UI with defaults
                showNotification('All settings reset to defaults!', 'success');
            } else {
                showNotification('Failed to reset settings', 'error');
            }
        } catch (error) {
            console.error('Error resetting settings:', error);
            showNotification('Error resetting settings', 'error');
        }
    }
};

function applySettingsToUI(settings) {
    console.log('applySettingsToUI called with:', settings);
    
    // Assistant settings
    if (settings.assistant) {
        setToggle('voice-feedback', settings.assistant.voice_feedback_enabled);
        setToggle('continuous-listening', settings.assistant.continuous_listening);
        setToggle('wake-word-enabled', settings.assistant.wake_word_enabled);
        console.log('Applied assistant settings');
    }
    
    // Contact settings
    if (settings.contacts) {
        setToggle('format-phone', settings.contacts.auto_format_phone);
        setToggle('whatsapp-integration', settings.contacts.whatsapp_integration);
        console.log('Applied contact settings');
    }
    
    // Media settings
    if (settings.media) {
        setToggle('system-volume', settings.media.system_volume_control);
        setToggle('keyboard-shortcuts', settings.media.media_key_integration);
        setToggle('media-notifications', settings.media.youtube_shortcuts);
        console.log('Applied media settings');
    }
    
    // Display settings
    if (settings.display) {
        setToggle('always-on-top', settings.display.always_on_top);
        setToggle('minimize-to-tray', settings.display.minimize_to_tray);
        
        // Set theme color
        if (settings.display.theme_color) {
            const colorPicker = document.getElementById('themeColorPicker');
            if (colorPicker) {
                colorPicker.value = settings.display.theme_color;
                // Apply the color to the interface
                document.documentElement.style.setProperty('--primary-color', settings.display.theme_color);
            }
        }
        console.log('Applied display settings');
    }
    
    // System settings
    if (settings.system) {
        setToggle('start-with-windows', settings.system.start_with_windows);
        console.log('Applied system settings');
    }
}

function gatherSettingsFromUI() {
    console.log('gatherSettingsFromUI called');
    const settings = {
        assistant: {
            voice_feedback_enabled: getToggleState('voice-feedback'),
            continuous_listening: getToggleState('continuous-listening'),
            wake_word_enabled: getToggleState('wake-word-enabled')
        },
        contacts: {
            auto_format_phone: getToggleState('format-phone'),
            whatsapp_integration: getToggleState('whatsapp-integration')
        },
        media: {
            system_volume_control: getToggleState('system-volume'),
            media_key_integration: getToggleState('keyboard-shortcuts'),
            youtube_shortcuts: getToggleState('media-notifications')
        },
        display: {
            always_on_top: getToggleState('always-on-top'),
            minimize_to_tray: getToggleState('minimize-to-tray'),
            theme_color: getColorValue('themeColorPicker')
        },
        system: {
            start_with_windows: getToggleState('start-with-windows')
        }
    };
    console.log('Gathered settings:', settings);
    return settings;
}

function setToggle(toggleId, value) {
    const toggle = document.getElementById(toggleId);
    console.log(`Setting toggle ${toggleId} to ${value}, element:`, toggle);
    if (toggle) {
        toggle.checked = value;
        console.log(`✓ Set ${toggleId} = ${value}`);
    } else {
        console.error(`✗ Toggle element not found: ${toggleId}`);
    }
}

function getToggleState(toggleId) {
    const toggle = document.getElementById(toggleId);
    const state = toggle ? toggle.checked : false;
    console.log(`Getting toggle ${toggleId} state: ${state}`);
    return state;
}

function getColorValue(colorPickerId) {
    const colorPicker = document.getElementById(colorPickerId);
    const color = colorPicker ? colorPicker.value : '#00AAFF';
    console.log(`Getting color ${colorPickerId} value: ${color}`);
    return color;
}

function showNotification(message, type = 'info') {
    console.log(`Notification: ${message} (${type})`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Special handlers for specific settings
window.handleStartupToggle = async function(enabled) {
    try {
        const response = await eel.set_startup_enabled(enabled)();
        if (response.success) {
            showNotification(enabled ? 'Startup enabled' : 'Startup disabled', 'success');
        } else {
            showNotification('Failed to update startup setting', 'error');
            // Revert toggle
            setToggle('start-with-windows', !enabled);
        }
    } catch (error) {
        console.error('Error setting startup:', error);
        showNotification('Error updating startup setting', 'error');
        setToggle('start-with-windows', !enabled);
    }
};

window.checkMicrophoneAccess = async function() {
    try {
        const response = await eel.check_microphone_access()();
        if (response.access) {
            showNotification('Microphone access: ' + response.message, 'success');
        } else {
            showNotification('Microphone issue: ' + response.message, 'warning');
        }
    } catch (error) {
        console.error('Error checking microphone:', error);
        showNotification('Error checking microphone access', 'error');
    }
};

window.handleAlwaysOnTop = async function(enabled) {
    try {
        const response = await eel.set_always_on_top(enabled)();
        if (response.success) {
            showNotification(response.message || 'Always on top setting saved', 'info');
        } else {
            showNotification('Failed to update always on top setting', 'error');
        }
    } catch (error) {
        console.error('Error setting always on top:', error);
        showNotification('Error updating always on top setting', 'error');
    }
};

window.handleMinimizeToTray = async function(enabled) {
    try {
        console.log('handleMinimizeToTray called with:', enabled);
        console.log('About to call eel.set_minimize_to_tray...');
        
        const response = await eel.set_minimize_to_tray(enabled)();
        console.log('Minimize to tray response received:', response);
        
        if (response.success) {
            console.log('✅ Success response:', response.message);
            showNotification(response.message || 'Minimize to tray setting saved', 'success');
        } else {
            console.log('❌ Error response:', response.error);
            showNotification('Failed to update minimize to tray setting: ' + (response.error || 'Unknown error'), 'error');
            // Revert toggle
            setToggle('minimize-to-tray', !enabled);
        }
    } catch (error) {
        console.error('❌ Exception in handleMinimizeToTray:', error);
        showNotification('Error updating minimize to tray setting: ' + error.message, 'error');
        setToggle('minimize-to-tray', !enabled);
    }
};

// Auto-save settings when toggles change
function setupAutoSave() {
    console.log('Setting up auto-save...');
    const toggles = document.querySelectorAll('input[type="checkbox"]');
    console.log(`Found ${toggles.length} toggles`);
    
    toggles.forEach((toggle, index) => {
        console.log(`Setting up toggle ${index + 1}: ${toggle.id}`);
        toggle.addEventListener('change', function() {
            const toggleId = this.id;
            const enabled = this.checked;
            console.log(`Toggle changed: ${toggleId} = ${enabled}`);
            
            // Special handling for certain settings
            if (toggleId === 'start-with-windows') {
                handleStartupToggle(enabled);
            } else if (toggleId === 'always-on-top') {
                handleAlwaysOnTop(enabled);
            } else if (toggleId === 'minimize-to-tray') {
                handleMinimizeToTray(enabled);
            } else if (toggleId === 'wake-word-enabled') {
                handleWakeWordToggle(enabled);
            } else {
                // Regular settings - save after a brief delay
                setTimeout(() => {
                    console.log('Auto-saving settings...');
                    saveAllSettings();
                }, 100);
            }
        });
    });
    
    // Setup wake word input auto-save
    const wakeWordInput = document.getElementById('wake-word-input');
    const saveWakeWordBtn = document.getElementById('save-wake-word');
    
    if (wakeWordInput && saveWakeWordBtn) {
        // Save on button click
        saveWakeWordBtn.addEventListener('click', function() {
            const wakeWord = wakeWordInput.value.trim();
            if (wakeWord) {
                handleWakeWordChange(wakeWord);
            } else {
                showNotification('Wake word cannot be empty', 'error');
            }
        });
        
        // Save on Enter key press
        wakeWordInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                saveWakeWordBtn.click();
            }
        });
        
        // Validate input in real-time
        wakeWordInput.addEventListener('input', function() {
            const wakeWord = this.value.trim();
            const isValid = wakeWord.length >= 2;
            
            saveWakeWordBtn.disabled = !isValid;
            if (isValid) {
                saveWakeWordBtn.classList.remove('btn-outline-secondary');
                saveWakeWordBtn.classList.add('btn-outline-primary');
            } else {
                saveWakeWordBtn.classList.remove('btn-outline-primary');
                saveWakeWordBtn.classList.add('btn-outline-secondary');
            }
        });
    }
    
    // Setup theme color picker auto-save
    const colorPicker = document.getElementById('themeColorPicker');
    if (colorPicker) {
        colorPicker.addEventListener('change', function() {
            const color = this.value;
            console.log(`Theme color changed: ${color}`);
            
            // Apply color immediately to settings interface
            document.documentElement.style.setProperty('--primary-color', color);
            
            // Save to backend first, then refresh main page theme
            setTimeout(async () => {
                console.log('Auto-saving theme color...');
                try {
                    const result = await eel.set_theme_color(color)();
                    console.log('Theme color save result:', result);
                    
                    if (result.success) {
                        // Try to update main page directly
                        try {
                            await eel.updateMainPageTheme(color)();
                        } catch (e) {
                            console.log('Note: Main page update call failed (normal if main page not ready)');
                        }
                        
                        showNotification('Theme color updated!', 'success');
                    } else {
                        showNotification('Error saving theme color', 'error');
                    }
                    
                    // Also save all other settings
                    saveAllSettings();
                } catch (error) {
                    console.error('Error saving theme color:', error);
                    showNotification('Error saving theme color', 'error');
                }
            }, 100);
        });
        console.log('Theme color picker auto-save setup complete');
    }
    
    console.log('Auto-save setup complete');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings page DOM loaded');
    
    // Wait for EEL to be ready
    setTimeout(function() {
        console.log('Initializing settings...');
        if (typeof eel !== 'undefined') {
            loadSettings();
            loadWakeWordSettings(); // Load wake word specific settings
            setupAutoSave();
        } else {
            console.error('EEL not available');
        }
    }, 500);
});

// Wake Word Handler Functions
async function handleWakeWordChange(wakeWord) {
    console.log(`Setting wake word to: ${wakeWord}`);
    try {
        const result = await eel.set_wake_word(wakeWord)();
        console.log('Wake word result:', result);
        
        if (result.success) {
            showNotification(result.message, 'success');
            // Update the input to show the saved value
            const input = document.getElementById('wake-word-input');
            if (input) {
                input.value = result.wake_word;
            }
        } else {
            showNotification(result.error || 'Failed to save wake word', 'error');
        }
    } catch (error) {
        console.error('Error setting wake word:', error);
        showNotification('Error saving wake word', 'error');
    }
}

async function handleWakeWordToggle(enabled) {
    console.log(`Setting wake word detection: ${enabled}`);
    try {
        const result = await eel.set_wake_word_enabled(enabled)();
        console.log('Wake word toggle result:', result);
        
        if (result.success) {
            showNotification(result.message, 'success');
        } else {
            showNotification(result.error || 'Failed to save wake word detection setting', 'error');
        }
    } catch (error) {
        console.error('Error setting wake word detection:', error);
        showNotification('Error saving wake word detection setting', 'error');
    }
}

// Load wake word settings
async function loadWakeWordSettings() {
    try {
        // Load wake word
        const wakeWordResult = await eel.get_wake_word()();
        if (wakeWordResult.success) {
            const input = document.getElementById('wake-word-input');
            if (input) {
                input.value = wakeWordResult.wake_word;
            }
        }
        
        // Load wake word enabled status
        const enabledResult = await eel.get_wake_word_enabled()();
        if (enabledResult.success) {
            const toggle = document.getElementById('wake-word-enabled');
            if (toggle) {
                toggle.checked = enabledResult.enabled;
            }
        }
    } catch (error) {
        console.error('Error loading wake word settings:', error);
    }
}