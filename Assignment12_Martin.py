# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:16:34 2023

@author: ielmartin
"""
# -*- coding: utf-8 -*-

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
            
        
        
    def find_bus_connection(self, buses):
        
        bus_name_list = []
        for item in self.df['connection']: 
            bus_row = buses.df.loc[buses.df['connection'] == item]
            if bus_row.empty is False:
                bus_name_list.append(bus_row['name'].values[0])
            else:
                bus_name_list.append(False)
        self.df['bus_connection'] = bus_name_list
            
        
class Buses(GridNodeObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        
    def get_connectivity(self):
        for item in self.list:
            bus_name = item.find('cim:IdentifiedObject.name',ns).text
            self.name.append(bus_name)
            for connectivity_node in self.grid.findall('cim:ConnectivityNode',ns):
                node_name = connectivity_node.find('cim:IdentifiedObject.name',ns).text
                if node_name == bus_name:
                    self.connect.append(connectivity_node.find('cim:ConnectivityNode.ConnectivityNodeContainer',ns).attrib.get(ns['rdf']+'resource'))
        self.df['name']=self.name
        self.df['node_container']=self.connect
        
    def get_cim_data(self):
        self.voltage_lvl = []
        
        for item in self.list:
            container= item.find('cim:Equipment.EquipmentContainer',ns)
            for vl in self.grid.findall('cim:VoltageLevel',ns):
                if container.attrib.get(ns['rdf']+'resource') == "#" + vl.attrib.get(ns['rdf']+'ID'):
                    self.voltage_lvl.append(vl.find('cim:IdentifiedObject.name',ns).text)
        
        self.df['voltage'] = self.voltage_lvl
        

    def create_pp_bus(self, net):
        for bus_name, bus_voltage in zip(self.df['name'], self.df['voltage']):  
            pp.create_bus(net, name=bus_name,vn_kv=bus_voltage)
                               
        #self.df.apply(lambda row: pp.create_bus(net, name=row['name'],vn_kv=row['voltage']),axis=1)


class Loads(GridNodeObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "EnergyConsumer"):
        super().__init__(eq, ssh, ns, element_type)
        
    #def create_pp_load(self, net):
        
    
class Generators(GridNodeObjects):
    
    def __init__(self,eq,ssh,ns, element_type = "SynchronousMachine"):
        super().__init__(eq, ssh, ns, element_type)
        
             

#eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')
#ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')
eq = ET.parse('Assignment_EQ_reduced.xml')
ssh = ET.parse('Assignment_SSH_reduced.xml')


ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

buses = Buses(eq,ssh,ns)
loads = Loads(eq,ssh,ns)
gens = Generators(eq,ssh,ns)

buses.get_connectivity()


#loads.find_bus_connection(buses)
#gens.find_bus_connection(buses)

buses.get_cim_data()



#print(loads.name)
#print(gens.name)

  
net = pp.create_empty_network()


buses.create_pp_bus(net)
print(net.bus) 
print(buses.df)
print(loads.df)
print(gens.df)


