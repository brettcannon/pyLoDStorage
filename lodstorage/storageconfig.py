'''
Created on 2020-08-29

@author: wf
'''
from enum import Enum
import os
from pathlib import Path

class StoreMode(Enum):
    '''
    possible supported storage modes
    '''
    JSON = 1
    JSONABLE = 2
    SQL = 3
    SPARQL = 4
    YAML = 5    
    
class StorageConfig(object):
    '''
    a storage configuration
    '''
    
    @classmethod        
    def getCachePath(cls,name:str)->str:
        '''
        get the path to the default cache
        
        Args:
            name(str): the name of the cache to use
        '''
        home = str(Path.home())
        cachedir=f"{home}/{name}"
        return cachedir

    def __init__(self, mode=StoreMode.SQL,cacheFile=None,withShowProgress=True,profile=True,debug=False,errorDebug=True):
        '''
        Constructor
        
        Args:
            mode(StoreMode): the storage mode e.g. sql
            cacheFile(string): the common cacheFile to use (if any)
            withShowProgress(boolean): True if progress should be shown
            profile(boolean): True if timing / profiling information should be shown
            debug(boolean): True if debugging information should be shown
            errorDebug(boolean): True if debug info should be provided on errors (should not be used for production since it might reveal data)
        '''
        self.mode=mode
        self.cacheFile=cacheFile
        self.profile=profile
        self.withShowProgress=withShowProgress
        self.debug=debug
        self.errorDebug=errorDebug
        
    @staticmethod
    def getDefault(debug=False):
        return StorageConfig.getSQL(debug)    
        
    @staticmethod
    def getSQL(debug=False):
        config=StorageConfig(mode=StoreMode.SQL,debug=debug)
        config.tableName=None
        return config
    
    @staticmethod
    def getJSON(debug=False):
        config=StorageConfig(mode=StoreMode.JSON,debug=debug)
        return config
    
    @staticmethod
    def getJsonAble(debug=False):
        config=StorageConfig(mode=StoreMode.JSONABLE,debug=debug)
        return config
    
    @staticmethod
    def getSPARQL(prefix,endpoint,host,debug=False):
        config=StorageConfig(mode=StoreMode.SPARQL,debug=debug)
        config.prefix=prefix
        config.host=host
        config.endpoint=endpoint
        return config
    
    @staticmethod
    def getYaml(debug=False):
        config=StorageConfig(mode=StoreMode.YAML,debug=debug)
        return config
    
    