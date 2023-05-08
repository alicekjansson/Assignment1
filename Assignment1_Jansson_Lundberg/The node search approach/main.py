# -*- coding: utf-8 -*-
"""
Created on Sun May  7 10:51:25 2023

@author: ielmartin
"""

#This is the main part of the code

#import pandapower (including plotting tool), elementtree for xml parsing &... 
# custom grid object classes for CIM to pandapower conversion 
import pandapower as pp
import pandapower.plotting as plot
import xml.etree.ElementTree as ET
from GridClasses import Buses, Lines,Transformers, Loads, Generators

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#Step 1: Parse XML files (choose reduced or microgrid)
# eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')         #First version microgrid
# ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')       #First version microgrid
eq = ET.parse('MicroGridTestConfiguration_T1_BE_EQ_V2-3.xml')         #Second version microgrid
ssh = ET.parse('MicroGridTestConfiguration_T1_BE_SSH_V2.xml')       #Second version microgrid
#eq = ET.parse('Assignment_EQ_reduced.xml')                         #Reduced network
#ssh = ET.parse('Assignment_SSH_reduced.xml')                       #Reduced network

#Define namespace
ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

#Create grid in Pandapower from parsed CIM data via our classes, then plot resultning network

#Start with creating empty network
net = pp.create_empty_network()
#Create buses
buses = Buses(eq,ssh,ns)
buses.create_pp_bus(net)
#Create loads
loads = Loads(eq,ssh,ns)
#loads.find_bus_connection(buses)
loads.create_pp_load(net, buses)
#Create generators
gens = Generators(eq,ssh,ns)
#gens.find_bus_connection(buses)
gens.create_pp_gen(net, buses)
#Create lines
lines = Lines(eq,ssh,ns)
lines.create_pp_line(net)
#Create transformers
trans=Transformers(eq,ssh,ns)
trans.create_pp_trans(net,buses)
#Plot  
plot.simple_plot(net)