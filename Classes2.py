# -*- coding: utf-8 -*-
"""
Created on Fri May  5 08:50:57 2023

@author: Alice
"""

import pandas as pd
import pandapower as pp
import pandapower.plotting as plot
import xml.etree.ElementTree as ET
from functions import get_node, find_bus
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class GridNodeObjects:
    
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
        self.get_cim_connectivity()
            
        
    def get_cim_connectivity(self):
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
            if n == 1:
                self.node2.append(False)
        
        self.df['node1']=self.node1
        self.df['node2']=self.node2
        
    def find_bus_connection(self, buses, node_no = 'node1'):
        
        bus_name_list = []
        for node in self.df[node_no]: 
            bus_row = buses.df.loc[buses.df['node1'] == node]
            if bus_row.empty is False:
                bus_name_list.append(bus_row['name'].values[0])
            else:
                n = 0
                iter_max = 10
                while n < iter_max:
                    new_node = self.bus_search(node)
                    bus_row = buses.df.loc[buses.df['node1'] == new_node]
                    if bus_row.empty is False:
                        bus_name_list.append(bus_row['name'].values[0])
                        break
                    else:
                        node = new_node
                        n+=1
                if n == iter_max:
                    bus_name_list.append(False)
                    
        self.df[node_no+'_bus'] = bus_name_list
        
                
    def bus_search(self, node):
        for terminal in self.grid.findall('cim:Terminal',ns):
            if terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource') == node:
                        cond_equip = terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource')
                        for terminal in self.grid.findall('cim:Terminal',ns):
                            if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == cond_equip:
                                if terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource') != node:
                                    new_node = terminal.find('cim:Terminal.ConnectivityNode',ns).attrib.get(ns['rdf']+'resource')
        return new_node                            
                                    
            

        
class Buses(GridNodeObjects):
    
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
                               
        #self.df.apply(lambda row: pp.create_bus(net, name=row['name'],vn_kv=row['voltage']),axis=1)
        


class Loads(GridNodeObjects):
    
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
            if bus_name is not False:
                bus = pp.get_element_index(net, "bus", bus_name)
                pp.create_load(net, bus, active_power, name =load_name)
        
    
class Generators(GridNodeObjects):
    
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
            if bus_name is not False:
                bus = pp.get_element_index(net, "bus", bus_name)
                pp.create_gen(net, bus, active_power, name =gen_name)
        
class Lines(GridNodeObjects):
    
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

class Transformers(GridNodeObjects):
    
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

eq = ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml')
ssh = ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml')
# eq = ET.parse('Assignment_EQ_reduced.xml')
# ssh = ET.parse('Assignment_SSH_reduced.xml')


ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

#Main: Create grid in Pandapower and plot
#Start with creating empty network
net = pp.create_empty_network()
#Create buses
buses = Buses(eq,ssh,ns)
df_buses=buses.df
buses.create_pp_bus(net)
#Create loads
loads = Loads(eq,ssh,ns)
loads.find_bus_connection(buses)
loads.create_pp_load(net)
#Create generators
gens = Generators(eq,ssh,ns)
gens.find_bus_connection(buses)
gens.create_pp_gen(net)
#Create lines
lines = Lines(eq,ssh,ns)
df_line=lines.df
lines.create_pp_line(net)
#Create transformers
trans=Transformers(eq,ssh,ns)
df_trans=trans.df
trans.create_pp_trans(net,buses)
#Plot   
plot.simple_plot(net)