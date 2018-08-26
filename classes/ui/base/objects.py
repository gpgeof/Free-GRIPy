# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 20:43:24 2018

@author: Adriano
"""

import wx

import app
from app import log
from classes.base import GripyObject
from classes.om import ObjectManager
#from classes.ui import UIManager


class UIBaseObject(GripyObject):
    tid = None
    
    def __init__(self, **data):
        super().__init__(**data)
      
    def PostInit(self):
        """To be overrriden"""
        pass

    def PreDelete(self):
        """To be overrriden"""
        pass

    def _call_self_remove(self):
        try:
            if isinstance(self, UIControllerObject):
                uid = self.uid
            else:
                uid = self._controller_uid
            UIM_class = self._get_manager_class()
            UIM = UIM_class()   
            wx.CallAfter(UIM.remove, uid)

        except Exception as e:
            print ('ERROR: _call_self_remove ', e)


###############################################################################
###############################################################################
                                 

class UIControllerObject(UIBaseObject):
    """
    The base class for all Controller classes (MVC software architectural 
    pattern).
        
    """
    tid = None
    # TODO: verificar se vale a pena manter esses singletons
    _singleton = False
    _singleton_per_parent = False
       
    def __init__(self):
        super(UIControllerObject, self).__init__()  
        self.model = None  
        self.view = None 
  
    def __setitem__(self, key, value):
        """If Controller does not have key, redirects __setitem__ to model."""  
        try:
            super().__setitem__(key, value)
        except:
            try:
                self.model.__setitem__(key, value)
            except:
                raise Exception('ERROR in UIControllerObject.__setitem__({},'+\
                                +'{})'.format(key, value)
                )   
                
    def __setattr__(self, key, value):
        """If Controller does not have key, redirects __setattr__ to model."""   
        try:
            super().__setattr__(key, value)
        except:
            try:
                self.model.__setattr__(key, value)
            except:
                raise Exception('ERROR in UIControllerObject.__setattr__({},'+\
                                +'{})'.format(key, value)
                )    
        
    def _model_changed(self, old_value, new_value, 
                                                 topic=app.pubsub.AUTO_TOPIC):
        """Redirect model messages to the system as they were 
        controller messages.
        """    
        key = topic.getName().split('.')[2]
        topic = 'change.' + key
        self.send_message(topic, old_value=old_value, new_value=new_value)
 
    def _create_model_view(self, **base_state): 
        """Function to create model and view objects (MVC pattern)."""
        UIM_class = self._get_manager_class()
        UIM = UIM_class()         
        model_class, view_class = UIM.get_model_view_classes(self.tid)
        # First, create model object
        if model_class is not None:
            try:
                self.model = model_class(self.uid, **base_state)
                #
                for attr_name, attr_props in self.model._ATTRIBUTES.items():
                    self.model.subscribe(self._model_changed, 'change.' + attr_name)
                #
            except Exception as e:
                msg = 'ERROR on creating MVC model {} object: {}'.format(model_class.__name__, e)
                log.exception(msg)
                print ('\n', msg)
                raise
        else:
            self.model = None
        # Then, create view object   
        if view_class is not None:     
            try:
                self.view = view_class(self.uid)
            except Exception as e:
                msg = 'ERROR on creating MVC view {} object: {}'.format(view_class.__name__, e)
                log.exception(msg)
                print ('\n', msg, view_class, model_class.__dict__, '\n')
                raise e             
        else:
            self.view = None  
    
    def _PostInit(self):
        """Redirects post init call made by UIManager.create to model, 
        view and controller objects.
        """
        try:
            if self.model:
                self.model.PostInit()
        except Exception as e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.model.__class__.__name__, e)
            log.exception(msg)
            print ('\n', msg)
            raise
        try:    
            if self.view:        
                self.view.PostInit()
        except Exception as e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.view.__class__.__name__, e)
            log.exception(msg)
            print ('\n', msg)
            raise
        try:                
            self.PostInit()    
        except Exception as e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.__class__.__name__, e)
            log.exception(msg)
            print ('\n', msg)
            raise
        
   
    def attach(self, OM_objuid):
        """Attaches this object to a ObjectManager object.
        
        Example: 
            self.attach(('log', 1))
            OM.remove(('log', 1))     -> self will be removed by UIManager 
        """
        OM = ObjectManager()
        obj = OM.get(OM_objuid)
        try:
            # TODO: REVER ISSO
            obj.subscribe(self._call_self_remove, 'remove')
        except:
            pass
           
    def detach(self, OM_objuid):
        """Detach a object vinculated to a ObjectManager object 
        by attach function.
        """
        OM = ObjectManager()
        obj = OM.get(OM_objuid)
        try:
            # TODO: REVER ISSO
            obj.unsubscribe(self._call_self_remove, 'remove')        
        except:
            pass
        
        
    def get_state(self):
        """Returns MVC triad state.
        
        In general, object states are used add persistence to a object or to
        make an object clone.
        """
        if not self.model:
            return None 
        return self.model._getstate()
        """
        UIM = UIManager()
        children = UIM.list(parentuidfilter=self.uid)
        if children:
            state['children'] = []
            for child in children:
                state['children'].append(child.get_state())
        return self.tid, state
        """
    
    """  
    # TODO: ver se deve-se manter o tid na chamada abaixo (@staticmethod)
    @staticmethod    
    def load_state(state, tid, parentuid=None):
        children = state.pop('children', None)
        UIM = UIManager()
        obj = UIM.create(tid, parentuid, **state)
        if children:
            for child_tid, child_state in children:
                UIControllerObject.load_state(child_state, child_tid, obj.uid)
        return obj
    """
    

class UIModelObject(UIBaseObject):
    """
    The base class for all Model classes (MVC software architectural pattern).
        
    """
    tid = None
    _IMMUTABLES_KEYS = ['_controller_uid']

    def __init__(self, controller_uid, **state):
        UIM_class = self._get_manager_class()
        UIM = UIM_class()   
        try:
            super().__init__(**state)
            self._controller_uid = controller_uid
            # We are considering that only Controller class objects 
            # can create Model class objects. Then, we must verify it

            model_class = UIM.get_model_view_classes(controller_uid[0])[0]
            if self.__class__ != model_class:
                msg = 'Error! Only the controller can create the model.'
                raise Exception(msg)                  
        except:
            try:
                UIM.remove(self._controller_uid)
            except:
                pass
            raise 


class UIViewObject(UIBaseObject):
    """
    The base class for all View classes (MVC software architectural pattern).
        
    """
    tid = None
    _IMMUTABLES_KEYS = ['_controller_uid']
    
    def __init__(self, controller_uid):
        super().__init__()
        self._controller_uid = controller_uid        
        # We are considering that only Controller class objects 
        # can create View class objects. Then, we must verify it      
        UIM_class = self._get_manager_class()
        UIM = UIM_class()
        view_class = UIM.get_model_view_classes(controller_uid[0])[1]
        if self.__class__ != view_class:
            msg = 'Error! Only the controller can create the view.'
            log.exception(msg)
            raise Exception(msg)       

