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