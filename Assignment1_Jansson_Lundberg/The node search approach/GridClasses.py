# -*- coding: utf-8 -*-
"""
Created on Fri May  5 08:50:57 2023

@author: Alice
"""

#This script holds all classes of grid objects, internally stored as GridObjects and can be read as dataframes

import pandas as pd
import pandapower as pp
from functions import get_node, find_bus, get_cim_connectivity, find_bus_connection
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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
        self.list=self.grid.findall('cim:'+element_type,ns)
        self.node1 = []
        self.node2 = []
        
        self.df['ID']=[element.attrib.get(ns['rdf']+'ID') for element in self.list]
        self.df['name']=[element.find('cim:IdentifiedObject.name',ns).text for element in self.list]
        get_cim_connectivity(self)
            
        
class Buses(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        self.get_cim_data()
        
    def get_cim_data(self):
        voltage_lvl = []  
        connections=[]
        for bus in self.list:
            container= bus.find('cim:Equipment.EquipmentContainer',ns)
            #Iterate through voltagelevels to collect voltages
            for vl in self.grid.findall('cim:VoltageLevel',ns):
                if container.attrib.get(ns['rdf']+'resource') == "#" + vl.attrib.get(ns['rdf']+'ID'):
                    voltage_lvl.append(vl.find('cim:IdentifiedObject.name',ns).text)
            id1=bus.attrib.get(ns['rdf']+'ID')
            #Iterate through terminals (and connectivitynodes) to find where bus is connected
            for terminal in self.grid.findall('cim:Terminal',ns):
                if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + id1:
                    nodename=(get_node(self.grid,terminal))  
                    #Check if the connectivitynode is for a busbar
                    if 'Busbar' in nodename:
                        connections.append(nodename)
                    else:
                        #Otherwise find busbar via breaker
                        connections.append(find_bus(self.grid,terminal))
        self.df['voltage'] = voltage_lvl
        self.df['Busbar']  = connections
        

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
        
        
    def create_pp_load(self, net, buses):
        find_bus_connection(self, buses)
        for load_name, bus_name, active_power in zip(self.df['name'],self.df['node1_bus'], self.df['p']):
            if bus_name is not False:
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
        
        
    def create_pp_gen(self, net, buses):
        find_bus_connection(self, buses)
        for gen_name, bus_name, active_power in zip(self.df['name'],self.df['node1_bus'], self.df['p']):
            if bus_name is not False:
                bus = pp.get_element_index(net, "bus", bus_name)
                pp.create_gen(net, bus, active_power, name =gen_name)
        
class Lines(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "ACLineSegment"):
        super().__init__(eq, ssh, ns, element_type)
        self.line_list=self.grid.findall('cim:ACLineSegment',ns)
        self.df=self.insert_linedata()
    
    def insert_linedata(self):
        length=[]
        volt=[]
        node=[]
        name=[]
        for line in self.line_list:
            lineid=line.attrib.get(ns['rdf']+'ID')       
            #Find connected terminals
            for terminal in self.grid.findall('cim:Terminal',ns):
                if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + lineid:
                    #Check if the connectivitynode is for a busbar
                    nodename=(get_node(self.grid,terminal))
                    if 'Busbar' in nodename:
                        node.append(nodename)
                    else:
                        #Find busbar via breaker
                        node.append(find_bus(self.grid,terminal))
            #Collect line data
            l=line.find('cim:Conductor.length',ns).text
            #Find voltage levels
            for bv in self.grid.findall('cim:BaseVoltage',ns):
                if line.find('cim:ConductingEquipment.BaseVoltage',ns).attrib.get(ns['rdf']+'resource') == '#' + bv.attrib.get(ns['rdf']+'ID'):
                    voltage=bv.find('cim:IdentifiedObject.name',ns).text 
                else:
                    voltage='None'
            volt.append(voltage)
            length.append(l)
            name.append(line.find('cim:IdentifiedObject.name',ns).text)
        self.df['Name']=name
        self.df['Length']=length
        self.df['VoltageLevel']=volt
        self.df['Node1']=node[::2]
        self.df['Node2']=node[1::2]
        return self.df   
    
    def create_pp_line(self, net):
        for line_name, bus1_name, bus2_name, length in zip(self.df['name'],self.df['Node1'],self.df['Node2'], self.df['Length']):
            if ((bus1_name is not None) and (bus2_name is not None)):
                bus1 = pp.get_element_index(net, "bus", bus1_name)
                bus2=pp.get_element_index(net, "bus", bus2_name)
                pp.create_line(net,bus1,bus2,length,'NAYY 4x50 SE',line_name)

class Transformers(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "PowerTransformer"):
        super().__init__(eq, ssh, ns, element_type)
        self.trans_list=self.grid.findall('cim:PowerTransformer',ns)
        self.df=self.insert_transdata()
        
    def insert_transdata(self):
        subs=[]
        node=[[],[]]
        rateds=[[],[]]
        ratedu=[[],[]]
        name=[]
        for trans in self.trans_list:
            subid=trans.find('cim:Equipment.EquipmentContainer',ns).attrib.get(ns['rdf']+'resource')
            transid=trans.attrib.get(ns['rdf']+'ID')            #ID of PowerTransformer
            #Add data about two sides of transformer
            i=0     #Keep track of which side of transformer
            for transend in self.grid.findall('cim:PowerTransformerEnd',ns):
                if '#' + transid == transend.find('cim:PowerTransformerEnd.PowerTransformer',ns).attrib.get(ns['rdf']+'resource'):
                    #Get data on terminals the transformer end is connected to
                    for terminal in self.grid.findall('cim:Terminal',ns):
                        if transend.find('cim:TransformerEnd.Terminal',ns).attrib.get(ns['rdf']+'resource') == "#" + terminal.attrib.get(ns['rdf']+'ID'):
                            nodename=(get_node(self.grid,terminal))  
                            #Check if the connectivitynode is for a busbar
                            if 'Busbar' in nodename:
                                node[i].append(nodename)
                            else:
                                #Otherwise find busbar via breaker
                                node[i].append(find_bus(self.grid,terminal))

                    rateds[i].append(transend.find('cim:PowerTransformerEnd.ratedS',ns).text)
                    ratedu[i].append(transend.find('cim:PowerTransformerEnd.ratedU',ns).text)
                    i=i+1

            #Add substation info
            for sub in self.grid.findall('cim:Substation',ns):
                if subid == '#' + sub.attrib.get(ns['rdf']+'ID'):
                    substation=sub.find('cim:IdentifiedObject.name',ns).text
            subs.append(substation)
            name.append(trans.find('cim:IdentifiedObject.name',ns).text)    
            
        self.df['Name']=name
        self.df['Substation']=subs
        self.df['HVRatedS']=rateds[0]
        self.df['HVRatedU']=ratedu[0]
        self.df['LVRatedS']=rateds[1]
        self.df['LVRatedU']=ratedu[1]
        self.df['HVNode']=node[0]
        self.df['LVNode']=node[1]

        return self.df
    
    def create_pp_trans(self, net, buses):
        buslist=list(buses.df['name'])
        for trans_name, bus1_name, bus2_name in zip(self.df['name'],self.df['HVNode'],self.df['LVNode']):
            if ((bus1_name in buslist) and (bus2_name in buslist)):
                bus1 = pp.get_element_index(net, "bus", bus1_name)
                bus2=pp.get_element_index(net, "bus", bus2_name)
                pp.create_transformer(net,bus1,bus2,'25 MVA 110/20 kV',trans_name)

