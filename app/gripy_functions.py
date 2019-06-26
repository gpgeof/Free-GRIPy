# -*- coding: utf-8 -*-

from app.gripy_function_manager import FunctionManager
from basic.temp.func import do_STFT, do_CWT

from classes.om import Log
from classes.ui import DataMaskController
#from datatypes.DataTypes import Log


"""
#FunctionManager.register_function(ab, 'Soma Normal', A, B, a=A)
#@classmethod
#def register_function(cls, func, friendly_name=None,  *args, **kwargs):
"""


def register_app_functions():
    FunctionManager.register_function(do_STFT, 
                                      "Fourier Transform", 
                                      Log, 
                                      data_mask=DataMaskController
    )
    FunctionManager.register_function(do_CWT, 
                                      "Wavelet Transform", 
                                      Log, 
                                      data_mask=DataMaskController
    )

