# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:27:54 2023

@author: Alice
"""

import sys
sys.path.append(r'C:/Users/Alice/OneDrive - Lund University/Dokument/Doktorand IEA/Kurser/KTH kurs/pandapower-develop')

import pandapower as pp
from Classes1 import Buses,Lines,Transformers
import xml.etree.ElementTree as ET
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#Step 1: Parse XML files
eq=ET.parse('Assignment_EQ_reduced.xml') 
ssh=ET.parse('Assignment_SSH_reduced.xml') 
ns=ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

#Step 2: Create internal datastructures
df_buses=Buses(eq,ssh,ns).get_df()
df_trans=Transformers(eq,ssh,ns).get_df()
df_lines=Lines(eq,ssh,ns).get_df()


#Step 3: Create pandapower objects
net=pp.create_empty_network()
for i,cimbus in df_buses.transpose().items():
    pp.create_bus(net,vn_kv=cimbus['VoltageLevel'],name=cimbus['Name'])
for i,cimtrf in df_trans.transpose().items():
    from_bus = pp.get_element_index(net, "bus", cimtrf['HVTerminal'])
    to_bus = pp.get_element_index(net, "bus", cimtrf['LVTerminal'])
    name=cimtrf['Name']
    std_type="25 MVA 110/20 kV"
    pp.create_transformer(net,from_bus,to_bus,name,std_type) 
    
    # pp.create_transformer(net,hv_bus=cimtrf['HVTerminal'],lv_bus=cimtrf['LVTerminal'],name=cimtrf['Name'],std_type="25 MVA 110/20 kV")  

#OBS how to choose standard type??
# for i,cimline in df_lines.transpose().items():
#     pp.create_line(net, cimline['Terminal1'], cimline['Terminal2'], float(cimline['Length']) ,std_type='184-AL1/30-ST1A 20.0', name=cimline['Name'])