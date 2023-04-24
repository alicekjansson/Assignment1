# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:28:03 2023

@author: ielmartin
"""
import pandapower as pp

import xml.etree.ElementTree as ET

eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')
ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')

ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

