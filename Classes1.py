# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:09:05 2023

@author: Alice
"""
import pandas as pd
import xml.etree.ElementTree as ET
#Step 1: Parse XML files
eq=ET.parse('Assignment_EQ_reduced.xml') 
ssh=ET.parse('Assignment_SSH_reduced.xml') 
ns=ns = {'cim':'http://iec.ch/TC57/2013/CIM-schema-cim16#',
      'entsoe':'http://entsoe.eu/CIM/SchemaExtension/3/1#',
      'rdf':'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
      'md':"http://iec.ch/TC57/61970-552/ModelDescription/1#"}

class Buses:
    
    def __init__(self,eq,ssh,ns):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.df=pd.DataFrame()
        self.grid=eq.getroot()
        self.loadflow=ssh.getroot()
        self.bus_list=self.grid.findall('cim:BusbarSection',ns)
        self.df.index=[bus.attrib.get(ns['rdf']+'ID') for bus in self.bus_list]
        self.df=self.insert_busdata()
        self.df['InService']=[True for el in range(len(self.bus_list))]
        self.df['Type']=['b' for el in range(len(self.bus_list))]
        
    def insert_busdata(self):
        names=[]
        voltages=[[],[],[]]
        for bus in self.bus_list:
            name=bus.find('cim:IdentifiedObject.name',ns)
            names.append(name.text)
            con=bus.find('cim:Equipment.EquipmentContainer',ns)
            for vl in self.grid.findall('cim:VoltageLevel',ns):
                if con.attrib.get(ns['rdf']+'resource') == "#" + vl.attrib.get(ns['rdf']+'ID'):
                    voltages[0].append(vl.find('cim:VoltageLevel.lowVoltageLimit',ns).text)
                    voltages[1].append(vl.find('cim:IdentifiedObject.name',ns).text)
                    voltages[2].append(vl.find('cim:VoltageLevel.highVoltageLimit',ns).text)
        self.df['Name']=names
        self.df['ipMax']=[(bus.find('cim:BusbarSection.ipMax',ns).text) for bus in self.bus_list]
        self.df['lowVoltageLimit']=voltages[0]
        self.df['VoltageLevel']=voltages[1]
        self.df['highVoltageLimit']=voltages[2]
        return self.df
    
    def get_df(self):
        return self.df
    
#Test code
buses=Buses(eq,ssh,ns)
df_buses=buses.get_df()

    
class Transformers:
    
    def __init__(self,eq,ssh,ns):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.df=pd.DataFrame()
        self.grid=eq.getroot()
        self.loadflow=ssh.getroot()
        
    def setup(self):
        #Fill up dataframe based on XML files
        return

class Lines:
    
    def __init__(self,eq,ssh,ns):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.df=pd.DataFrame()
        self.grid=eq.getroot()
        self.loadflow=ssh.getroot()
        
    def setup(self):
        #Fill up dataframe based on XML files
        return
    
class Shunts:
    
    def __init__(self,eq,ssh,ns):
        self.eq=eq
        self.ssh=ssh
        self.ns=ns
        self.df=pd.DataFrame()
        self.grid=eq.getroot()
        self.loadflow=ssh.getroot()
        
    def setup(self):
        #Fill up dataframe based on XML files
        return
    
