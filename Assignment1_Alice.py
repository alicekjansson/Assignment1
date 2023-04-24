# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:27:54 2023

@author: Alice
"""

import sys
sys.path.append(r'C:/Users/Alice/OneDrive - Lund University/Dokument/Doktorand IEA/Kurser/KTH kurs/pandapower-develop')

import pandapower as pp
import pandapower.networks
import pandapower.topology
import pandapower.plotting
import pandapower.converter
import pandapower.estimation

import xml.etree.ElementTree as ET

#Step 1: Parse XML files
EQ=ET.parse('Assignment_EQ_reduced.xml') 
grid=EQ.getroot()
SSH=ET.parse('Assignment_SSH_reduced.xml') 
loadflow=SSH.getroot()

#Step 2: Create internal datastructures


net=pp.create_empty_network()