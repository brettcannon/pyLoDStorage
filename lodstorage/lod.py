'''
Created on 2021-01-31

@author: wf
'''

class LOD(object):
    '''
    list of Dict aka Table
    '''

    def __init__(self,name):
        '''
        Constructor
        '''
        self.name=name
        pass
    
    @staticmethod
    def getFields(listOfDicts,sampleCount:int=None):
        if sampleCount is None:
            if listOfDicts is None:
                return None
            sampleCount=len(listOfDicts)
        fields=[]
        for row in listOfDicts:
            for key in row.keys():
                if not key in fields:
                    fields.append(key)
        return fields
        
    @staticmethod    
    def setNone4List(listOfDicts,fields):
        '''
        set the given fields to None for the records in the given listOfDicts
        if they are not set
        Args:
            listOfDicts(list): the list of records to work on
            fields(list): the list of fields to set to None 
        '''
        for record in listOfDicts:
            LOD.setNone(record, fields)
    
    @staticmethod
    def setNone(record,fields):
        '''
        make sure the given fields in the given record are set to none
        Args:
            record(dict): the record to work on
            fields(list): the list of fields to set to None 
        '''
        for field in fields:
            if not field in record:
                record[field]=None
                
    '''
    https://stackoverflow.com/questions/33542997/python-intersection-of-2-lists-of-dictionaries/33543164
    '''
    @staticmethod  
    def sortKey(d,key=None):
        ''' get the sort key for the given dict d with the given key
        '''
        if key is None:
            # https://stackoverflow.com/a/60765557/1497139
            return hash(tuple(d.items()))
        else:
            return d[key] 
        
    @staticmethod            
    def intersect(listOfDict1,listOfDict2,key=None):
        '''
        get the  intersection of the two lists of Dicts by the given key 
        '''
        i1=iter(sorted(listOfDict1, key=lambda k: LOD.sortKey(k, key)))
        i2=iter(sorted(listOfDict2, key=lambda k: LOD.sortKey(k, key)))
        c1=next(i1)
        c2=next(i2)
        lr=[]
        while True:
            try:
                val1=LOD.sortKey(c1,key)
                val2=LOD.sortKey(c2,key)
                if val1<val2:
                    c1=next(i1)
                elif val1>val2:
                    c2=next(i2)
                else:
                    lr.append(c1)
                    c1=next(i1)
                    c2=next(i2)
            except StopIteration:
                break     
        return lr    
    
    @staticmethod
    def addLookup(lookup,duplicates,record,value,withDuplicates:bool):
        '''
        add a single lookup result
        
        Args:
            lookup(dict): the lookup map
            duplicates(list): the list of duplicates
            record(dict): the current record
            value(object): the current value to lookup
            withDuplicates(bool): if True duplicates should be allowed and lists returned if False a separate duplicates
            list is created 
        '''
        if value in lookup:
            if withDuplicates:
                lookupResult=lookup[value]
                lookupResult.append(record)
            else:
                duplicates.append(record)
                return
        else:
            if withDuplicates:
                lookupResult=[record]
            else:
                lookupResult=record
        lookup[value]=lookupResult  
    
    @staticmethod
    def getLookup(lod:list,attrName:str,withDuplicates:bool=False):
        '''
        create a lookup dictionary by the given attribute name for the given list of dicts
        
        Args:
            lod(list): the list of dicts to get the lookup dictionary for
            attrName(str): the attribute to lookup
            withDuplicates(bool): whether to retain single values or lists
        
        Return:
            a dictionary for lookup
        '''
        lookup={}
        duplicates=[]
        for record in lod:
            value=None
            if isinstance(record,dict):
                if attrName in record:
                    value=record[attrName]
            else:
                if hasattr(record, attrName):
                    value=getattr(record,attrName)
            if value is not None:
                if isinstance(value,list):
                    for listValue in value:
                        LOD.addLookup(lookup,duplicates,record,listValue,withDuplicates)    
                else:
                    LOD.addLookup(lookup,duplicates,record,value,withDuplicates)    
        if withDuplicates:
            return lookup  
        else:
            return lookup,duplicates
