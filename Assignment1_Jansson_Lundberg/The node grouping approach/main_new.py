# -*- coding: utf-8 -*-
"""
Created on Sun May  7 13:42:56 2023
@author: ielmartin
"""

# Main script includes cim-xml parsing, creation of grid object class instances and corresponding panda power objects in order to plot the network
import pandas as pd
import pandapower as pp
import pandapower.plotting as plot
import xml.etree.ElementTree as ET

# import grid object classes
from Classes_new import Terminals, Buses, Lines,Transformers, Loads, Generators

# comment out cim-data that is not to be parsed
eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')
ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')
eq = ET.parse('Assignment_EQ_reduced.xml')
ssh = ET.parse('Assignment_SSH_reduced.xml')
eq = ET.parse('MicroGridTestConfiguration_T1_BE_EQ_V2-3.xml')         #Second version microgrid
ssh = ET.parse('MicroGridTestConfiguration_T1_BE_SSH_V2.xml')       #Second version microgrid


ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

# create instances of grid object classes using cim data 
terminals = Terminals(eq,ssh,ns)
buses = Buses(eq,ssh,ns)
loads = Loads(eq,ssh,ns)
gens = Generators(eq,ssh,ns)
lines = Lines(eq,ssh,ns)
trafos = Transformers(eq,ssh,ns)

# Determine terminals of each grid object 
terminals.get_connectivity_nodes()
buses.find_terminals(terminals)
loads.find_terminals(terminals)
gens.find_terminals(terminals)
lines.find_terminals(terminals)
trafos.find_terminals(terminals)

# generate pandapower network including finding grid object connections
net = pp.create_empty_network()
buses.create_pp_bus(net)
loads.create_pp_load(net, terminals, buses)
gens.create_pp_gen(net, terminals, buses)
lines.create_pp_line(net, terminals, buses)
trafos.create_pp_trans(net, terminals, buses)

# plot the pandapower network
plot.simple_plot(net, bus_size=1.0, plot_loads=True, plot_gens=True)







