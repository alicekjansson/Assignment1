# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:28:03 2023

@author: ielmartin
"""
import pandas as pd
import pandapower as pp
import xml.etree.ElementTree as ET


class GridObjects:
    
    def __init__(self,eq,ssh,ns,element_type):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.grid=eq.getroot()
        self.ldf=ssh.getroot()
        self.df=pd.DataFrame()
        self.list=self.grid.findall('cim:'+element_type,ns)
        self.df['ID']=[element.attrib.get(ns['rdf']+'ID') for element in self.list]
        
        
class Buses(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        
 
        
class Loads(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "EnergyConsumer"):
        super().__init__(eq, ssh, ns, element_type)
        
    
    def get_cim_data(self, buses):
        
        for load in self.list:

        
        
    
        # required data: bus connection, 
        
    
    
class Generators(GridObjects):
    
    def __init__(self,eq,ssh,ns, element_type = "GeneratingUnit"):
        super().__init__(eq, ssh, ns, element_type)
        
        

eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')
ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')

ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

buses = Buses(eq,ssh,ns)
  
loads = Loads(eq,ssh,ns)
loads.get_cim_data(buses)

print(test_buses.df)
print(net.bus)

test_gen = Generators(eq,ssh,ns,"GeneratingUnit")
test_gen2 = Generators(eq,ssh,ns, "ThermalGeneratingUnit")
print(test_gen.df)
print(test_gen2.df)