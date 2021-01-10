from typing import List, Dict


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


def darwin_get_store() -> List[Dict[str, str]]:
    store_list = []

    for line in darwin_package_store.split("\n"):
        line = line.strip()
        if not line or not line.startswith("#"):  # WRONG LOGIC -> TODO: remove
            continue
        line = line[1:]  # WRONG LOGIC

        iconpath, svgname = line.split("=>")
        svgname, color = svgname.strip().split("@")

        store_item = {
            "dest": darwin_decode_path(iconpath.strip()),
            "svg": svgname.strip(),
            "color": color.strip(),
        }
        store_list.append(store_item)

    return store_list


darwin_package_store = """
    App Store>AppIcon       => app_store@blue
    AppCleaner>AppCleaner   => recycle@yellow
    Books>iBooksAppIcon     => book@red
    Calendar>App            => calendar@green
    Calendar>App-empty      => calendar@green
    Calculator>AppIcon      => calculator@pink
    Contacts>Contacts       => contact@blue
    Chess>Chess             => chess@pink
    Dashboard>Dashboard     => dashboard@blue
    Dictionary>Dictionary   => dictionary@yellow
    Facetime>AppIcon        => facetime@green
    Font Book>appicon       => font@blue
    Home>AppIcon-mac        => home@red
    iTunes>iTunes           => music@blue
    Launchpad>Launchpad     => rocket@green
    Mail>ApplicationIcon    => mail@yellow
    Mission Control>Expose  => mission@pink
    Maps>maps               => location@green
    Notes>AppIcon           => notes@red
    Photos>AppIcon          => gallery@yellow
    Preview>Preview         => preview@pink
    Reminders>icon          => bell@red
    Reminders>Reminders     => bell@red
    Safari>compass          => safari@blue
    Siri>Siri               => microphone@pink
    Stickies>Stickies       => pin@yellow
    Stocks>AppIcon_macOS    => stocks@red
    TextEdit>Edit           => paper@green
    Time Machine>backup     => time_machine@pink
    Automator>Automator         => robot_arm@blue
    Automator>AutomatorApplet   => robot_arm@blue
    Image Capture>ImageCapture  => capture@red
    Messages>MessagesAppIcon    => message@green
    Photo Booth>PhotoBoothIcon  => camera@pink
    System Preferences>PrefApp  => settings@green
    QuickTime Player>QuickTimePlayerX   => quicktime@blue
    Soundflower/Soundflowerbed>appIcon  => flower@yellow

    Utilities/AU Lab>PPIcon     => wave@green
    Utilities/Console>AppIcon   => wrench@red
    Utilities/Grapher>Grapher   => graph@pink
    Utilities/Terminal>Terminal => terminal@black
    Utilities/Disk Utility>AppIcon  => disk@yellow
    Utilities/Screenshot>AppIcon    => screenshot@blue
    Utilities/Boot Camp Assistant>DA    => windows@yellow
    Utilities/Keychain Access>AppIcon   => key@red
    Utilities/System Information>ASP    => microchip@black
    Utilities/Digital Color Meter>AppIcons  => color_picker@pink
    Utilities/Script Editor>SEScriptEditorX => script@black
    Utilities/Voiceover Utility>voiceover   => voiceover@yellow
    Utilities/Activity Monitor>ActivityMonitor  => wave@black
    Utilities/AirPort Utility>AirPortUtility    => wifi@green
    Utilities/Audio MIDI Setup>AudioMidiSetup   => midi@pink
    Utilities/Migration Assistant>MigrateAsst   => migration@red
    Utilities/ColorSync Utility>ColorSyncUtility    => sync@yellow
    Utilities/Bluetooth File Exchange>BluetoothFileExchange => bluetooth@blue

    e:/System/Library/CoreServices/Dock.app/Contents/Resources/finder.png           => finder@blue
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/finder@2x.png        => finder@blue
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull.png        => trash_full@pink
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull2.png       => trash_full@pink
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull@2x.png     => trash_full@pink
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashfull2@2x.png    => trash_full@pink
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty.png       => trash_empty@pink
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty2.png      => trash_empty@pink
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty@2x.png    => trash_empty@pink
    e:/System/Library/CoreServices/Dock.app/Contents/Resources/trashempty2@2x.png   => trash_empty@pink

    Python 3.7/IDLE>IDLE    => python_idle@yellow
    Python 3.7/Python Launcher>PythonLauncher   => python@red

    Firefox>firefox         => firefox@pink
    Visual Studio Code>Code => vscode@blue
    VLC>VLC                 => vlc@red
    VLC>VLC-Xmas            => vlc@red
    Mounty>AppIcon          => mountains@blue
    Paintbrush>AppIcon      => paintbrush@green
    GIMP-2.10>gimp          => gimp@green
    The Unarchiver>unarchiver   => zip@yellow
"""
