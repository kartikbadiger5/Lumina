    // Reset & Scan logic
    $("#resetScanBtn").on("click", function() {
        if(confirm("Are you sure you want to reset and scan? This will clear all previously scanned apps.")) {
            eel.reset_scanned_apps()(function(result) {
                if(result === 'ok') {
                    $("#scanAppsBtn").trigger("click");
                }
            });
        }
    });
$(document).ready(function () {
    // Load and apply theme color from settings
    loadAndApplyThemeColor();
    
    // Handle window minimize to tray
    window.addEventListener('beforeunload', function(e) {
        // Check if minimize to tray is enabled
        eel.get_minimize_to_tray()(function(response) {
            if (response && response.enabled) {
                console.log('Minimize to tray enabled, attempting to minimize...');
                eel.minimize_to_tray()(function(result) {
                    if (result && result.success) {
                        console.log('Successfully minimized to tray');
                    }
                });
            }
        });
    });

    // ==================== CUSTOM MODAL FUNCTIONS ====================
    
    function showCustomModal(title, message, onConfirm, isDangerous = false) {
        $("#modalTitle").text(title);
        $("#modalMessage").text(message);
        
        // Add danger class if it's a dangerous action
        if (isDangerous) {
            $("#modalConfirm").addClass("danger");
        } else {
            $("#modalConfirm").removeClass("danger");
        }
        
        $("#customModal").fadeIn(300);
        
        // Remove any existing event handlers
        $("#modalConfirm").off("click");
        $("#modalCancel").off("click");
        
        // Add new event handlers
        $("#modalConfirm").on("click", function() {
            $("#customModal").fadeOut(300);
            if (onConfirm) onConfirm();
        });
        
        $("#modalCancel").on("click", function() {
            $("#customModal").fadeOut(300);
        });
        
        // Close on overlay click
        $("#customModal").on("click", function(e) {
            if (e.target === this) {
                $("#customModal").fadeOut(300);
            }
        });
        
        // Close on Escape key
        $(document).on("keydown.modal", function(e) {
            if (e.key === "Escape") {
                $("#customModal").fadeOut(300);
                $(document).off("keydown.modal");
            }
        });
    }
    
    function showCustomAlert(title, message) {
        $("#modalTitle").text(title);
        $("#modalMessage").text(message);
        $("#modalConfirm").text("OK").removeClass("danger");
        $("#modalCancel").hide();
        
        $("#customModal").fadeIn(300);
        
        // Remove any existing event handlers
        $("#modalConfirm").off("click");
        
        // Add new event handler
        $("#modalConfirm").on("click", function() {
            $("#customModal").fadeOut(300);
            $("#modalCancel").show(); // Restore cancel button for future use
            $("#modalConfirm").text("Confirm"); // Restore confirm text
        });
        
        // Close on overlay click
        $("#customModal").on("click", function(e) {
            if (e.target === this) {
                $("#customModal").fadeOut(300);
                $("#modalCancel").show();
                $("#modalConfirm").text("Confirm");
            }
        });
        
        // Close on Escape key
        $(document).on("keydown.modal", function(e) {
            if (e.key === "Escape") {
                $("#customModal").fadeOut(300);
                $("#modalCancel").show();
                $("#modalConfirm").text("Confirm");
                $(document).off("keydown.modal");
            }
        });
    }

    // ==================== ACTION DROPDOWN FUNCTIONALITY ====================
    
    // Toggle dropdown menu
    $("#actionDropdownBtn").on("click", function(e) {
        e.stopPropagation();
        $("#actionDropdownMenu").toggleClass("show");
    });
    
    // Close dropdown when clicking outside
    $(document).on("click", function(e) {
        if (!$(e.target).closest('.action-dropdown-container').length) {
            $("#actionDropdownMenu").removeClass("show");
        }
    });
    
    // Shutdown functionality
    $("#shutdownBtn").on("click", function() {
        console.log('🔴 Shutdown button clicked - starting shutdown process');
        $("#actionDropdownMenu").removeClass("show");
        
        // Show custom centered modal instead of browser alert
        showCustomModal(
            "Shutdown Application", 
            "Are you sure you want to shutdown the application?", 
            function() {
                // This function runs when user confirms
                console.log('✅ User confirmed shutdown');
                
                // Show loading overlay for shutdown
                $("#loadingOverlay").fadeIn(300);
                
                try {
                    console.log('🔍 Checking EEL availability...');
                    console.log('EEL available:', typeof eel !== 'undefined');
                    console.log('shutdown_application available:', typeof eel !== 'undefined' && eel.shutdown_application);
                    
                    // Call backend shutdown immediately
                    if (typeof eel !== 'undefined' && eel.shutdown_application) {
                        console.log('📞 Calling backend shutdown...');
                        eel.shutdown_application()();
                        console.log('✅ Backend shutdown called');
                    } else {
                        console.error('❌ EEL or shutdown_application not available');
                        showCustomAlert('Error', 'EEL communication not available. Force closing...');
                    }
                    
                    // Force close after 1 second as requested
                    setTimeout(function() {
                        console.log('⏰ Force closing application after 1 second...');
                        
                        // Try multiple aggressive methods to close
                        try {
                            // Method 1: Standard window close
                            if (window.close) {
                                console.log('Trying window.close()...');
                                window.close();
                            }
                            
                            // Method 2: Chrome app window close
                            if (window.chrome && window.chrome.app && window.chrome.app.window) {
                                console.log('Trying Chrome app close...');
                                window.chrome.app.window.current().close();
                            }
                            
                            // Method 3: Electron main process exit
                            if (window.require) {
                                console.log('Trying Electron IPC...');
                                const { ipcRenderer } = window.require('electron');
                                ipcRenderer.send('app-quit');
                            }
                            
                            // Method 4: EEL force close if available
                            if (typeof eel !== 'undefined' && eel.forceCloseWindow) {
                                console.log('Trying EEL force close...');
                                eel.forceCloseWindow()();
                            }
                            
                            // Method 5: Navigate away and try to crash gracefully
                            setTimeout(() => {
                                console.log('Trying navigation fallback...');
                                window.location.href = 'about:blank';
                                
                                // Ultimate fallbacks
                                setTimeout(() => {
                                    if (window.process && window.process.exit) {
                                        window.process.exit(0);
                                    }
                                    // Force reload as final attempt
                                    window.location.reload(true);
                                }, 300);
                            }, 200);
                            
                        } catch (closeError) {
                            console.error('Error during forced closure:', closeError);
                            // Final fallback - just reload
                            window.location.reload(true);
                        }
                    }, 1000); // Exactly 1 second as requested
                    
                } catch (error) {
                    console.error('❌ Shutdown error:', error);
                    showCustomAlert('Shutdown Error', 'Error occurred during shutdown: ' + error.message);
                    $("#loadingOverlay").fadeOut(300);
                }
            },
            true // Mark as dangerous action (red button)
        );
    });
    
    // Restart functionality
    $("#restartBtn").on("click", function() {
        console.log('Restart clicked');
        $("#actionDropdownMenu").removeClass("show");
        
        // Show custom centered modal
        showCustomModal(
            "Restart Application", 
            "Are you sure you want to restart the application?", 
            function() {
                // This function runs when user confirms
                console.log('✅ User confirmed restart');
                
                // Show loading overlay
                $("#loadingOverlay").fadeIn(300);
                
                // Call restart function
                eel.restart_application()(function(response) {
                    console.log('Restart response:', response);
                    
                    // Wait a moment and then reload the page
                    setTimeout(function() {
                        window.location.reload();
                    }, 2000);
                });
            },
            false // Not a dangerous action (normal blue button)
        );
    });
    
    // --- Application Scanner UI Logic ---
    $("#scanAppsBtn").on("click", function() {
        $("#scanLoading").show();
        $("#scanResults").hide();
        $("#appsTableBody").empty();
        console.log('Starting scan_desktop_apps eel call...');
        eel.scan_desktop_apps()(function(result) {
            console.log('scan_desktop_apps eel call returned:', result);
            $("#scanLoading").hide();
            $("#scanResults").show();
            $("#appsTableBody").empty();
            if (result && result.status === 'already_scanned') {
                $("#appsTableBody").append('<tr><td>All applications are already scanned and stored.</td></tr>');
                if (result.all_apps && result.all_apps.length > 0) {
                    result.all_apps.forEach(function(app) {
                        $("#appsTableBody").append(`<tr><td>${app.name}</td></tr>`);
                    });
                }
            } else if (result && result.status === 'new_scanned' && result.apps.length > 0) {
                window.scannedApps = result.all_apps;
                result.all_apps.forEach(function(app) {
                    $("#appsTableBody").append(`<tr><td>${app.name}</td></tr>`);
                });
            } else {
                $("#appsTableBody").append('<tr><td>No applications found.</td></tr>');
            }
        });
    });

    eel.init()()

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },

    });

    // Siri configuration - Optimized for 400px window
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 350,  // Reduced from 800 to fit 400px window
        height: 100, // Reduced from 200 for better proportions
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
      });

    // Siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },

    });

    // mic button click event

    $("#MicBtn").click(function () { 
        eel.playAssistantSound()
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands()()
    });

    // Wake word activation function (called from Python when "lumina" is detected)
    function activateAssistantUI() {
        console.log("Wake word detected - activating UI");
        
        // Show wake word detection status
        $("#statusText").text("Wake word detected! Listening...").show();
        
        // Hide oval and show SiriWave
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        
        // Add visual feedback - pulse effect
        $("#statusText").addClass("pulse-effect");
        
        // Use default theme color for status text
        $("#statusText").css("color", "#00AAFF");
        
        // Remove pulse effect after a moment
        setTimeout(() => {
            $("#statusText").removeClass("pulse-effect");
        }, 2000);
    }

    // Expose the function to be called from Python
    eel.expose(activateAssistantUI);


    function doc_keyUp(e) {
        // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time

        if (e.key === 'j' && e.metaKey) {
            eel.playAssistantSound()
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // to play assistant 
    function PlayAssistant(message) {
        if (message != "") {
            // Show recognizing for typed command
            $("#statusText").text("Recognizing...").show();
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands(message)(function(response) {
                // After response, hide status and return to ready
                $("#statusText").text("").hide();
            });
            $("#chatbox").val("")
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
    }

    // toogle fucntion to hide and display mic and send button 
    function ShowHideButton(message) {
        if (message.length == 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
        else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // key up event handler on text box
    $("#chatbox").keyup(function () {

        let message = $("#chatbox").val();
        ShowHideButton(message)
    
    });
    
    // send button event handler
    $("#SendBtn").click(function () {
    
        let message = $("#chatbox").val()
        PlayAssistant(message)
    
    });
    

    // enter press event handler on chat box
    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            let message = $("#chatbox").val()
            PlayAssistant(message)
        }
    });

// Load and apply theme color from backend settings
async function loadAndApplyThemeColor() {
    try {
        console.log('Loading theme color from settings...');
        const response = await eel.get_theme_color()();
        console.log('Theme color response:', response);
        
        if (response.success && response.color) {
            const themeColor = response.color;
            console.log('Applying theme color:', themeColor);
            
            // Apply to the hood (particle effects)
            applyHoodTheme(themeColor);
            
            // Apply to status text
            $("#statusText").css("color", themeColor);
            
            // Apply to CSS custom properties for overall theme
            document.documentElement.style.setProperty('--primary-color', themeColor);
            document.documentElement.style.setProperty('--theme-color', themeColor);
            
            // Apply to specific UI elements
            applyThemeToUIElements(themeColor);
            
        } else {
            console.log('Using default theme color');
            const defaultColor = "#00AAFF";
            applyHoodTheme(defaultColor);
            $("#statusText").css("color", defaultColor);
            document.documentElement.style.setProperty('--primary-color', defaultColor);
            document.documentElement.style.setProperty('--theme-color', defaultColor);
        }
    } catch (error) {
        console.error('Error loading theme color:', error);
        // Fallback to default
        const defaultColor = "#00AAFF";
        applyHoodTheme(defaultColor);
        $("#statusText").css("color", defaultColor);
    }
}

// Apply theme color to the hood particles
function applyHoodTheme(color) {
    function hexToRgb(hex) {
        hex = hex.replace('#', '');
        if (hex.length === 3) {
            hex = hex.split('').map(x => x + x).join('');
        }
        const num = parseInt(hex, 16);
        return [num >> 16, (num >> 8) & 255, num & 255];
    }
    
    const [r, g, b] = hexToRgb(color);
    $(".square span").each(function() {
        const gradient = `radial-gradient(rgba(${r},${g},${b},0.08) 40%, rgba(${r},${g},${b},0.25) 70%, rgba(${r},${g},${b},0) 100%)`;
        const shadow = `0 0 50px ${color}, inset 0 0 50px ${color}`;
        $(this).css({
            'background-image': gradient,
            'box-shadow': shadow
        });
    });
}

// Apply theme color to various UI elements
function applyThemeToUIElements(color) {
    // Apply to buttons with theme color
    $('.btn-primary').css({
        'background-color': color,
        'border-color': color
    });
    
    // Apply to links and accents
    $('.text-primary').css('color', color);
    
    // Apply to form controls focus
    $('input:focus, textarea:focus').css({
        'border-color': color,
        'box-shadow': `0 0 0 0.2rem ${color}40`
    });
    
    // Apply to any elements with data-theme attribute
    $('[data-theme="primary"]').css('color', color);
    
    // Don't apply theme colors to action dropdown button - keep it clean
    // Only apply to restart button hover
    $('.restart-btn:hover').css({
        'background-color': color + '33', // 20% opacity
        'color': color
    });
    
    // Convert hex to RGB for CSS custom properties
    const rgb = hexToRgb(color);
    if (rgb) {
        document.documentElement.style.setProperty('--theme-color-rgb', `${rgb.r}, ${rgb.g}, ${rgb.b}`);
    }
}

// Helper function to convert hex to RGB
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

// Function to refresh theme (can be called from settings)
window.refreshTheme = function() {
    loadAndApplyThemeColor();
};

// Function that can be called by EEL to update theme
eel.expose(updateThemeColor);
function updateThemeColor(color) {
    console.log('Received theme color update:', color);
    
    // Apply to the hood (particle effects)
    applyHoodTheme(color);
    
    // Apply to status text
    $("#statusText").css("color", color);
    
    // Apply to CSS custom properties for overall theme
    document.documentElement.style.setProperty('--primary-color', color);
    document.documentElement.style.setProperty('--theme-color', color);
    
    // Apply to specific UI elements
    applyThemeToUIElements(color);
    
    console.log('Theme updated to:', color);
}

// Function to restore window from tray (called from backend)
eel.expose(restoreFromTray);
function restoreFromTray() {
    console.log('Restoring window from tray...');
    // Bring window to focus
    window.focus();
    // Show window if hidden  
    if (document.hidden) {
        document.visibilityState = 'visible';
    }
    // Try to show the window again
    if (window.chrome && window.chrome.app && window.chrome.app.window) {
        window.chrome.app.window.current().show();
    }
}

// Function to force close window (called from backend)
eel.expose(forceCloseWindow);
function forceCloseWindow() {
    console.log('Force closing window from backend...');
    setTimeout(function() {
        try {
            window.close();
            
            // If that doesn't work, try other methods
            if (window.chrome && window.chrome.app && window.chrome.app.window) {
                window.chrome.app.window.current().close();
            }
            
            // Navigate away as last resort
            window.location.href = 'about:blank';
        } catch (e) {
            console.log('Error in force close:', e);
        }
    }, 100);
}


});