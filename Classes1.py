# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:09:05 2023

@author: Alice
"""
import pandas as pd
import xml.etree.ElementTree as ET
from functions import get_node


class GridObjects:
    
    def __init__(self,eq,ssh,ns,element_type):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.grid=eq.getroot()
        self.ldf=ssh.getroot()
        self.df=pd.DataFrame()
        self.list=self.grid.findall('cim:'+element_type,ns)
        self.df['ID']=[element.attrib.get(ns['rdf']+'ID') for element in self.list]
        
        
class Buses(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        self.bus_list=self.grid.findall('cim:BusbarSection',ns)
        self.df=self.insert_busdata()
        # self.df['InService']=[True for el in range(len(self.bus_list))]       #Solve this eventually from SSH?
        self.df['Type']=['b' for el in range(len(self.bus_list))]
        
    def insert_busdata(self):
        names=[]
        voltages=[[],[],[]]
        connections=[[],[]]
        #Iterate through all buses and collect data
        for bus in self.bus_list:
            name=bus.find('cim:IdentifiedObject.name',ns)
            names.append(name.text)
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
                    connections[0].append(terminal.find('cim:IdentifiedObject.name',ns).text)
                    connections[1].append(get_node(self.grid,terminal))
                            
        #Add data to dataframe               
        self.df['Name']=names
        self.df['ipMax']=[(bus.find('cim:BusbarSection.ipMax',ns).text) for bus in self.bus_list]
        self.df['lowVoltageLimit']=voltages[0]
        self.df['VoltageLevel']=voltages[1]
        self.df['highVoltageLimit']=voltages[2]
        self.df['Node']=connections[1]
        self.df['Terminal']=connections[0]
        return self.df
    
    def get_df(self):
        return self.df
    
class Transformers(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "PowerTransformer"):
        super().__init__(eq, ssh, ns, element_type)
        self.trans_list=self.grid.findall('cim:PowerTransformer',ns)
        self.df=self.insert_transdata()
        
    def insert_transdata(self):
        names=[]
        subs=[]
        term=[[],[]]
        node=[[],[]]
        rateds=[[],[]]
        ratedu=[[],[]]
        for trans in self.trans_list:
            name=trans.find('cim:IdentifiedObject.name',ns)
            names.append(name.text)
            subid=trans.find('cim:Equipment.EquipmentContainer',ns).attrib.get(ns['rdf']+'resource')
            transid=trans.attrib.get(ns['rdf']+'ID')            #ID of PowerTransformer
            #Add substation info
            for sub in self.grid.findall('cim:Substation',ns):
                if subid == '#' + sub.attrib.get(ns['rdf']+'ID'):
                    subs.append(sub.find('cim:IdentifiedObject.name',ns).text)
            #Add data about two sides of transformer
            i=0     #Keep track of which side of transformer
            for transend in self.grid.findall('cim:PowerTransformerEnd',ns):
                if '#' + transid == transend.find('cim:PowerTransformerEnd.PowerTransformer',ns).attrib.get(ns['rdf']+'resource'):
                    rateds[i].append(transend.find('cim:PowerTransformerEnd.ratedS',ns).text)
                    ratedu[i].append(transend.find('cim:PowerTransformerEnd.ratedU',ns).text)
                    #Get data on terminals the transformer end is connected to
                    for terminal in self.grid.findall('cim:Terminal',ns):
                        if transend.find('cim:TransformerEnd.Terminal',ns).attrib.get(ns['rdf']+'resource') == "#" + terminal.attrib.get(ns['rdf']+'ID'):
                            term[i].append(terminal.find('cim:IdentifiedObject.name',ns).text)
                            node[i].append(get_node(self.grid,terminal))    
                    i=i+1

        self.df['Name']=names
        self.df['Substation']=subs
        self.df['HVRatedS']=rateds[0]
        self.df['HVRatedU']=ratedu[0]
        self.df['LVRatedS']=rateds[1]
        self.df['LVRatedU']=ratedu[1]
        self.df['HVTerminal']=term[0]
        self.df['LVTerminal']=term[1]
        self.df['HVNode']=node[0]
        self.df['LVNode']=node[1]

        return self.df
    
    def get_df(self):
        return self.df

class Lines(GridObjects):
    
    def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
        super().__init__(eq, ssh, ns, element_type)
        self.line_list=self.grid.findall('cim:ACLineSegment',ns)
        self.df=self.insert_linedata()
    
    def insert_linedata(self):
        names=[]
        length=[]
        volt=[]
        term=[]
        node=[]
        pars=[[],[]]
        for line in self.line_list:
            lineid=line.attrib.get(ns['rdf']+'ID')  
            #Collect line data
            name=line.find('cim:IdentifiedObject.name',ns)
            names.append(name.text)
            l=line.find('cim:Conductor.length',ns).text
            length.append(l)
            pars[0].append(float(line.find('cim:ACLineSegment.r0',ns).text)/float(l))
            pars[1].append(float(line.find('cim:ACLineSegment.x0',ns).text)/float(l))
            #Find voltage levels
            for bv in self.grid.findall('cim:BaseVoltage',ns):
                if line.find('cim:ConductingEquipment.BaseVoltage',ns).attrib.get(ns['rdf']+'resource') == '#' + bv.attrib.get(ns['rdf']+'ID'):
                    volt.append(bv.find('cim:IdentifiedObject.name',ns).text)
            #Find connected terminals
            for terminal in self.grid.findall('cim:Terminal',ns):
                if terminal.find('cim:Terminal.ConductingEquipment',ns).attrib.get(ns['rdf']+'resource') == "#" + lineid:
                    term.append(terminal.find('cim:IdentifiedObject.name',ns).text)
                    node.append(get_node(self.grid,terminal)) 
        self.df['Name']=names
        self.df['Length']=length
        self.df['VoltageLevel']=volt
        self.df['Terminal1']=term[::2]      #Every other item in list is for the first terminal
        self.df['Terminal2']=term[1::2]     #Every other item in list is for the second terminal
        self.df['Node1']=node[::2]
        self.df['Node2']=node[1::2]
        self.df['r0/km']=pars[0]
        self.df['x0/km']=pars[1]
        return self.df
        
    def get_df(self):
        return self.df

#Step 1: Parse XML files
eq=ET.parse('Assignment_EQ_reduced.xml') 
ssh=ET.parse('Assignment_SSH_reduced.xml') 
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

  
#This is maybe??
# class Shunts(GridObjects):
    
#     def __init__(self, eq, ssh, ns, element_type = "BusbarSection"):
#         super().__init__(eq, ssh, ns, element_type)
    
