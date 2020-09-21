'''
Created on 2020-08-14

@author: wf
'''
import unittest
import getpass
from lodstorage.sparql import SPARQL
from lodstorage.sample import Sample
import time

class TestSPARQL(unittest.TestCase):
    ''' Test Apache Jena access via Wrapper'''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass

    def getJena(self,mode='query',debug=False,typedLiterals=False,profile=False):
        '''
        get the jena endpoint for the given mode
        
        Args:
           mode(string): query or update
           debug(boolean): True if debug information should be output
           typedLiterals(boolean): True if INSERT DATA SPARQL commands should use typed literals
           profile(boolean): True if profile/timing information should be shown
        '''
        endpoint="http://localhost:3030/example"
        jena=SPARQL(endpoint,mode=mode,debug=debug,typedLiterals=typedLiterals,profile=profile)
        return jena

    def testJenaQuery(self):
        '''
        test Apache Jena Fuseki SPARQL endpoint with example SELECT query 
        '''
        jena=self.getJena()
        queryString = "SELECT * WHERE { ?s ?p ?o. }"
        results=jena.query(queryString)
        self.assertTrue(len(results)>20)
        pass
    
    def testJenaInsert(self):
        '''
        test a Jena INSERT DATA
        '''
        jena=self.getJena(mode="update")
        insertCommands = [ """
        PREFIX cr: <http://cr.bitplan.com/>
        INSERT DATA { 
          cr:version cr:author "Wolfgang Fahl". 
        }
        """,'INVALID COMMAND']
        for index,insertCommand in enumerate(insertCommands):
            result,ex=jena.insert(insertCommand)
            if index==0:
                self.assertTrue(ex is None)
                print(result)
            else:
                msg=ex.args[0]
                self.assertTrue("QueryBadFormed" in msg)
                self.assertTrue("Error 400" in msg)
                pass
            
    def checkErrors(self,errors,expected=0):      
        '''
        check the given list of errors - print any errors if there are some
        and after that assert that the length of the list of errors is zero
        
        Args:
            errors(list): the list of errors to check
        '''
        if len(errors)>0:
            print("ERRORS:")
            for error in errors:
                print(error)
        self.assertEquals(expected,len(errors)) 
    
    def testDob(self):
        '''
        test the DOB (date of birth) function that converts from ISO-Date to
        datetime.date
        '''
        dt=Sample.dob("1926-04-21")
        self.assertEqual(1926,dt.year)
        self.assertEqual(4,dt.month)
        self.assertEqual(21,dt.day)
            
    def testListOfDictInsert(self):
        '''
        test inserting a list of Dicts and retrieving the values again
        using a person based example
        instead of
        https://en.wikipedia.org/wiki/FOAF_(ontology)
        
        we use an object oriented derivate of FOAF with a focus on datatypes
        '''
        listofDicts=Sample.getRoyals()
        typedLiteralModes=[True,False]
        entityType='foafo:Person'
        primaryKey='name'
        prefixes='PREFIX foafo: <http://foafo.bitplan.com/foafo/0.1/>'
        for typedLiteralMode in typedLiteralModes:
            jena=self.getJena(mode='update',typedLiterals=typedLiteralMode,debug=True)
            errors=jena.insertListOfDicts(listofDicts,entityType,primaryKey,prefixes)
            self.checkErrors(errors)
            
        jena=self.getJena(mode="query")    
        # does not work ...
        deleteString= """
        PREFIX foafo: <http://foafo.bitplan.com/foafo/0.1/>
        DELETE {
            ?person a foafo:Person 
        }
        """
        #jena.query(deleteString)
        queryString = """
        PREFIX foafo: <http://foafo.bitplan.com/foafo/0.1/>
        SELECT ?name ?born ?numberInLine ?wikidataurl ?age ?ofAge ?lastmodified WHERE { 
            ?person foafo:Person_name ?name.
            ?person foafo:Person_born ?born.
            ?person foafo:Person_numberInLine ?numberInLine.
            ?person foafo:Person_wikidataurl ?wikidataurl.
            ?person foafo:Person_age ?age.
            ?person foafo:Person_ofAge ?ofAge.
            ?person foafo:Person_lastmodified ?lastmodified. 
        }"""
        personResults=jena.query(queryString)
        self.assertEqual(len(listofDicts),len(personResults))
        personList=jena.asListOfDicts(personResults)   
        for index,person in enumerate(personList):
            print("%d: %s" %(index,person))
        # check the correct round-trip behavior
        self.assertEqual(listofDicts,personList)
        
    def testControlEscape(self):
        '''
        check the control-escaped version of an UTF-8 string
        '''
        controls="Α\tΩ\r\n";
        expected="Α\\tΩ\\r\\n"
        esc=SPARQL.controlEscape(controls)
        self.assertEqual(expected,esc)    
        
    def testSPARQLErrorMessage(self):
        '''
        test error handling 
        see https://stackoverflow.com/questions/63486767/how-can-i-get-the-fuseki-api-via-sparqlwrapper-to-properly-report-a-detailed-err
        '''
        listOfDicts=[{
            'title': '“Bioinformatics of Genome Regulation and Structure\Systems Biology” – BGRS\SB-2018',
            'url': 'https://thenode.biologists.com/event/11th-international-multiconference-bioinformatics-genome-regulation-structuresystems-biology-bgrssb-2018/'}]
        entityType="cr:Event"   
        primaryKey='title'
        prefixes="PREFIX cr: <http://cr.bitplan.com/Event/0.1/>"
        jena=self.getJena(mode='update',typedLiterals=False,debug=True)
        errors=jena.insertListOfDicts(listOfDicts,entityType,primaryKey,prefixes)
        self.checkErrors(errors,1)
        error=errors[0]
        self.assertTrue("probably the sparql query is bad formed" in error)
         
        
    def testEscapeStringContent(self):
        '''
        test handling of double quoted strings
        '''
        helpListOfDicts=[{'topic':'edit','description': '''Use 
the "edit" 
button to start editing - you can use 
- tab \t 
- carriage return \r 
- newline \n

as escape characters 
'''
        }]
        entityType='help:Topic'
        primaryKey='topic'
        prefixes='PREFIX help: <http://help.bitplan.com/help/0.0.1/>'    
        jena=self.getJena(mode='update',debug=True)
        errors=jena.insertListOfDicts(helpListOfDicts, entityType, primaryKey, prefixes, profile=True)
        self.checkErrors(errors)
        query="""
PREFIX help: <http://help.bitplan.com/help/0.0.1/>
        SELECT ?topic ?description
WHERE {
  ?help help:Topic_topic ?topic.
  ?help help:Topic_description ?description.
}
        """ 
        jena=self.getJena(mode='query')
        listOfDicts=jena.queryAsListOfDicts(query)
        # check round trip equality
        self.assertEqual(helpListOfDicts,listOfDicts)
   
    def testListOfDictSpeed(self):
        '''
        test the speed of adding data
        ''' 
        limit=5000
        for batchSize in [None,1000]:
            listOfDicts=Sample.getSample(limit)
            jena=self.getJena(mode='update',profile=True)
            entityType="ex:TestRecord"
            primaryKey='pkey'
            prefixes='PREFIX ex: <http://example.com/>'
            startTime=time.time()
            errors=jena.insertListOfDicts(listOfDicts, entityType, primaryKey, prefixes,batchSize=batchSize)   
            self.checkErrors(errors)
            elapsed=time.time()-startTime
            print ("adding %d records took %5.3f s => %5.f records/s" % (limit,elapsed,limit/elapsed))
        
    def testLocalWikdata(self):
        '''
        check local wikidata
        '''
        # check we have local wikidata copy:
        if getpass.getuser()=="wf":
            # use 2018 wikidata copy
            endpoint="http://jena.zeus.bitplan.com/wikidata/"
            wd=SPARQL(endpoint)
            queryString="""# get a list of whisky distilleries
PREFIX wd: <http://www.wikidata.org/entity/>            
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?item ?coord 
WHERE 
{
  # instance of whisky distillery
  ?item wdt:P31 wd:Q10373548.
  # get the coordinate
  ?item wdt:P625 ?coord.
}
"""
            results=wd.query(queryString)
            self.assertTrue(238<=len(results))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()