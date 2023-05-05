# -*- coding: utf-8 -*-
"""
Created on Fri May  5 11:26:04 2023

@author: Alice
"""

#This is the main part of the code

import sys
sys.path.append(r'C:/Users/Alice/OneDrive - Lund University/Dokument/Doktorand IEA/Kurser/KTH kurs/pandapower-develop')
import pandapower as pp
from Classes2 import Buses,Lines,Transformers, Loads, Generators
import xml.etree.ElementTree as ET
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandapower.plotting as plot

#Step 1: Parse XML files (choose reduced or microgrid)
eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')
ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')
# eq = ET.parse('Assignment_EQ_reduced.xml')
# ssh = ET.parse('Assignment_SSH_reduced.xml')

#Define namespace
ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

#Create grid in Pandapower via our classes and plot
#Start with creating empty network
net = pp.create_empty_network()
#Create buses
buses = Buses(eq,ssh,ns)
buses.create_pp_bus(net)
#Create loads
loads = Loads(eq,ssh,ns)
loads.find_bus_connection(buses)
loads.create_pp_load(net)
#Create generators
gens = Generators(eq,ssh,ns)
gens.find_bus_connection(buses)
gens.create_pp_gen(net)
#Create lines
lines = Lines(eq,ssh,ns)
lines.create_pp_line(net)
#Create transformers
trans=Transformers(eq,ssh,ns)
trans.create_pp_trans(net,buses)
#Plot   
plot.simple_plot(net)