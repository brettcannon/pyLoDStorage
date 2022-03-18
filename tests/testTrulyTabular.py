'''
Created on 2022-03-4

@author: wf
'''
import unittest
from lodstorage.trulytabular import TrulyTabular, WikidataItem
from lodstorage.query import Query
from lodstorage.sparql import SPARQL

class TestTrulyTabular(unittest.TestCase):
    '''
    test Truly tabular analysis
    '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass

    def testGetFirst(self):
        '''
        test the get First helper function
        '''
        tt=TrulyTabular("Q2020153")
        testcases=[
            { 
                "qlod":[{"name":"firstname"}],
                "expected": "firstname"
            },
            {
                "qlod":[],
                "expected": None
            },
            {
                "qlod":[{"name":"firstname"},{"name":"second name"}],
                "expected": None
            }
        ]
        for testcase in testcases:
            qLod=testcase["qlod"]
            expected=testcase["expected"]
            try:
                value=tt.getFirst(qLod,"name")
                self.assertEqual(expected,value)
            except Exception as ex:
                if self.debug:
                    print(str(ex))
                self.assertIsNone(expected)
                
    def documentQuery(self,tt,query,show=True,formats=["mediawiki"]):
        '''
        document the given query for the given TrueTabular instance
        '''
        qlod=tt.sparql.queryAsListOfDicts(query.query)
        for tablefmt in formats:
            tryItUrl="https://query.wikidata.org/"
            doc=query.documentQueryResult(qlod, tablefmt=tablefmt,tryItUrl=tryItUrl,floatfmt=".0f")
            docstr=doc.asText()
            if show:
                print (docstr)
                
    def testGetPropertiesByLabel(self):
        '''
        try getting properties by label
        '''
        debug=self.debug
        #debug=True
        propList=["title","country","location"]
        tt=TrulyTabular("Q2020153",propList)
        if debug:
            print (tt.properties)
        for prop in propList:
            self.assertTrue(prop in tt.properties)
            
    def testGetItemsByLabel(self):
        '''
        try getting items by label
        '''
        qLabels=["academic conference","scientific conference series","whisky distillery","human"]
        sparql=SPARQL(TrulyTabular.endpoint)
        items=WikidataItem.getItemsByLabel(sparql, qLabels)
        for item in items.values():
            print(item)
        for qLabel in qLabels:
            self.assertTrue(qLabel in items)

    def testTrulyTabularTables(self):
        '''
        test Truly Tabular for different tabular queries
        '''
        debug=self.debug
        #debug=True
        show=False
        showStats=["mediawiki","github","latex"]
        tables=[ 
            {
               "name": "computer scientist",
               "title": "humans with the occupation computer scientist",
               "qid":"Q5", # human
               "where": "?item wdt:P106 wd:Q82594.", # computer scientist only
               "propertyLabels": ["sex or gender","date of birth","place of birth","field of work","occupation","ORCID iD",
                                  "GND ID","DBLP author ID","Google Scholar author ID","VIAF ID"],
               "expected": 10  
            },
            {
               "name": "academic conferences",
               "title": "academic conferences",
               "qid": "Q2020153",# academic conference
               "propertyLabels":["title","country","location","short name","start time",
                "end time","part of the series","official website","described at URL",
                "WikiCFP event ID","GND ID","VIAF ID","main subject","language used",
                "is proceedings from"
               ],
               "expected": 7500
            },
            {
                "name": "scientific conferences series",
                "title": "scientific conference series",
                "qid": "Q47258130", # scientific conference series
                "propertyLabels":["title","short name","inception","official website","DBLP venue ID","GND ID",
                    "Microsoft Academic ID","Freebase ID","WikiCFP conference series ID",
                    "Publons journals/conferences ID","ACM conference ID"],
                "expected": 4200
            },
            {
                "name": "whisky distilleries",
                "title": "whisky distilleries",
                "qid": "Q10373548", # whisky distillery
                "propertyLabels":["inception","official website","owned by","country","headquarters location","Whiskybase distillery ID"],
                "expected": 200
            }
        ]
        errors=0
        for table in tables[3:]:
            # academic conference
            where=None
            if "where" in table:
                where=table["where"]
            tt=TrulyTabular(table["qid"],table["propertyLabels"],where=where,debug=debug)
            if "is proceedings from" in tt.properties:
                tt.properties["is proceedings from"].reverse=True
            count=tt.count()
            if (debug):
                print(count)
            self.assertTrue(count>table["expected"])
            stats=tt.getPropertyStatics()
            # sort descending by total percentage
            stats = sorted(stats, key=lambda row: row['total%'],reverse=True) 
            for tablefmt in showStats:
                query=Query(name=table["name"],title=table["title"],query="")
                doc=query.documentQueryResult(stats, tablefmt=tablefmt, withSourceCode=False)
                print(doc)
            if show:
                for wdProperty in tt.properties.values():
                    for asFrequency in [True,False]:
                        query=tt.noneTabularQuery(wdProperty,asFrequency=asFrequency)
                        try:
                            self.documentQuery(tt, query)
                        except Exception as ex:
                            print(f"query for {wdProperty} failed\n{str(ex)}")
                            errors+=1
                self.assertEqual(0,errors)
            
                
    def testMostFrequentIdentifiers(self):
        '''
        test getting the most frequent identifiers for some Wikidata Items
        '''
        show=True
        debug=self.debug
        #debug=True
        for qid in ["Q2020153","Q47258130","Q1143604"]:
            tt=TrulyTabular(qid,debug=debug)
            query=tt.mostFrequentIdentifiersQuery()
            self.documentQuery(tt, query,formats=["github"],show=show)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()