import xbmcaddon
import xbmcgui
import xbmc
import subprocess
import time
import os

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

device1 = "Gavs iPhone 6+"
device2 = "Gavs iPad Air"
device3 = "Gavs iPhone 4s"
device4 = "Disable Airplay"

##Get VPN Status and set dialog label

##Tunnelblick/MacSentry
process = subprocess.Popen(['pgrep', 'Tunnelblick'], stdout=subprocess.PIPE)
#process = subprocess.Popen(['pgrep', 'MacSentry'], stdout=subprocess.PIPE)
process.wait()
if not process.returncode:
    vpnlabel = "VPN is On"
else:
    vpnlabel = "VPN is Off"


##Native Network
# process = subprocess.Popen(["networksetup", "getcurrentlocation"], stdout=subprocess.PIPE)
# location = process.communicate()
# if "VPN\n" not in location:
#     vpnlabel = "VPN is Off"
# else:
#     vpnlabel = "VPN is On"



#####################################


dialog = xbmcgui.Dialog()
ret = dialog.select('Choose an AirPlay Device:', [device1, device2, device3, device4, vpnlabel])

if ret is 0:
    hsid = "i6"
if ret is 1:
    hsid = "iP"
if ret is 2:
    hsid = "i4"
if ret is 3:
    hsid = "Dis"
if ret is 4:
    hsid = "vpn"
if ret is -1:
    exit()


if ret == 3: #BuiltIn Audio
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.config","value":2}, "id":1}')
#    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.guisoundmode","value":2}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.passthrough","value":true}, "id":1}')
else: #Airplay
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.passthrough","value":false}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.config","value":1}, "id":2}')
#    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.guisoundmode","value":0}, "id":1}')



##HAMMERSPOON
xbmc.log( "HammerSpoon starting" )
os.system("open -g hammerspoon://%s" % hsid)
xbmc.log( "Hammerspoon finished" )

time.sleep(2)   # delays for 2 seconds. You can Also Use Float Value.

if ret == 0: #iPhone 6+
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice","value":"Gavs iPhone 6+"}, "id":1}')
if ret == 1: #iPad
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice","value":"Gavs iPad Air"}, "id":1}')
if ret == 2: #iPhone 4s
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice","value":"Gavs iPhone 4s"}, "id":1}')
if ret == 3: #Built-In
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice","value":"Built-In Digital Output"}, "id":1}')
