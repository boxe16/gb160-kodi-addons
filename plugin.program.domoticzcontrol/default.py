#   Title: Domoticz Control
#   Author: Chopper_Rob
#   Date: 1-1-2015
#   Info: Simple control function for Domoticz
#   URL : https://www.chopperrob.nl/domoticz/11-xbmc-kodi-status-in-domoticz
#   Version : 0.0.6
#

import os
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import re, traceback
import urllib, urlparse, urllib2, base64, json


__addon__       = xbmcaddon.Addon()
__addon_id__    = "plugin.program.domoticzcontrol"
__author__      = "Chopper Rob"
__url__         = "https://www.chopperrob.nl"
__version__     = "0.0.6"


__language__    = xbmcaddon.Addon(__addon_id__).getLocalizedString
CWD             = xbmcaddon.Addon(__addon_id__).getAddonInfo('path')
__addonname__   = __addon__.getAddonInfo('id')
__dataroot__    = xbmc.translatePath('special://profile/addon_data/%s' % __addonname__ ).decode('utf-8')
RESOURCE_PATH   = os.path.join(CWD, "resources" )

DomoticzIP      = xbmcaddon.Addon(__addon_id__).getSetting('ip')
DomoticzPort    = xbmcaddon.Addon(__addon_id__).getSetting('port')
DomoticzUser    = xbmcaddon.Addon(__addon_id__).getSetting('user')
DomtoiczPwd     = xbmcaddon.Addon(__addon_id__).getSetting('pwd')
ListType        = int(xbmcaddon.Addon(__addon_id__).getSetting('listtype'))
CustomIdxs      = xbmcaddon.Addon(__addon_id__).getSetting('customidxs')
NameRoomplan    = xbmcaddon.Addon(__addon_id__).getSetting('nameroomplan')
ShowItems       = 16

ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ITEM_HEIGHT = 36

__IDX__     = 0
__NAME__    = 1
__TYPE__    = 2
__IMAGE__   = 3
__STATUS__  = 4



class MainGUI(xbmcgui.WindowXMLDialog):
    def __init__(self,*args,**kwargs):
        pass

    def onInit(self):
        self.CurrentListType = 0
        self.domoticz = clsDomoticz()
        self.Loadlist(ListType)

    def Loadlist(self, ListNumber):
        self.getControl( 112 ).reset()
        xbmc.log ("laad nieuw lijst" + str(ListNumber))

        self.CurrentListType = ListNumber
        xbmc.log ("CurrentListType Loadlist: " + str(self.CurrentListType))
        if ListNumber == 0 :
            self.devices = self.domoticz.list_switches(0, 0)
            self.getControl( 113 ).setLabel (__language__(30201).title())
        if ListNumber == 1 :
            self.devices = self.domoticz.list_switches(1, 0)
            self.getControl( 113 ).setLabel (__language__(30202).title())
        if ListNumber == 2 :
            self.devices = self.domoticz.list_switches(0, self.domoticz.get_roomid(NameRoomplan))
            self.getControl( 113 ).setLabel (NameRoomplan.title())
        if ListNumber == 3 :
            self.devices = self.domoticz.list_scenes()
            self.getControl( 113 ).setLabel (__language__(30204).title())
        if ListNumber == 4 :
            self.devices = self.domoticz.list_customswitches(CustomIdxs)
            self.getControl( 113 ).setLabel (__language__(30205).title())

        if len(self.devices) < int(ShowItems):
            self.getControl( 111 ).setHeight ( 77 + (len(self.devices) * ITEM_HEIGHT) )
            self.getControl( 112 ).setHeight ( len(self.devices) * ITEM_HEIGHT )
        else:
            self.getControl( 111 ).setHeight ( 77 + (ShowItems * ITEM_HEIGHT) )
            self.getControl( 112 ).setHeight ( (ShowItems * ITEM_HEIGHT) )

        for item in self.devices:
            listitem = xbmcgui.ListItem( label = item[__NAME__] )

            listitem.setIconImage( item[__IMAGE__] )
            listitem.setProperty( "idx", item[__IDX__] )

            self.getControl( 112 ).addItem( listitem )

        self.setFocus(self.getControl(112))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_BACK:
            self.close()
        if action == ACTION_MOVE_LEFT:
            xbmc.log ("CurrentListType Action: " + str(self.CurrentListType))
            currentList = self.CurrentListType

            if currentList == 0 and CustomIdxs != "":
                currentList = 4
            elif currentList == 0 and CustomIdxs == "":
            	currentList = 3
            elif currentList == 3 and NameRoomplan == "":
            	currentList = 1
            else:
                currentList = int(currentList) - 1
            self.Loadlist(currentList)
            xbmc.log ("CURRENTLIST: " + str(currentList))

        if action == ACTION_MOVE_RIGHT:
            xbmc.log ("CurrentListType Action: " + str(self.CurrentListType))
            currentList = self.CurrentListType
            if currentList == 4:
            	currentList = 0
            elif currentList == 3 and CustomIdxs == "":
            	currentList = 0
            elif currentList == 1 and NameRoomplan == "":
            	currentList = 3
            else:
                currentList = int(currentList) + 1
            self.Loadlist(currentList)
            xbmc.log ("CURRENTLIST: " + str(currentList))

    def onClick(self, controlID):
        currentList = self.CurrentListType
        xbmc.log ("ONCLICK CURRENTLIST: " + str(currentList))

        xbmc.log ("CONTROL ID: " + str(controlID))
        if controlID == 112:
            idx = str(self.getControl(112).getSelectedItem().getProperty("idx"))
            xbmc.log ("ONCLICK SELECTED : " + idx)

            for item in self.devices:
                xbmc.log ("ONCLICK ITEM : " + str(item))
                xbmc.log ("ONCLICK LISTTYPE : " + str(ListType))
                if item[__IDX__] == idx and (item[__STATUS__] == 0 or item[__STATUS__] == 2):
                    if currentList == 3:
                        self.domoticz.set_scenestatus(idx, 1)
                    else:
                        self.domoticz.set_switchstatus(idx, 1)
                elif item[__IDX__] == idx and item[__STATUS__] == 1:
                    if currentList == 3:
                        self.domoticz.set_scenestatus(idx, 0)
                    else:
                        self.domoticz.set_switchstatus(idx, 0)
            self.close()

    def onFocus(self, controlID):
        pass

class clsDomoticz:
    def __init__(self):
        self.base64string = base64.encodestring('%s:%s' % (DomoticzUser, DomtoiczPwd)).replace('\n', '')

    def load_json(self, url):
        request = urllib2.Request(url)
        request.add_header("Authorization", "Basic %s" % self.base64string)
        return urllib2.urlopen(request).read()

    # takes 2 arguments. first if only favorites should be listed (0 or 1) and the second is the plan id. if no plan is selected it should be 0
    def list_switches(self, IsFavorite, plan):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=devices&filter=all&used=true&order=Name'
        if int(plan) > 0:
            self.url += "&plan=" + str(plan)

        array_id = []
        json_object = json.loads(self.load_json(self.url))

        status = -2
        if json_object["status"] == "OK":
            status = -1
            for i, v in enumerate(json_object["result"]):
                item = []
                if ((IsFavorite == 1 and json_object["result"][i]["Favorite"] == 1) or IsFavorite == 0) and "Lighting" in json_object["result"][i]["Type"] :
                    item.append (json_object["result"][i]["idx"])
                    item.append (json_object["result"][i]["Name"])
                    item.append (json_object["result"][i]["Type"])

                    # Image
                    if json_object["result"][i]["SwitchType"] == "Contact":
                        if json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/contact48_Open.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/contact48.png")
                    elif json_object["result"][i]["SwitchType"] == "Door Lock":
                        if json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/door48open.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/door48.png")
                    elif json_object["result"][i]["SwitchType"] == "Dimmer":
                        if json_object["result"][i]["Status"] == "On":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/dimmer48-on.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/dimmer48-off.png")
                    elif "Blinds" in json_object["result"][i]["SwitchType"]:
                        if json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/blindsopen48sel.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/blinds48.png")
                    elif json_object["result"][i]["SwitchType"] == "Doorbell":
                        item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/doorbell48.png")
                    elif json_object["result"][i]["SwitchType"] == "Smoke Detector":
                        if json_object["result"][i]["Status"] == "On":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/smoke48on.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/smoke48off.png")
                    elif json_object["result"][i]["SwitchType"] == "X10 Siren":
                        if json_object["result"][i]["Status"] == "On" or json_object["result"][i]["Status"] == "All On":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/siren-on.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/siren-off.png")
                    else:
                        if json_object["result"][i]["Status"] == "On" or json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_On.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_Off.png")

                    # Status
                    if json_object["result"][i]["Status"] == "On" or json_object["result"][i]["Status"] == "Open" or json_object["result"][i]["Status"] == "All On":
                        item.append (1)
                    if json_object["result"][i]["Status"] == "Off" or json_object["result"][i]["Status"] == "Closed" or json_object["result"][i]["Status"] == "All Off":
                        item.append (0)
                    if json_object["result"][i]["Status"] == "Mixed":
                        item.append (2)

                if len(item) > 0:
                    array_id.append (item)
            return array_id

    def list_scenes(self):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=scenes'
        array_id = []
        json_object = json.loads(self.load_json(self.url))

        status = -2
        if json_object["status"] == "OK":
            status = -1
            for i, v in enumerate(json_object["result"]):
                item = []

                item.append (json_object["result"][i]["idx"])
                item.append (json_object["result"][i]["Name"])
                item.append (json_object["result"][i]["Type"])

                # Image
                if json_object["result"][i]["Type"] == "Scene":
                    item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/push48.png")
                elif json_object["result"][i]["Type"] == "Group" and json_object["result"][i]["Status"] == "On":
                    item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/push48.png")
                elif json_object["result"][i]["Type"] == "Group" and json_object["result"][i]["Status"] == "Off":
                    item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/pushoff48.png")
                elif json_object["result"][i]["Type"] == "Group" and json_object["result"][i]["Status"] == "Mixed":
                    item.append ("pushmixed48.png")
                else:
                    item.append ("")

                # Status
                if json_object["result"][i]["Status"] == "On":
                    item.append (1)
                if json_object["result"][i]["Status"] == "Off":
                    item.append (0)
                if json_object["result"][i]["Status"] == "Mixed":
                    item.append (2)

                if len(item) > 0:
                    array_id.append (item)
                xbmc.log ("SCENE " + str(item))

            xbmc.log ("ARRAY ID " + str(array_id))
            return array_id

    def list_customswitches(self, idxs):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=devices&filter=all&used=true&order=Name'
        array_idx = idxs.split(",")
        array_id = []
        json_object = json.loads(self.load_json(self.url))

        status = -2
        if json_object["status"] == "OK":
            status = -1
            for i, v in enumerate(json_object["result"]):
                item = []
                if json_object["result"][i]["idx"] in array_idx and "Lighting" in json_object["result"][i]["Type"] :
                    item.append (json_object["result"][i]["idx"])
                    item.append (json_object["result"][i]["Name"])
                    item.append (json_object["result"][i]["Type"])

                    # Image
                    if json_object["result"][i]["Status"] == "On":
                        item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_On.png")
                    else:
                        item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_Off.png")

                    # Status
                    if json_object["result"][i]["Status"] == "On":
                        item.append (1)
                    if json_object["result"][i]["Status"] == "Off":
                        item.append (0)
                    if json_object["result"][i]["Status"] == "Mixed":
                        item.append (2)

                if len(item) > 0:
                    array_id.append (item)
            return array_id

    def get_roomid(self, roomname):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=plans'
        json_object = json.loads(self.load_json(self.url))
        roomid = 0
        if json_object["status"] == "OK":
            for i, v in enumerate(json_object["result"]):
                if json_object["result"][i]["Name"].lower() == str(roomname).lower() :
                    roomid = json_object["result"][i]["idx"]
        return roomid

    def set_switchstatus (self, switchid, status):
        update_domoticz = 0
        if status == 1:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchlight&idx=" + str(switchid) + "&switchcmd=On&level=0"
            update_domoticz = 1
        if status == 0:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchlight&idx=" + str(switchid) + "&switchcmd=Off&level=0"
            update_domoticz = 1

        if update_domoticz:
            request = urllib2.Request(self.url)
            request.add_header("Authorization", "Basic %s" % self.base64string)
            self.response = urllib2.urlopen(request).read()

    def set_scenestatus (self, switchid, status):
        xbmc.log ("START SETSCENESTATUS : ")
        update_domoticz = 0
        if status == 1:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchscene&idx=" + str(switchid) + "&switchcmd=On"
            update_domoticz = 1
        if status == 0:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchscene&idx=" + str(switchid) + "&switchcmd=Off"
            update_domoticz = 1

        if update_domoticz:
            request = urllib2.Request(self.url)
            request.add_header("Authorization", "Basic %s" % self.base64string)
            self.response = urllib2.urlopen(request).read()
            xbmc.log ("START SETSCENESTATUS: " + str(response))

open(os.path.join( __dataroot__, "text.txt" ), 'a').close()

ui = MainGUI("main_gui.xml",CWD,"Default")
ui.doModal()
del ui
