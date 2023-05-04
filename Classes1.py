# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:09:05 2023

@author: Alice
"""
import pandas as pd
import xml.etree.ElementTree as ET
from functions import get_node, find_bus


class GridObjects:
    
    def __init__(self,eq,ssh,ns,element_type):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.grid=eq.getroot()
        self.ldf=ssh.getroot()
        self.df=pd.DataFrame()
        self.list=self.grid.findall('cim:'+element_type,ns)
        self.name=[]
        
    def get_df(self):
        return self.df
        
class Buses(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        self.bus_list=self.grid.findall('cim:BusbarSection',ns)
        self.df=self.insert_busdata()
        
    def insert_busdata(self):
        voltages=[[],[],[]]
        connections=[]
        #Iterate through all buses and collect data
        for bus in self.bus_list:
            con=bus.find('cim:Equipment.EquipmentContainer',ns)
            id1=bus.attrib.get(ns['rdf']+'ID')
            #Iterate through voltagelevels to collect voltages
            for vl in self.grid.findall('cim:VoltageLevel',ns):
                if con.attrib.get(ns['rdf']+'resource') == "#" + vl.attrib.get(ns['rdf']+'ID'):
                    voltages[0].append(vl.find('cim:VoltageLevel.lowVoltageLimit',ns).text)
                    voltages[1].append(vl.find('cim:IdentifiedObject.name',ns).text)
                    voltages[2].append(vl.find('cim:VoltageLevel.highVoltageLimit',ns).text)
            #Iterate through terminals (and connectivitynodes) to find where bus is connected
            for terminal in self.grid.findall('cim:Terminal',ns):
                if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + id1:
                    connections.append(get_node(self.grid,terminal))
                            
        #Add data to dataframe    
        self.df['ID']=[element.attrib.get(ns['rdf']+'ID') for element in self.list]
        self.df['Name']=[bus.find('cim:IdentifiedObject.name',ns).text for bus in self.list]           
        self.df['ipMax']=[(bus.find('cim:BusbarSection.ipMax',ns).text) for bus in self.bus_list]
        self.df['lowVoltageLimit']=voltages[0]
        self.df['VoltageLevel']=voltages[1]
        self.df['highVoltageLimit']=voltages[2]
        self.df['Node']=connections
        return self.df
    



    
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
        for trans in self.trans_list:
            bus_exists=True
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
                                tempnode=find_bus(self.grid,terminal)
                                if tempnode == 'NoBus':
                                    bus_exists=False
                                else:
                                    node[i].append(tempnode)
                    if bus_exists==True:
                        rateds[i].append(transend.find('cim:PowerTransformerEnd.ratedS',ns).text)
                        ratedu[i].append(transend.find('cim:PowerTransformerEnd.ratedU',ns).text)
                    i=i+1
            if bus_exists==True:
                #Add substation info
                for sub in self.grid.findall('cim:Substation',ns):
                    if subid == '#' + sub.attrib.get(ns['rdf']+'ID'):
                        substation=sub.find('cim:IdentifiedObject.name',ns).text
                subs.append(substation)
                self.name.append(trans.find('cim:IdentifiedObject.name',ns).text)    
            
        self.df['Name']=self.name
        self.df['Substation']=subs
        self.df['HVRatedS']=rateds[0]
        self.df['HVRatedU']=ratedu[0]
        self.df['LVRatedS']=rateds[1]
        self.df['LVRatedU']=ratedu[1]
        self.df['HVNode']=node[0]
        self.df['LVNode']=node[1]

        return self.df

class Lines(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "ACLineSegment"):
        super().__init__(eq, ssh, ns, element_type)
        self.line_list=self.grid.findall('cim:ACLineSegment',ns)
        self.df=self.insert_linedata()
    
    def insert_linedata(self):
        length=[]
        volt=[]
        node=[]
        for line in self.line_list:
            bus_exists=True
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
                        tempnode=find_bus(self.grid,terminal)
                        if tempnode == 'NoBus':
                            bus_exists=False
                        else:
                            node.append(tempnode)
            if bus_exists==True:
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
                self.name.append(line.find('cim:IdentifiedObject.name',ns).text)
        self.df['Name']=self.name
        self.df['Length']=length
        self.df['VoltageLevel']=volt
        self.df['Node1']=node[::2]
        self.df['Node2']=node[1::2]
        return self.df

#Step 1: Parse XML files
# eq=ET.parse('Assignment_EQ_reduced.xml') 
# ssh=ET.parse('Assignment_SSH_reduced.xml') 
eq=ET.parse('MicroGridTestConfiguration_T1_NL_EQ_V2.xml') 
ssh=ET.parse('MicroGridTestConfiguration_T1_NL_SSH_V2.xml') 
ns=ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

#Test code
buses=Buses(eq,ssh,ns)
df_buses=buses.get_df()
transformers=Transformers(eq,ssh,ns)
df_trans=transformers.get_df()
lines=Lines(eq,ssh,ns)
df_lines=lines.get_df()

    
