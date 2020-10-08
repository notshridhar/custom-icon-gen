def darwin_decode_path(coded_path: str) -> str:
    """
    Construct full path from shortened path
    ---------------------------------------
    Returns full path if path exists
    Returns empty string otherwise
    """
    part1, part2 = coded_path.split(":")

    if part1 == "e":
        # explicit path
        dest_path = part2
    else:
        # app icon convention
        dest_path = f"/Applications/{part1}.app/Contents/Resources/{part2}.icns"
    
    return dest_path


darwin_packages = {
    "App Store:AppIcon": "app_store",
    "AppCleaner:AppCleaner": "recycle",
    "Reminders:Reminders": "bell",
    "Reminders:icon": "bell",
    "Books:iBooksAppIcon": "book",
    "Calendar:App": "calendar",
    "Calendar:App-empty": "calendar",
    "Calculator:AppIcon": "calculator",
    "Contacts:Contacts": "contact",
    "Chess:Chess": "chess",
    "Dictionary:Dictionary": "dictionary",
    "Facetime:AppIcon": "facetime",
    "Photo Booth:PhotoBoothIcon": "camera",
    "Image Capture:ImageCapture": "capture",
    "Dashboard:Dashboard": "dashboard",
    "Firefox:firefox": "firefox",
    "Font Book:appicon": "font",
    "Photos:AppIcon": "gallery",
    "GIMP-2.10:gimp": "gimp",
    "Utilities/Grapher:Grapher": "graph",
    "Home:AppIcon-mac": "home",
    "Mail:ApplicationIcon": "mail",
    "Mission Control:Expose": "mission",
    "Maps:maps": "location",
    "Messages:MessagesAppIcon": "message",
    "Siri:Siri": "microphone",
    "Mounty:AppIcon": "mountains",
    "iTunes:iTunes": "music",
    "Notes:AppIcon": "notes",
    "Paintbrush:AppIcon": "paintbrush",
    "Stickies:Stickies": "pin",
    "TextEdit:Edit": "paper",
    "Time Machine:backup": "time_machine",
    "Preview:Preview": "preview",
    "QuickTime Player:QuickTimePlayerX": "quicktime",
    "Automator:Automator": "robot_arm",
    "Automator:AutomatorApplet": "robot_arm",
    "Launchpad:Launchpad": "rocket",
    "Safari:compass": "safari",
    "Soundflower/Soundflowerbed:appIcon": "flower",
    "Python 3.7/Python Launcher:PythonLauncher": "python",
    "Python 3.7/IDLE:IDLE": "python_idle",
    "Stocks:AppIcon_macOS": "stocks",
    "System Preferences:PrefApp": "settings",
    "VLC:VLC": "vlc",
    "VLC:VLC-Xmas": "vlc",
    "Visual Studio Code:Code": "vscode",
    "The Unarchiver:unarchiver": "zip",
    "Utilities/Activity Monitor:ActivityMonitor": "wave",
    "Utilities/Boot Camp Assistant:DA": "windows",
    "Utilities/Migration Assistant:MigrateAsst": "migration",
    "Utilities/Audio MIDI Setup:AudioMidiSetup": "midi",
    "Utilities/Keychain Access:AppIcon": "key",
    "Utilities/Bluetooth File Exchange:BluetoothFileExchange": "bluetooth",
    "Utilities/Digital Color Meter:AppIcons": "color_meter",
    "Utilities/Disk Utility:AppIcon": "disk",
    "Utilities/System Information:ASP": "microchip",
    "Utilities/Screenshot:AppIcon": "screenshot",
    "Utilities/Script Editor:SEScriptEditorX": "script",
    "Utilities/ColorSync Utility:ColorSyncUtility": "sync",
    "Utilities/Terminal:Terminal": "terminal",
    "Utilities/AU Lab:PPIcon": "wave",
    "Utilities/AirPort Utility:AirPortUtility": "wifi",
    "Utilities/Console:AppIcon": "wrench",
    "Utilities/Voiceover Utility:voiceover": "voiceover",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/finder.png": "finder",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/finder@2x.png": "finder",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull.png": "trash_full",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull2.png": "trash_full",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull@2x.png": "trash_full",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull2@2x.png": "trash_full",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty.png": "trash_empty",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty2.png": "trash_empty",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty@2x.png": "trash_empty",
    "e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty2@2x.png": "trash_empty",
}
