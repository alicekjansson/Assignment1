# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 16:09:44 2023

@author: ielmartin
"""
import pandapower as pp

#This file is for sharing functions which are of use to both of us
ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}


def get_component_connection(self, terminals):
    # for each component in component_list
    for item in self.list:
        # counter for multiterminal objects
        n=0
        # go through terminals
        for terminal in self.grid.findall('cim:Terminal',ns):
            
            if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + item.attrib.get(ns['rdf']+'ID'):
                
                terminal_id = '#' + terminal.attrib.get(ns['rdf']+'ID')
                node_id = terminals.terminal_connect[terminal_id]
                
                if node_id == 'false':
                    terminal_id  = 'disconnected'
                    
                if n == 0:    
                    self.node1.append(terminal_id)
                    
                if n == 1:                  
                    self.node2.append(terminal_id)
                    
                if n == 2:
                    self.node3.append(terminal_id)
                
                n+=1
        # for single and two-terminal objects, ignore superfluous terminals
        if n == 1:
            self.node2.append(False)
            self.node3.append(False)
        
        if n == 2:
            self.node3.append(False)
                
    self.df['node1']=self.node1
    self.df['node2']=self.node2
    self.df['node3']=self.node3
     
def find_bus(self, net, terminals, buses, terminal_id):
    # get cn id
    node_id = terminals.terminal_connect[terminal_id]
    # check if existing bus connected to same cn, if so return bus name
    for t_id in buses.df['node1'].values:
        if terminals.terminal_connect[t_id] == node_id:
            row = buses.df[buses.df['node1'] == t_id]
            return(row['name'].values[0])
    
    # else check if new bus connected to same cn already has been created
    for bus_name in net.bus['name']:
        if bus_name == node_id:
            return bus_name
    
    # else if load or generator set new bus name
    if self.e_type == 'EnergyConsumer' or self.e_type == 'SynchronousMachine': 
        return terminal_id
    
    # else for lines and transformers
    elif self.e_type == 'ACLineSegment' or self.e_type == 'PowerTransformer':
        bus_name = terminal_id
        # if no existing bus found, check if terminal is connected to existing bus via breaker
        for t_id, n_id in terminals.terminal_connect.items():
            #find other terminals connected to same connectivity node
            if t_id != terminal_id and n_id == node_id:
                for terminal in self.grid.findall('cim:Terminal',ns):
                    terminal_name=terminal.find('cim:IdentifiedObject.name',ns).text
                    # find circiut breaker connected to same connectivity node
                    if '#' + terminal.attrib.get(ns['rdf']+'ID') == t_id and (('Breaker' in terminal_name) or ('CIRCB' in terminal_name) or ('BREAKER' in terminal_name)):
                        breaker_id=terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource')
                        # find other breaker terminal and retrieve connectivity node
                        for terminal2 in self.grid.findall('cim:Terminal',ns):
                            if terminal2.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == breaker_id:
                                if terminal2.find('cim:IdentifiedObject.name',ns).text != terminal_name:
                                    terminal_check = '#' + terminal2.attrib.get(ns['rdf']+'ID')
                                    #print(terminal_name)
                                    node_id = terminals.terminal_connect[terminal_check]
                                    #print(node_id)
                                    # check if existing bus connected to same cn, if so return bus name
                                    for t_id in buses.df['node1'].values:
                                        if terminals.terminal_connect[t_id] == node_id:
                                            row = buses.df[buses.df['node1'] == t_id]
                                            return(row['name'].values[0])
                                     # else check if new bus connected to same cn already has been created
                                    for name in net.bus['name']:
                                        if name == node_id:
                                            return name
        
        return bus_name 
         
 
def add_missing_node(self, net, bus_name):
    voltage = 110
    pp.create_bus(net, name=bus_name,vn_kv=voltage, type='n')