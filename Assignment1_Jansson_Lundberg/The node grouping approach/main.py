# -*- coding: utf-8 -*-
"""
Created on Sun May  7 13:42:56 2023

@author: ielmartin
"""

import pandas as pd
import pandapower as pp
import pandapower.plotting as plot
import xml.etree.ElementTree as ET

from Classes import Buses, Lines,Transformers, Loads, Generators


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



buses = Buses(eq,ssh,ns)
buses.get_cim_data()


loads = Loads(eq,ssh,ns)
loads.get_cim_connectivity()
loads.find_bus_connection(buses)


gens = Generators(eq,ssh,ns)
gens.get_cim_connectivity()
gens.find_bus_connection(buses)


lines = Lines(eq,ssh,ns)
lines.get_cim_connectivity()
lines.find_bus_connection(buses)
lines.find_bus_connection(buses,'node2')

trafos = Transformers(eq,ssh,ns)
trafos.get_cim_connectivity()
trafos.find_bus_connection(buses)
trafos.find_bus_connection(buses,'node2')

trafos.find_bus_connection(buses,'node3')
print(trafos.df)
print(lines.df)
print(buses.df)


net = pp.create_empty_network()

buses.create_pp_bus(net)
loads.create_pp_load(net)
gens.create_pp_gen(net)
lines.create_pp_line(net)
trafos.create_pp_trans(net)

plot.simple_plot(net)




