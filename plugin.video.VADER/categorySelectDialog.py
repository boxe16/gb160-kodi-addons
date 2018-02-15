# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html
# This is an XBMC addon for demonstrating the capabilities
# and usage of PyXBMCt framework.

import os
import xbmc
import xbmcaddon
import pyxbmct
from lib import utils
import plugintools

from itertools import tee, islice, chain, izip

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')

# Enable or disable Estuary-based design explicitly
# pyxbmct.skin.estuary = True



def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)

class categorySelectDialog(pyxbmct.AddonDialogWindow):

    def __init__(self, title='', categories=None):
        super(categorySelectDialog, self).__init__(title)
        self.categories = categories
        self.listOfRadioButtons = []
        self.radioMap = {}
        maxRows = len(categories)
        self.setGeometry(400, 600, maxRows+1, 1)
        self.set_active_controls()
        self.set_navigation()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)



    def set_active_controls(self):
        row = 0

        for category in self.categories:
            for catId in category:
                catName = category[catId]

                radiobutton = pyxbmct.RadioButton(catName)
                catSetting = plugintools.get_setting(catName)
                self.placeControl(radiobutton, row, 0)
                self.connect(radiobutton, self.radio_update)

                if catSetting == True:
                    radiobutton.setSelected(True)
                else:
                    radiobutton.setSelected(False)


                self.listOfRadioButtons.append(radiobutton)
                self.radioMap[catName] = radiobutton





                row = row  + 1

        self.close_button = pyxbmct.Button('Close')
        self.placeControl(self.close_button, row, 0)
        self.connect(self.close_button, self.close)


    from itertools import tee, islice, chain, izip


    def set_navigation(self):

        for previous, item, nextItem in previous_and_next(self.listOfRadioButtons):

            if previous != None:
                item.controlUp(previous)
            if nextItem != None:
                item.controlDown(nextItem)
            if nextItem == None:
                item.controlDown(self.close_button)
                self.close_button.controlUp(item)



                # length = len(self.listOfRadioButtons)
            # obj = self.listOfRadioButtons[length-1]
            # item.controlDown(self.close_button)


        self.setFocus(self.listOfRadioButtons[0])



    def radio_update(self):
        # Update radiobutton caption on toggle
        # utils.log('entered radio update ' + str(listPos))
        # radioButton = self.listOfRadioButtons[listPos]
        radioButton = self.getFocus()
        for catName, radioButtonItem in self.radioMap.iteritems():
            if radioButton == radioButtonItem:
                label = catName


        if radioButton.isSelected():
            plugintools.set_setting(label, 'True')
        else:
            plugintools.set_setting(label, 'False')

