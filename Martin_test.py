# -*- coding: utf-8 -*-
"""
Created on Sun May  7 13:42:56 2023

@author: ielmartin
"""

import pandas as pd
import pandapower as pp
import pandapower.plotting as plot
import xml.etree.ElementTree as ET


class GridObjects:
    
    def __init__(self,eq,ssh,ns,element_type):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.grid=eq.getroot()
        self.ldf=ssh.getroot()
        self.df=pd.DataFrame()
        self.node1 = []
        self.node2 = []
        if element_type != "BusbarSection":
            self.list=self.grid.findall('cim:'+element_type,ns)
            self.df['ID']=[element.attrib.get(ns['rdf']+'ID') for element in self.list]
            self.df['name']=[element.find('cim:IdentifiedObject.name',ns).text for element in self.list]        
        
    def get_cim_connectivity(self):
        for item in self.list:
            n=0
            for terminal in self.grid.findall('cim:Terminal',ns):
                if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + item.attrib.get(ns['rdf']+'ID'):
                    if n == 0:
                        node_id = terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource')
                        for node in self.grid.findall('cim:ConnectivityNode',ns):
                            if "#"+node.attrib.get(ns['rdf']+'ID') == node_id:
                                self.node1.append(node.find('cim:ConnectivityNode.ConnectivityNodeContainer',ns).attrib.get(ns['rdf']+'resource'))
                                n+=1
                                break
                    else:        
                        node_id = terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource')
                        for node in self.grid.findall('cim:ConnectivityNode',ns):
                            if "#" + node.attrib.get(ns['rdf']+'ID') == node_id:
                                self.node2.append(node.find('cim:ConnectivityNode.ConnectivityNodeContainer',ns).attrib.get(ns['rdf']+'resource'))
                                n+=1
                                break
            if n == 1:
                self.node2.append(False)
        
        self.df['node1']=self.node1
        self.df['node2']=self.node2
        
    def find_bus_connection(self, buses, node_no = 'node1'):
        
        bus_name_list = []
        for idx, node in zip(self.df.index,self.df[node_no]): 
            bus_row = buses.df.loc[buses.df['node1'] == node]
            if bus_row.empty is False:
                bus_name_list.append(bus_row['name'].values[0])
            else:
                bus_name_list.append(self.add_missing_bus(buses, idx, node_no))
                             
        self.df[node_no+'_bus'] = bus_name_list
        
    def add_missing_bus(self, buses, idx, node_no):
        
        if self.df.at[idx, node_no] == False:
            self.df.at[idx, node_no] = 'new_bus_' + self.df.at[idx, 'name']
            ID = 'new_id_' + self.df.at[idx, 'name']
            name = self.df.at[idx, node_no]
            node1 = 'new_node_' + self.df.at[idx, 'name']
            node2 = False
            voltage = 110
            new_row = [ID, name, node1, node2, voltage]
            buses.df.loc[len(buses.df)] = new_row
        
        return name 
        
class Buses(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        
        
        for node in self.grid.findall('cim:ConnectivityNode',ns):
                self.node1.append(node.find('cim:ConnectivityNode.ConnectivityNodeContainer',ns).attrib.get(ns['rdf']+'resource'))
        self.node1 = list(dict.fromkeys(self.node1))
        node_name_list = []
        n=1
        for bus in self.node1: 
            self.node2.append(False)
            node_name_list.append('Bus_'+ str(n))
            n+=1
        self.df['ID']=self.node1
        self.df['name']= node_name_list
        self.df['node1']=self.node1
        self.df['node2']=self.node2         
        
    def get_cim_data(self):
        voltage_lvl = []  
        for vl in self.grid.findall('cim:VoltageLevel',ns):
            if "#" + vl.attrib.get(ns['rdf']+'ID') in self.node1:
                voltage_lvl.append(vl.find('cim:IdentifiedObject.name',ns).text)
        
        self.df['voltage'] = voltage_lvl
        
    def create_pp_bus(self, net):
        for bus_name, bus_voltage in zip(self.df['name'], self.df['voltage']):  
            pp.create_bus(net, name=bus_name,vn_kv=bus_voltage)
                               

class Loads(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "EnergyConsumer"):
        super().__init__(eq, ssh, ns, element_type)
        
        load_power = []
        for load_id in self.df['ID']:   
            for element in self.ldf.findall('cim:'+element_type,ns):
                if '#' + load_id  == element.attrib.get(ns['rdf']+'about'):
                    load_power.append(element.find('cim:EnergyConsumer.p',ns).text)
        self.df['p']=load_power
        
        
    def create_pp_load(self, net):
        for load_name, bus_name, active_power in zip(self.df['name'],self.df['node1_bus'], self.df['p']):
            if bus_name != False:
                bus = pp.get_element_index(net, "bus", bus_name)
                pp.create_load(net, bus, active_power, name =load_name)
          
class Generators(GridObjects):
    
    def __init__(self,eq,ssh,ns, element_type = "SynchronousMachine"):
        super().__init__(eq, ssh, ns, element_type)
        
        gen_power = []
        for gen_id in self.df['ID']:   
            for element in self.ldf.findall('cim:'+element_type,ns):
                if '#' + gen_id  == element.attrib.get(ns['rdf']+'about'):
                    gen_power.append(element.find('cim:RotatingMachine.p',ns).text)
        self.df['p']=gen_power
        
        
    def create_pp_gen(self, net):
        for gen_name, bus_name, active_power in zip(self.df['name'],self.df['node1_bus'], self.df['p']):
            if bus_name != False:
                bus = pp.get_element_index(net, "bus", bus_name)
                pp.create_gen(net, bus, active_power, name =gen_name)
        
class Lines(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "ACLineSegment"):
        super().__init__(eq, ssh, ns, element_type)
        
        length=[]
        for line in self.list:
            l=line.find('cim:Conductor.length',ns).text
            length.append(l)
        self.df['length']=length

    def create_pp_line(self, net):
        for line_name, bus1_name, bus2_name, line_length in zip(self.df['name'],self.df['node1_bus'], self.df['node2_bus'], self.df['length']):
            if bus1_name != False and bus2_name != False:
                std_type="N2XS(FL)2Y 1x300 RM/35 64/110 kV"
                bus1 = pp.get_element_index(net, "bus", bus1_name)
                bus2 = pp.get_element_index(net, "bus", bus2_name)
                pp.create_line(net, bus1, bus2, line_length, std_type, name =line_name)    

class Transformers(GridObjects):

    def __init__(self, eq, ssh, ns, element_type = "PowerTransformer"):
        super().__init__(eq, ssh, ns, element_type)


    def create_pp_trans(self, net):
        for trans_name, bus1_name, bus2_name in zip(self.df['name'],self.df['node1_bus'], self.df['node2_bus']):
            if bus1_name != False and bus2_name != False:
                std_type='25 MVA 110/20 kV'
                bus1 = pp.get_element_index(net, "bus", bus1_name)
                bus2 = pp.get_element_index(net, "bus", bus2_name)
                pp.create_transformer(net, bus1, bus2, std_type, name =trans_name)

eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')
ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')
#eq = ET.parse('Assignment_EQ_reduced.xml')
#ssh = ET.parse('Assignment_SSH_reduced.xml')


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


net = pp.create_empty_network()

buses.create_pp_bus(net)
loads.create_pp_load(net)
gens.create_pp_gen(net)
lines.create_pp_line(net)
trafos.create_pp_trans(net)

plot.simple_plot(net)




