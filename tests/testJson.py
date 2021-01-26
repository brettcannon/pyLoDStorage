'''
Created on 2020-09-12

@author: wf
'''
import unittest
import json
from lodstorage.sample import Royals,Cities
from lodstorage.jsonable import JSONAble, Types
import time

class TestJsonAble(unittest.TestCase):
    '''
    test JSON serialization with JsonAble mixin
    '''

    def setUp(self):
        self.profile=False
        self.debug=False
        pass

    def tearDown(self):
        pass
        
    
    def testSingleToDoubleQuote(self):
        jsonStr='''
        {
            "cities": [
            {
                "name": "Upper Hell's Gate"
            },
            {
                 "name": "N'zeto"
            }
            ]
        }
        '''
        listOfDicts=json.loads(jsonStr)
        dictStr=str(listOfDicts)   
        if self.debug:
            print(dictStr)
        jsonStr2=JSONAble.singleQuoteToDoubleQuote(dictStr)
        if self.debug:
            print(jsonStr2)
        self.assertEqual('''{"cities": [{"name": "Upper Hell's Gate"}, {"name": "N'zeto"}]}''',jsonStr2)
        
    def testSingleQuoteToDoubleQuoteStackoverflow(self):
        """
        see 
            - https://stackoverflow.com/a/63862387/1497139 
            - https://stackoverflow.com/a/50257217/1497139
        """
        singleQuotedExamples=[
            '''{'cities': [{'name': "Upper Hell's Gate"}, {'name': "N'zeto"}]''']
        for example in singleQuotedExamples:
            if self.debug:
                print (example)
            for useRegex in [False,True]:
                doubleQuoted=JSONAble.singleQuoteToDoubleQuote(example,useRegex=useRegex)
                if self.debug:
                    print(doubleQuoted)
            if self.debug:
                print
            
    def dumpListOfDicts(self,listOfDicts,limit):
        if self.debug:
            for index,record in enumerate(listOfDicts[:limit]):
                print("%2d:%s" % (index,record))
                
    def check(self,manager,manager1,listName,debugLimit):
        self.dumpListOfDicts(manager.__dict__[listName], debugLimit)
        self.dumpListOfDicts(manager1.__dict__[listName], debugLimit)
        self.assertEqual(manager.__dict__,manager1.__dict__)    
            
    def testJsonAble(self):
        '''
        test JSONAble
        '''
        examples=[{
            'manager': Royals(load=True),
            'listName': 'royals'
        }, {
            'manager': Cities(load=True),
            'listName': 'cities'
        }
        ]
        debugLimit=10
        debugChars=debugLimit*100
        index=0
        for useToJson in [True,False]:
            for example in examples:
                starttime=time.time()
                manager=example['manager']
                listName=example['listName']
                if useToJson:
                    jsonStr=manager.toJSON()
                else:
                    jsonStr=manager.asJSON()
                if self.debug:
                    print(jsonStr[:debugChars])
                    #print(jsonStr,file=open('/tmp/example%d.json' %index,'w'))
                index+=1
                if self.profile:
                    print("->JSON for %d took %7.3f s" % (index, (time.time()-starttime)))
                self.assertTrue(isinstance(jsonStr,str))
                starttime=time.time()
                jsonDict=json.loads(jsonStr)
                self.assertTrue(isinstance(jsonDict,dict))
                if self.debug:
                    print(str(jsonDict)[:debugChars])
                if self.profile:
                    print("<-JSON for %d took %7.3f s" % (index, time.time()-starttime))
                cls=manager.__class__
                types=Types(cls.__name__)
                types.getTypes(listName,manager.__dict__[listName])
                manager1=cls()
                manager1.fromJson(jsonStr,types=types)
                self.check(manager,manager1,listName,debugLimit=debugLimit)
        pass
    
    def testRoyals(self):
        '''
        test Royals example
        '''
        royals1=Royals(load=True)
        self.assertEqual(4,len(royals1.royals))
        json=royals1.toJSON()
        if self.debug:
            print(json)
        types=Types.forTable(royals1, "royals",debug=True)
        royals2=Royals()
        royals2.fromJson(json,types=types)
        self.assertEqual(4,len(royals2.royals))
        if self.debug:
            print(royals1.royals)
            print(royals2.royals)
        self.assertEqual(royals1.royals,royals2.royals)
    
    def testTypes(self):
        '''
        test the given types
        '''
        royals1=Royals(load=True)
        types1=Types.forTable(royals1, "royals")
        json=types1.toJSON()
        if self.debug:
            print(json)
        types2=Types("Royals")
        types2.fromJson(json)
        self.assertEqual(types1.typeMap,types2.typeMap)
        
    def testStoreAndRestore(self):
        '''
        test storing and restoring from a JSON file
        '''
        royals1=Royals(load=True)
        storeFilePrefix="/tmp/royals-pylodstorage"
        royals1.storeToJsonFile(storeFilePrefix,"royals")
        royals2=Royals()
        royals2.restoreFromJsonFile(storeFilePrefix)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()