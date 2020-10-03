import os


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
    
    return dest_path if os.path.exists(dest_path) else ""


darwin_packages = {
    "App Store:AppIcon": "app_store",
    "Reminders:Reminders": "bell",
    "Reminders:icon": "bell",
    "Calendar:App": "calendar",
    "Calendar:App-empty": "calendar",
    "Image Capture:ImageCapture": "capture",
    "Dashboard:Dashboard": "dashboard",
    "Font Book:appicon": "font",
    "Photos:AppIcon": "gallery",
    "Home:AppIcon-mac": "home",
    "Maps:maps": "location",
    "Messages:MessagesAppIcon": "message",
    "Siri:Siri": "microphone",
    "Mounty:AppIcon": "mountains",
    "iTunes:iTunes": "music",
    "Preview:Preview": "preview",
    "QuickTime Player:QuickTimePlayerX": "quicktime",
    "Automator:Automator": "robot_arm",
    "Automator:AutomatorApplet": "robot_arm",
    "Safari:compass": "safari",
    "Visual Studio Code:Code": "vscode",
    "Utilities/ColorSync Utility:ColorSyncUtility": "sync",
    "Utilities/Terminal:Terminal": "terminal",
    "Utilities/AU Lab:PPIcon": "wave",
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
