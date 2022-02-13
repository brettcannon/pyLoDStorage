'''
Created on 2021-01-29

@author: wf
'''
import unittest
import copy
import io
import os
from contextlib import redirect_stdout
from lodstorage.query import QueryManager, Query, QueryResultDocumentation
from lodstorage.querymain import main as queryMain
from lodstorage.sparql import SPARQL
import tests.testSqlite3
from tests.basetest import Basetest

class TestQueries(Basetest):
    '''
    Test query handling
    '''

    def testSQLQueries(self):
        '''
        see https://github.com/WolfgangFahl/pyLoDStorage/issues/19
        '''
        show=self.debug
        qm=QueryManager(lang='sql',debug=False)
        self.assertEqual(2,len(qm.queriesByName)) 
        sqlDB=tests.testSqlite3.TestSQLDB.getSampleTableDB()
        #print(sqlDB.getTableDict())
        for _name,query in qm.queriesByName.items():
            listOfDicts=sqlDB.query(query.query)
            resultDoc=query.documentQueryResult(listOfDicts)         
            if show:
                print(resultDoc)
        pass
    
    def testSparqlQueries(self):
        '''
        test SPARQL queries 
        '''
        show=self.debug
        show=True
        qm=QueryManager(lang='sparql',debug=False)
        for name,query in qm.queriesByName.items():
            if name in ["Nicknames"]:
                if show:
                    print(f"{name}:{query}")
                endpoint=SPARQL(query.endpoint)
                try:
                    qlod=endpoint.queryAsListOfDicts(query.query)
                    for tablefmt in ["mediawiki","github","latex"]:
                        doc=query.documentQueryResult(qlod, tablefmt=tablefmt,floatfmt=".0f")
                        docstr=doc.asText()
                        if show:
                            print (docstr)
                            
                except Exception as ex:
                    print(f"{query.title} at {query.endpoint} failed: {ex}")
        
    def testUnicode2LatexWorkaround(self):
        '''
        test the uniCode2Latex conversion workaround
        '''
        debug=self.debug
        for code in range(8320,8330):
            uc=chr(code)
            latex=QueryResultDocumentation.uniCode2Latex(uc)
            if debug:
                print(f"{uc}→{latex}")
            #self.assertTrue(latex.startswith("$_"))
        unicode="À votre santé!"
        latex=QueryResultDocumentation.uniCode2Latex(unicode)
        if debug:
            print(f"{unicode}→{latex}")
        self.assertEqual("\\`A votre sant\\'e!",latex)
    
    def testWikiDataLinker(self):
        '''
        https://github.com/WolfgangFahl/pyLoDStorage/issues/56
        
        addWikiData Linker to QueryResultDocumentation and callback for further such handlers while at it
        '''
        qlod=[
            {"wikidata":"http://www.wikidata.org/entity/Q1353","label":"Delhi"},
            {"wikidata":"Q2","label":"Earth"},
            {"wikidata":"https://www.wikidata.org/wiki/Property:P31","label":"instanceof"}
        ]
        query=Query(name="testQuery",query="no specific query")
        query.addFormatCallBack(QueryResultDocumentation.wikiDataLink)
        debug=self.debug
        #debug=True
        lod=copy.deepcopy(qlod)
        query.preFormatWithCallBacks(lod,"mediawiki")
        if debug:
            print(lod)
        self.assertEqual("[https://www.wikidata.org/wiki/Q1353 Q1353]",lod[0]["wikidata"])
        self.assertEqual("[https://www.wikidata.org/wiki/Q2 Q2]",lod[1]["wikidata"])
        self.assertEqual("[https://www.wikidata.org/wiki/Property:P31 Property:P31]",lod[2]["wikidata"])
        
    def testQueryCommandLine(self):
        '''
        test the sparql query command line
        '''
        debug=self.debug
        #debug=True
        args=["-d","-qn","US President Nicknames","-l","sparql","-f","csv"]
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            queryMain(args)
            result=stdout.getvalue()
        self.assertTrue('''Theodore Roosevelt","Teddy"''' in result)
        if debug:
            print(result)
        
    def testCommandLineUsage(self):
        '''
        test the command line usage
        '''
        args=["-h"]
        try:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                queryMain(args)
            self.fail("system exit expected")
        except SystemExit:
            pass
        debug=self.debug
        #debug=True
        if debug:
            print(stdout.getvalue())
        self.assertTrue("--queryName" in stdout.getvalue())
            
    def testQueryDocumentation(self):
        '''
        test QueryDocumentation
        '''
        show=self.debug
        #show=True
        queries=[
            {
                "endpoint":"https://query.wikidata.org/sparql",
                "prefixes": [],
                "lang": "sparql",
                "name": "Nicknames",
                "description": "https://stackoverflow.com/questions/70206791/sparql-i-have-individual-with-multiple-values-for-single-object-property-how",
                "title": "Nick names of US Presidents",
                "query":"""SELECT ?item ?itemLabel (GROUP_CONCAT(DISTINCT ?nickName; SEPARATOR=",") as ?nickNames)
WHERE 
{
  # president
  ?item wdt:P39 wd:Q11696.
  ?item wdt:P1449 ?nickName
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} GROUP BY ?item ?itemLabel"""
            },
            {
            "endpoint":"https://query.wikidata.org/sparql",
            "prefixes": ["http://www.wikidata.org/entity/","http://commons.wikimedia.org/wiki/Special:FilePath/"],
            "lang": "sparql",
            "name": "CAS15",
            "title": "15 Random substances with CAS number",
            "description": "Wikidata SPARQL query showing the 15 random chemical substances with their CAS Number",
            "query": """# List of 15 random chemical components with CAS-Number, formula and structure
# see also https://github.com/WolfgangFahl/pyLoDStorage/issues/46
# WF 2021-08-23
SELECT ?substance ?substanceLabel ?formula ?structure ?CAS
WHERE { 
  ?substance wdt:P31 wd:Q11173.
  ?substance wdt:P231 ?CAS.
  ?substance wdt:P274 ?formula.
  ?substance wdt:P117  ?structure.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 15
"""
            },
            {
            "endpoint":"https://query.wikidata.org/sparql",
            "prefixes": ["http://www.wikidata.org/entity/"],
            "lang": "sparql",
            "name": "CityTop10",
            "title": "Ten largest cities of the world",
            "description": "Wikidata SPARQL query showing the 10 most populated cities of the world using the million city class Q1637706 for selection",
            "query": """# Ten Largest cities of the world 
# WF 2021-08-23
# see also http://wiki.bitplan.com/index.php/PyLoDStorage#Examples
# see also https://github.com/WolfgangFahl/pyLoDStorage/issues/46
SELECT DISTINCT ?city ?cityLabel ?population ?country ?countryLabel 
WHERE {
  VALUES ?cityClass { wd:Q1637706}.
  ?city wdt:P31 ?cityClass .
  ?city wdt:P1082 ?population .
  ?city wdt:P17 ?country .
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
}
ORDER BY DESC(?population)
LIMIT 10"""
            },
            {
            "endpoint":"https://sophox.org/sparql",
            "lang": "sparql",
            "prefixes": [],
            "query":
        """# count osm place type instances
# WF 2021-08-23
# see also http://wiki.bitplan.com/index.php/PyLoDStorage#Examples
# see also https://github.com/WolfgangFahl/pyLoDStorage/issues/46
SELECT (count(?instance) as ?count) ?placeType ?placeTypeLabel
WHERE { 
  VALUES ?placeType {
    "city"
    "town"
    "village"
  }
  ?instance osmt:place ?placeType
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
GROUP BY ?placeType ?placeTypeLabel
ORDER BY ?count""",
        "name": "OSM place types",
        "title": "count OpenStreetMap place type instances",
        "description":"""This SPARQL query 
determines the number of instances available in the OpenStreetMap for the placeTypes city,town and village
"""}]
        for queryMap in queries:
            endpointUrl=queryMap.pop("endpoint")
            endpoint=SPARQL(endpointUrl)
            query=Query(**queryMap)
            query.addFormatCallBack(QueryResultDocumentation.wikiDataLink)  
            showYaml=False
            if showYaml:
                yamlMarkup=query.asYaml()
                print(yamlMarkup)
            try:
                qlod=endpoint.queryAsListOfDicts(query.query)
                for tablefmt in ["mediawiki","github","latex"]:
                    doc=query.documentQueryResult(qlod, tablefmt=tablefmt,floatfmt=".0f")
                    docstr=doc.asText()
                    if show:
                        print (docstr)
                        
            except Exception as ex:
                print(f"{query.title} at {endpointUrl} failed: {ex}")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()