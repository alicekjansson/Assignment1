# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:27:54 2023

@author: Alice
"""

import sys
sys.path.append(r'C:/Users/Alice/OneDrive - Lund University/Dokument/Doktorand IEA/Kurser/KTH kurs/pandapower-develop')

import pandapower
import pandapower.networks
import pandapower.topology
import pandapower.plotting
import pandapower.converter
import pandapower.estimation

import xml.etree.ElementTree as ET

EQ=ET.parse('Assignment_EQ_reduced.xml') 
grid=EQ.getroot()