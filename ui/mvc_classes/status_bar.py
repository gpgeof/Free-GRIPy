# -*- coding: utf-8 -*-

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIModelObject 
from classes.ui import UIViewObject 
from app import log
 
     
class StatusBarController(UIControllerObject):
    tid = 'statusbar_controller'
    _singleton_per_parent = True
    
    def __init__(self):
        super(StatusBarController, self).__init__()
        
        
class StatusBarModel(UIModelObject):
    tid = 'statusbar_model'

    # TODO: Corrigir atributo abaixo
    _ATTRIBUTES = {
        'label': {'default_value': wx.EmptyString, 
                  'type': str}
    }    
    
    def __init__(self, controller_uid, **base_state):
        super(StatusBarModel, self).__init__(controller_uid, **base_state)  


class StatusBar(UIViewObject, wx.StatusBar):
    tid = 'statusbar'
 
    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        _UIM = UIManager()
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        wx.StatusBar.__init__(self, parent_controller.view)
        parent_controller.view.SetStatusBar(self)

    def PostInit(self):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        self.SetStatusText(controller.model.label)
        
        
        