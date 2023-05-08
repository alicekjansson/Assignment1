# -*- coding: utf-8 -*-
"""
Created on Mon May  8 08:16:03 2023

@author: ielmartin
"""
import pandas as pd
import pandapower as pp

ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

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
        self.node3 = []
        self.trafo3 = 'no'
        if element_type != "node_group":
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
                                node1 = node.find('cim:ConnectivityNode.ConnectivityNodeContainer',ns).attrib.get(ns['rdf']+'resource')
                                self.node1.append(node1)
                                n+=1
                                break
                    if n == 1:        
                        node_id = terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource')
                        for node in self.grid.findall('cim:ConnectivityNode',ns):
                            if "#" + node.attrib.get(ns['rdf']+'ID') == node_id:
                                node2 = node.find('cim:ConnectivityNode.ConnectivityNodeContainer',ns).attrib.get(ns['rdf']+'resource')
                                if node2 != node1:
                                    self.node2.append(node2)
                                    n+=1
                                    break
                    else:
                        node_id = terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource')
                        for node in self.grid.findall('cim:ConnectivityNode',ns):
                            if "#" + node.attrib.get(ns['rdf']+'ID') == node_id:
                                node3 = node.find('cim:ConnectivityNode.ConnectivityNodeContainer',ns).attrib.get(ns['rdf']+'resource')
                                if node3 != node1 and node3 != node2:
                                    self.node3.append(node3)
                                    self.trafo3 =item.find('cim:IdentifiedObject.name',ns).text 
                                    n+=1
                                    break
                        
            if n == 1:
                self.node2.append(False)
                self.node3.append(False)
            
            if n == 2:
                self.node3.append(False)
                

        
        self.df['node1']=self.node1
        self.df['node2']=self.node2
        self.df['node3']=self.node3
        
    def find_bus_connection(self, buses, node_no = 'node1'):
        
        bus_name_list = []
        for idx, node in zip(self.df.index,self.df[node_no]): 
            bus_row = buses.df.loc[buses.df['node1'] == node]
            if bus_row.empty is False:
                bus_name_list.append(bus_row['name'].values[0])
            else:
                if node_no != "node3" or (node_no == "node3" and self.trafo3 == "yes"):
                    bus_name_list.append(self.add_missing_bus(buses, idx, node_no))
                else:
                    bus_name_list.append(False)
                             
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
    
    def __init__(self, eq, ssh, ns, element_type = "node_group"):
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
            for trans_name, bus1_name, bus2_name, bus3_name in zip(self.df['name'],self.df['node1_bus'], self.df['node2_bus'], self.df['node3_bus']):
                if  bus3_name != False:
                    std_type= '63/25/38 MVA 110/20/10 kV'
                    bus1 = pp.get_element_index(net, "bus", bus1_name)
                    bus2 = pp.get_element_index(net, "bus", bus2_name)
                    bus3 = pp.get_element_index(net, "bus", bus3_name)
                    pp.create_transformer3w(net, bus1, bus2, bus3, std_type, name =trans_name)
                
                else:
                    std_type='25 MVA 110/20 kV'
                    bus1 = pp.get_element_index(net, "bus", bus1_name)
                    bus2 = pp.get_element_index(net, "bus", bus2_name)
                    pp.create_transformer(net, bus1, bus2, std_type, name =trans_name)