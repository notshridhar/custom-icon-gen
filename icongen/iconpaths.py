from typing import List, Tuple


def darwin_decode_path(encoded_path: str) -> str:
    """ Construct full path from shortened path """

    # explicit path
    if encoded_path.startswith("e:"):
        dest_path = encoded_path[2:]

    # app icon convention
    else:
        app_name, icon_name = encoded_path.split(">")
        dest_path = f"/Applications/{app_name}.app/Contents/Resources/{icon_name}.icns"

    return dest_path


def darwin_get_store() -> List[Tuple[str, str]]:
    store_list = []

    for line in darwin_package_store.split("\n"):
        line = line.strip()
        if not line or not line.startswith("#"):  # WRONG LOGIC -> TODO: remove
            continue
        line = line[1:]  # WRONG LOGIC
        iconpath, svgname = line.split("=>")
        iconpath = darwin_decode_path(iconpath.strip())
        store_list.append((iconpath, svgname.strip()))

    return store_list


darwin_package_store = """
    App Store>AppIcon       => app_store
    AppCleaner>AppCleaner   => recycle
    #Books>iBooksAppIcon     => book
    Calendar>App            => calendar
    Calendar>App-empty      => calendar
    Calculator>AppIcon      => calculator
    Contacts>Contacts       => contact
    Chess>Chess             => chess
    Dashboard>Dashboard     => dashboard
    Dictionary>Dictionary   => dictionary
    Facetime>AppIcon        => facetime
    Font Book>appicon       => font
    Home>AppIcon-mac        => home
    iTunes>iTunes           => music
    Launchpad>Launchpad     => rocket
    Mail>ApplicationIcon    => mail
    Mission Control>Expose  => mission
    Maps>maps               => location
    Notes>AppIcon           => notes
    Photos>AppIcon          => gallery
    Preview>Preview         => preview
    Reminders>icon          => bell
    Reminders>Reminders     => bell
    Safari>compass          => safari
    Siri>Siri               => microphone
    Stickies>Stickies       => pin
    Stocks>AppIcon_macOS    => stocks
    TextEdit>Edit           => paper
    Time Machine>backup     => time_machine
    Automator>Automator         => robot_arm
    Automator>AutomatorApplet   => robot_arm
    Image Capture>ImageCapture  => capture
    Messages>MessagesAppIcon    => message
    Photo Booth>PhotoBoothIcon  => camera
    System Preferences>PrefApp  => settings
    QuickTime Player>QuickTimePlayerX   => quicktime
    Soundflower/Soundflowerbed>appIcon  => flower

    Utilities/AU Lab>PPIcon     => wave
    Utilities/Console>AppIcon   => wrench
    Utilities/Grapher>Grapher   => graph
    Utilities/Terminal>Terminal => terminal
    Utilities/Disk Utility>AppIcon  => disk
    Utilities/Screenshot>AppIcon    => screenshot
    Utilities/Boot Camp Assistant>DA    => windows
    Utilities/Keychain Access>AppIcon   => key
    Utilities/System Information>ASP    => microchip
    Utilities/Digital Color Meter>AppIcons  => color_picker
    Utilities/Script Editor>SEScriptEditorX => script
    Utilities/Voiceover Utility>voiceover   => voiceover
    Utilities/Activity Monitor>ActivityMonitor  => wave
    Utilities/AirPort Utility>AirPortUtility    => wifi
    Utilities/Audio MIDI Setup>AudioMidiSetup   => midi
    Utilities/Migration Assistant>MigrateAsst   => migration
    Utilities/ColorSync Utility>ColorSyncUtility    => sync
    Utilities/Bluetooth File Exchange>BluetoothFileExchange => bluetooth

    e:/System/Library/CoreServices/Dock.app/Contents/Resources/finder.png           => finder
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/finder@2x.png        => finder
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull.png        => trash_full
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull2.png       => trash_full
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull@2x.png     => trash_full
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull2@2x.png    => trash_full
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty.png       => trash_empty
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty2.png      => trash_empty
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty@2x.png    => trash_empty
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty2@2x.png   => trash_empty

    Python 3.7/IDLE>IDLE    => python_idle
    Python 3.7/Python Launcher>PythonLauncher   => python

    Firefox>firefox         => firefox
    Visual Studio Code>Code => vscode
    VLC>VLC                 => vlc
    VLC>VLC-Xmas            => vlc
    Mounty>AppIcon          => mountains
    Paintbrush>AppIcon      => paintbrush
    GIMP-2.10>gimp          => gimp
    The Unarchiver>unarchiver   => zip
"""
