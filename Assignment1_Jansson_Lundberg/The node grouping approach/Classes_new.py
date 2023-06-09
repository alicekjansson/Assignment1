# -*- coding: utf-8 -*-
"""
Created on Mon May  8 08:16:03 2023

@author: ielmartin
"""
import pandas as pd
import pandapower as pp
from functions_new import get_component_connection, find_bus, add_missing_node

ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

# superclass of all grid objects
class GridObjects:
    
    def __init__(self,eq,ssh,ns,element_type):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.grid=eq.getroot()
        self.grid_data=ssh.getroot()
        self.df=pd.DataFrame()
        self.node1 = []
        self.node2 = []
        self.node3 = []
        self.e_type = element_type
        
        self.list=self.grid.findall('cim:'+element_type,ns)
        self.df['ID']=[element.attrib.get(ns['rdf']+'ID') for element in self.list]
        self.df['name']=[element.find('cim:IdentifiedObject.name',ns).text for element in self.list]
        
    # calls function in new_function.py to find the terminals for each grid object 
    def find_terminals(self, terminals):
        get_component_connection(self, terminals)
            

# this class is used to extract terminals and corresponding connectivity nodes from cim data. If CN a missing from cim data, a new one is associated to the terminal
class Terminals(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "Terminal"):
        super().__init__(eq, ssh, ns, element_type)
        
    # find which connectivity node each terminal connects (or doesn't connect) to
    def get_connectivity_nodes(self):
        
        # locate terminals from ssh file
        ssh_terminals = self.grid_data.findall('cim:'+"Terminal",ns)
        
        # Collect info on terminal connection status in dictionary
        self.terminal_connect= {}
        for terminal in ssh_terminals:
            terminal_id = terminal.attrib.get(ns['rdf']+'about')
            connection_check = terminal.find('cim:ACDCTerminal.connected',ns).text
            self.terminal_connect[terminal_id] = connection_check

        
        # Get connectivity node  of all connected terminals
        for terminal in self.list: # for all terminals in eq file
             terminal_id = '#' + terminal.attrib.get(ns['rdf']+'ID')
             if terminal_id in self.terminal_connect: # if terminal from eq file in ssh file
                 node_id = terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource') # get terminal connectivity node
                 # if terminal is connected
                 if self.terminal_connect[terminal_id] == 'true':
                     # find corresponding connectivity node from eq file
                     for node in self.grid.findall('cim:ConnectivityNode',ns):
                         if "#"+node.attrib.get(ns['rdf']+'ID') == node_id:
                            self.terminal_connect[terminal_id] = node_id # replace "true" with CN id                          
                            break
                
                # if no corresponding connectivity node found in eq file, add one to the dictionary anyway 
                 if self.terminal_connect[terminal_id] == 'true':
                     self.terminal_connect[terminal_id] = node_id # replace "true" with CN id                                                        
        
class Buses(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        
        # Adjust list/dataframe so only busbars and no breaker nodes are included
        new_list = []
        for item in self.list:
            if 'Busbar' in item.find('cim:IdentifiedObject.name',ns).text:
                new_list.append(item)
        self.list = new_list
        self.df = self.df[self.df['name'].str.contains('Busbar')]
        
        # Get voltage levels for busbars from cim data to use in pandapower
        voltage_lvl = []
        for element in self.grid.findall('cim:'+element_type,ns):
            equip_container = element.find('cim:Equipment.EquipmentContainer',ns).attrib.get(ns['rdf']+'resource')
            if element.find('cim:IdentifiedObject.name',ns).text in self.df['name'].values:
                for vl in self.grid.findall('cim:VoltageLevel',ns):
                    if "#" + vl.attrib.get(ns['rdf']+'ID') == equip_container:
                        voltage_lvl.append(vl.find('cim:IdentifiedObject.name',ns).text)
            
        self.df['voltage'] = voltage_lvl
        
    # create pandapower objects
    def create_pp_bus(self, net):
        for bus_name, bus_voltage in zip(self.df['name'], self.df['voltage']):
            if bus_name not in net.bus['name'].values:
                pp.create_bus(net, name=bus_name,vn_kv=bus_voltage, type='b')                             

class Loads(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "EnergyConsumer"):
        super().__init__(eq, ssh, ns, element_type)
        
        load_power = []
        for load_id in self.df['ID']:   
            for element in self.grid_data.findall('cim:'+element_type,ns):
                if '#' + load_id  == element.attrib.get(ns['rdf']+'about'):
                    load_power.append(element.find('cim:EnergyConsumer.p',ns).text)
        self.df['p']=load_power       
        
    def create_pp_load(self, net, terminals, buses):
        for load_name, terminal_id, active_power in zip(self.df['name'], self.df['node1'], self.df['p']):
            if terminal_id != False and terminal_id != 'disconnected':
                #get name for bus connected to load
                bus_name = find_bus(self, net, terminals, buses, terminal_id)
                # if no bus found
                if bus_name == terminal_id:
                    # create new bus with connectivity node id as name
                    bus_name = terminals.terminal_connect[terminal_id]
                    add_missing_node(self, net, bus_name)
                # create loads in pandapower
                bus = pp.get_element_index(net, "bus", bus_name)
                pp.create_load(net, bus, active_power, name =load_name)
                           
          
class Generators(GridObjects):
    
    def __init__(self,eq,ssh,ns, element_type = "SynchronousMachine"):
        super().__init__(eq, ssh, ns, element_type)
        
        gen_power = []
        for gen_id in self.df['ID']:   
            for element in self.grid_data.findall('cim:'+element_type,ns):
                if '#' + gen_id  == element.attrib.get(ns['rdf']+'about'):
                    gen_power.append(element.find('cim:RotatingMachine.p',ns).text)
        self.df['p']=gen_power
        
        
    def create_pp_gen(self, net, terminals, buses):
        for gen_name, terminal_id, active_power in zip(self.df['name'],self.df['node1'], self.df['p']):
            if terminal_id != False and terminal_id != 'disconnected':
                #get name for bus connected to generator
                bus_name = find_bus(self, net, terminals, buses, terminal_id)
                # if no bus found
                if bus_name == terminal_id:
                    # create new bus with connectivity node id as name
                    bus_name = terminals.terminal_connect[terminal_id]
                    add_missing_node(self, net, bus_name)
                # create generators in pandapower
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

    def create_pp_line(self, net, terminals, buses):
        for line_name, t1_id, t2_id, line_length in zip(self.df['name'],self.df['node1'], self.df['node2'], self.df['length']):
            
            if t1_id != False and t2_id != False and t1_id != 'disconnected' and t2_id != 'disconnected':
                std_type="N2XS(FL)2Y 1x300 RM/35 64/110 kV"
                bus1_name = find_bus(self, net, terminals, buses, t1_id)
                if bus1_name == t1_id:
                    # create new bus with connectivity node id as name
                    bus1_name = terminals.terminal_connect[t1_id]
                    add_missing_node(self, net, bus1_name)
                    
                bus2_name = find_bus(self, net, terminals, buses, t2_id)
                if bus2_name == t2_id:
                    # create new bus with connectivity node id as name
                    bus2_name = terminals.terminal_connect[t2_id]
                    add_missing_node(self, net, bus2_name)
                
                
                bus1 = pp.get_element_index(net, "bus", bus1_name)
                bus2 = pp.get_element_index(net, "bus", bus2_name)
                pp.create_line(net, bus1, bus2, line_length, std_type, name =line_name)    

class Transformers(GridObjects):

    def __init__(self, eq, ssh, ns, element_type = "PowerTransformer"):
        super().__init__(eq, ssh, ns, element_type)


    def create_pp_trans(self, net, terminals, buses):
            for trans_name, t1_id, t2_id, t3_id in zip(self.df['name'],self.df['node1'], self.df['node2'], self.df['node3']):
                if  t3_id != False and t3_id != 'disconnected':
                    std_type= '63/25/38 MVA 110/20/10 kV'
                    bus1_name = find_bus(self, net, terminals, buses, t1_id)
                    if bus1_name == t1_id:
                        # create new bus with connectivity node id as name
                        bus1_name = terminals.terminal_connect[t1_id]
                        add_missing_node(self, net, bus1_name)
                        
                    bus2_name = find_bus(self, net, terminals, buses, t2_id)
                    if bus2_name == t2_id:
                        # create new bus with connectivity node id as name
                        bus2_name = terminals.terminal_connect[t2_id]
                        add_missing_node(self, net, bus2_name)        
                                     
                    bus3_name = find_bus(self, net, terminals, buses, t3_id)
                    if bus3_name == t3_id:
                        # create new bus with connectivity node id as name
                        bus3_name = terminals.terminal_connect[t3_id]
                        add_missing_node(self, net, bus3_name)
                    
                    bus1 = pp.get_element_index(net, "bus", bus1_name)
                    bus2 = pp.get_element_index(net, "bus", bus2_name)
                    bus3 = pp.get_element_index(net, "bus", bus3_name)
                    pp.create_transformer3w(net, bus1, bus2, bus3, std_type, name =trans_name)
                
                else:
                    std_type='25 MVA 110/20 kV'
                    bus1_name = find_bus(self, net, terminals, buses, t1_id)
                    if bus1_name == t1_id:
                        # create new bus with connectivity node id as name
                        bus1_name = terminals.terminal_connect[t1_id]
                        add_missing_node(self, net, bus1_name)
                        
                    bus2_name = find_bus(self, net, terminals, buses, t2_id)
                    if bus2_name == t2_id:
                        # create new bus with connectivity node id as name
                        bus2_name = terminals.terminal_connect[t2_id]
                        add_missing_node(self, net, bus2_name)
                    bus1 = pp.get_element_index(net, "bus", bus1_name)
                    bus2 = pp.get_element_index(net, "bus", bus2_name)
                    pp.create_transformer(net, bus1, bus2, std_type, name =trans_name)