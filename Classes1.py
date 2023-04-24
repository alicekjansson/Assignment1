# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:09:05 2023

@author: Alice
"""
import pandas as pd
import xml.etree.ElementTree as ET
#Step 1: Parse XML files
EQ=ET.parse('Assignment_EQ_reduced.xml') 
SSH=ET.parse('Assignment_SSH_reduced.xml') 
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
        self.grid=EQ.getroot()
        self.loadflow=SSH.getroot()
        
    def setup(self):
        #Fill up dataframe based on XML files
        return

    
class Transformers:
    
    def __init__(self,eq,ssh):
        self.eq=eq
        self.ssh=ssh
        self.df=pd.DataFrame()
        self.grid=EQ.getroot()
        self.loadflow=SSH.getroot()
        
    def setup(self):
        #Fill up dataframe based on XML files
        return

class Lines:
    
    def __init__(self,eq,ssh):
        self.eq=eq
        self.ssh=ssh
        self.df=pd.DataFrame()
        self.grid=EQ.getroot()
        self.loadflow=SSH.getroot()
        
    def setup(self):
        #Fill up dataframe based on XML files
        return
    
class Shunts:
    
    def __init__(self,eq,ssh):
        self.eq=eq
        self.ssh=ssh
        self.df=pd.DataFrame()
        self.grid=EQ.getroot()
        self.loadflow=SSH.getroot()
        
    def setup(self):
        #Fill up dataframe based on XML files
        return
    
