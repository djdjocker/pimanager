# -*- coding: utf-8 -*-
import sys

from gui import GUI

gui = None

def start():
    global gui
    gui = GUI()
    gui.start()
    