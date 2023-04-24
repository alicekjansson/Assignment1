# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:09:05 2023

@author: Alice
"""

import xml.etree.ElementTree as ET
#Step 1: Parse XML files
EQ=ET.parse('Assignment_EQ_reduced.xml') 
grid=EQ.getroot()
SSH=ET.parse('Assignment_SSH_reduced.xml') 
loadflow=SSH.getroot()

class Buses:
    
    def __init__(self):
        return
    
class Transformers:
    
    def __init__(self):
        return

class Lines:
    
    def __init__(self):
        return
    
class Shunts:
    
    def __init__(self):
        return
    
