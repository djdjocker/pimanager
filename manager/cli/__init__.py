# -*- coding: utf-8 -*-
import logging
import sys
import os

import manager
from server import Server

def main():
    args = sys.argv[1:]
    
    Server().run(args)