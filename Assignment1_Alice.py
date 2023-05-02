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
df_transformers=Transformers(eq,ssh,ns).get_df()
df_lines=Lines(eq,ssh,ns).get_df()

#Step 3: Create pandapower objects
net=pp.create_empty_network()
bus_id=[]
for i,cimbus in df_buses.transpose().items():
    bus=pp.create_bus(net,vn_kv=cimbus['VoltageLevel'],name=cimbus['Name'])