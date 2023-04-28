# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:28:03 2023

@author: ielmartin
"""
import pandas as pd
import pandapower as pp
import xml.etree.ElementTree as ET


class GridNodeObjects:
    
    def __init__(self,eq,ssh,ns,element_type):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.grid=eq.getroot()
        self.ldf=ssh.getroot()
        self.df=pd.DataFrame()
        self.list=self.grid.findall('cim:'+element_type,ns)
        self.name = []
        self.connect = []
        
        
    def get_cim_connectivity(self):
        for item in self.list:
            self.name.append(item.find('cim:IdentifiedObject.name',ns).text)
            for terminal in self.grid.findall('cim:Terminal',ns):
                if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + item.attrib.get(ns['rdf']+'ID'):
                    self.connect.append(terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource'))
        
        self.df['name']=self.name
        self.df['connection']=self.connect
        
        
class Buses(GridNodeObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        
    def create_pp_buses(net, self):
        
        

class Loads(GridNodeObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "EnergyConsumer"):
        super().__init__(eq, ssh, ns, element_type)
        

    
class Generators(GridNodeObjects):
    
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
gens = Generators(eq,ssh,ns,"SynchronousMachine")


buses.get_cim_connectivity()
loads.get_cim_connectivity()
gens.get_cim_connectivity()


print(buses.name)
print(loads.name)
print(gens.name)

  
net = pp.create_empty_network() 



