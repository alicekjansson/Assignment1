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
# eq=ET.parse('Assignment_EQ_reduced.xml') 
# ssh=ET.parse('Assignment_SSH_reduced.xml') 
eq=ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml') 
ssh=ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml') 
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
    from_bus = pp.get_element_index(net, "bus", cimtrf['HVNode'])
    to_bus = pp.get_element_index(net, "bus", cimtrf['LVNode'])
    pp.create_transformer(net,from_bus,to_bus,"25 MVA 110/20 kV",cimtrf['Name']) 
for i, cimline in df_lines.transpose().items():
    from_bus = pp.get_element_index(net, "bus", cimline['Node1'])
    to_bus = pp.get_element_index(net, "bus", cimline['Node2'])
    pp.create_line(net,from_bus,to_bus,cimline['Length'],'NAYY 4x50 SE',cimline['Name'])
   
   