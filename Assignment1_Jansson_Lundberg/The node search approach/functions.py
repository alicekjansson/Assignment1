# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:03:44 2023

@author: Alice
"""

#This file is for sharing functions which are of use to both of us
ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}



def get_node(grid,terminal):
    for cn in grid.findall('cim:ConnectivityNode',ns):
        if terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource') == "#" + cn.attrib.get(ns['rdf']+'ID'):
            node=cn.find('cim:IdentifiedObject.name',ns)
            return node.text
        else:       
            temp= 'NoBus'
    #If there is no bus
    return temp

def node_id(grid,terminal):
    for cn in grid.findall('cim:ConnectivityNode',ns):
        if terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource') == "#" + cn.attrib.get(ns['rdf']+'ID'):
            nodename=cn.find('cim:IdentifiedObject.name',ns)
            nodeid=cn.attrib.get(ns['rdf']+'ID')
            return nodename.text,nodeid
        else:
            temp= ('NoBus','NoBus')
    #If there is no bus
    return temp

def find_bus(grid,terminal):
    nodename,nodeid=node_id(grid,terminal)
    for terminal2 in grid.findall('cim:Terminal',ns):
        node2id=terminal2.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource')
        terminal2name=terminal2.find('cim:IdentifiedObject.name',ns).text
        #Terminal2 = breaker terminal
        # Find terminal at same connectivitynode which has a breaker
        if ('#'+nodeid == node2id) and (('Breaker' in terminal2name) or ('CIRCB' in terminal2name) or ('BREAKER' in terminal2name)):
            terminal2id=terminal2.attrib.get(ns['rdf']+'ID')
            breakerid2=terminal2.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource')
            for terminal3 in grid.findall('cim:Terminal',ns):
                terminal3id=terminal3.attrib.get(ns['rdf']+'ID')
                breakerid3=terminal3.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource')
                #Terminal3 = busbar terminal
                #Find terminal with the same breaker, this is busbar terminal
                if (terminal3id != terminal2id) and (breakerid2 == breakerid3):
                    return get_node(grid,terminal3)
         
# function to determine which connectivity node a bus, a load or a generator is associated with 
# (halfway generalized to lines and 2-winding transformers too)                
def get_cim_connectivity(self):
    # for each bus/load/generator (or busbar): check which connectivity node the terminal connects to,
    # and store that connectivity node in the grid object dataframe
    for item in self.list:
        n=0
        for terminal in self.grid.findall('cim:Terminal',ns):
            if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + item.attrib.get(ns['rdf']+'ID'):
                if n == 0:
                    self.node1.append(terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource'))
                    n+=1
                else:
                    self.node2.append(terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource'))
                    n+=1
        # relevant when considering 2-terminal objects as well
        if n == 1:
            self.node2.append(False)
    
    self.df['node1']=self.node1
    self.df['node2']=self.node2
                
# function to determine which bus a load/generator is connected to. 
def find_bus_connection(self, buses, node_no = 'node1'):
    
    bus_name_list = []
    # for each connectivity node for a load/generator - pair with corresponding bus connectivity node
    # store corresponding bus name in data frame
    for node in self.df[node_no]: 
        bus_row = buses.df.loc[buses.df['node1'] == node]
        if bus_row.empty is False:
            bus_name_list.append(bus_row['name'].values[0])
        else:
            bus_name_list.append(False)
    self.df[node_no+'_bus'] = bus_name_list       
    