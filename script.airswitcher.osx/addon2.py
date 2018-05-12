import xbmcaddon
import xbmcgui
import xbmc
import subprocess
import time

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

device1 = "Gavs iPhone 6+"
device2 = "Gavs iPad Air"
device3 = "Gavs iPhone 4s"
device4 = "Disable"

dialog = xbmcgui.Dialog()
ret = dialog.select('Choose an AirPlay Device:', [device1, device2, device3, device4])

if ret is -1:
    exit()


if ret == 3: #Default
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.config","value":2}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.guisoundmode","value":2}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.passthrough","value":true}, "id":1}')
else: #Airplay
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.passthrough","value":false}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.config","value":1}, "id":2}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.guisoundmode","value":0}, "id":1}')



##APPLESCRIPT
xbmc.log( "airswitcher applescript starting" )
#os.system("/usr/bin/osascript /Users/gavin/Desktop/Airplay.scpt %s" % answer)
script = '''
	if "%s" equals "0" then
		set kodidev to "Gavs iPhone 6+"
		deviceSwitch(kodidev)
	else if "%s" equals "1" then
		set kodidev to "AirFloat"
		deviceSwitch(kodidev)
	else if "%s" equals "2" then
		set kodidev to "Gavs iPhone 4s"
		deviceSwitch(kodidev)
	else if "%s" equals "3" then
		set kodidev to "Digital Out"
		deviceSwitch(kodidev)
	end if

    on deviceSwitch(kodidev)
	try
		tell application "System Events"
			tell process "SystemUIServer" to set btMenu to (menu bar item 1 of menu bar 1 whose description contains "volume")
			tell btMenu
				click
				delay 1
				try
					tell (menu item kodidev of menu 1) to click
				on error
					try
						delay 1
						tell (menu item kodidev of menu 1) to click
					on error
						try
                            delay 2
						    tell (menu item kodidev of menu 1) to click
                        on error
                            display dialog "Error Connecting to device :(" with title "AirSwitcher" giving up after 5
                            tell app "Kodi" to activate
                        end try
                    end try
				end try
			end tell
		end tell
	end try
    end deviceSwitch
''' % (ret, ret, ret, ret)
##APPLESCRIPT
proc = subprocess.Popen(['osascript', '-'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
stdout_output = proc.communicate(script)[0]
print stdout_output
xbmc.log( "airswitcher applescript finished" )

time.sleep(2)   # delays for 5 seconds. You can Also Use Float Value.

if ret == 3: #Default
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice","value":"Built-In Digital Output"}, "id":1}')
else: #Airplay
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice","value":"Gavs iPhone 6+"}, "id":1}')
