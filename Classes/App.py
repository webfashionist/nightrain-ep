__author__ = 'naetech'

import wx


class App(wx.App):

    def __init__(self):
        self.locale = ''
        wx.App.__init__(self)

    def OnPreInit(self):
        self.ResetLocale()
        self.locale = wx.Locale(wx.LANGUAGE_GERMAN)
        return True

    def OnInit(self):
        self.ResetLocale()
        self.locale = wx.Locale(wx.LANGUAGE_GERMAN)
        return True
