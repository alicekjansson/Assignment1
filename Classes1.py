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
        
    def get_connectors(self,busbar):
        connect_list=[]
        return connect_list
    
    def get_df(self):
        return self.df
    
    def get_list(self):
        return self.bus_list
        
    def setup(self):
        #Fill up dataframe based on XML files
        return
    
#Test code
buses=Buses(eq,ssh,ns).get_list()

    
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
    
