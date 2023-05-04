# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:03:44 2023

@author: Alice
"""

#This file is for sharing functions which are of use to both of us
ns=ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
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
        if ('#'+nodeid == node2id) and (('Breaker' in terminal2name) or 'CIRCB' in terminal2name):
            terminal2id=terminal2.attrib.get(ns['rdf']+'ID')
            breakerid2=terminal2.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource')
            for terminal3 in grid.findall('cim:Terminal',ns):
                terminal3id=terminal3.attrib.get(ns['rdf']+'ID')
                breakerid3=terminal3.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource')
                #Terminal3 = busbar terminal
                #Find terminal with the same breaker, this is busbar terminal
                if (terminal3id != terminal2id) and (breakerid2 == breakerid3):
                    return get_node(grid,terminal3)