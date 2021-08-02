# Copyright © 2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import zipfile
import re

##################################
### NLP Translate             ####
### sentiment code translator ####
##################################

def nlp_sentiment_translate(
                            in_file,
                            key_column, # ID column 
                            document_column, # Text variable column
                            in_caslib, in_castable,
                            out_caslib, out_castable_sentiment, 
                            hostname = None,
                            out_castable_matches = None, 
                            out_castable_features = None,
                            out_file = "SentimentScoreCode.py"
):
    """It will read the score code that is written as SAS Code extract the language and hostame, 
       then write a python code equivalent using the `SWAT` package.
    
    Parameters
    ----------
    in_file : str
        The filepath of the .zip file downloaded through the SAS Viya GUI
    in_caslib : str
        Name of the input table caslib 
    in_castable : str 
        Name of the input table
    out_caslib : str
        Name of the output table caslib
    out_castable_sentiment  : 
        sentiment output table name
    out_castable_matches  : 
        matches output table name, if the argument is not defined the table name will be the same as `out_castable_sentiment` with "_matches" added
    out_castable_features  : 
        features output table name, if the argument is not defined the table name will be the same as `out_castable_sentiment` with "_features" added   
    key_column  : 
        Key column name for unique identifier
    document_column  : 
        text variable column name           

    out_file : str
        Name and path of the output file. Default: "SentimentScoreCode.py"
    
    Returns
    -------
    Dict
        A dict with the python score code, out castable, out caslib and the written file path.
    Example 
    -------
    nlp_sentiment_translate("filepath.zip")
    """

## reading score code
    if out_castable_sentiment is None:
        raise Exception("out_castable_sentiment must be defined.")
    if out_castable_matches is None:
        out_castable_matches = out_castable_sentiment + "_matches"
    if out_castable_features is None:
        out_castable_features = out_castable_sentiment + "_features"

    if in_file is None:
        raise Exception("Read file must be specified")



    archives = zipfile.ZipFile(in_file, "r")
    rawScore = archives.read("ScoreCode.sas").decode("UTF-8")

### getting hostname
    if hostname is None:
        hostname = re.search('(?<=%let cas_server_hostname = ")(.*)(?=";)', rawScore).group(0)

## getting language
    language = re.search('(?<=%let language = ")(.*)(?=";)', rawScore).group(0)

## writing code header 
    pyscore = """## SWAT package needed to run the codes, below the packages in pip and conda
# documentation: https://github.com/sassoftware/python-swat/
# pip install swat
# conda install -c sas-institute swat \n
import swat \n
"""

###### writing score code

## defining variables
    pyscore += """## Defining tables and models variables\n

in_caslib = \"{}\"
in_castable = \"{}\"
out_caslib = \"{}\"
out_castable_sentiment = \"{}\"
out_castable_matches = \"{}\"
out_castable_features = \"{}\"
key_column = \"{}\"
document_column = \"{}\"
language = \"{}\" \n
""".format(in_caslib, in_castable, out_caslib, 
            out_castable_sentiment, out_castable_matches,
            out_castable_features, key_column, \
            document_column, language
            )

## Writting connection

    pyscore += """## Connecting to SAS Viya \n
conn = swat.CAS(hostname = \"{}\", ## change if needed
                port = 8777,
                protocol='http',  ## change protocol to cas and port to 5570 if using binary connection (unix)
                username='username', ## use your own credentials
                password='password') ## we encorage using .authinfo \n

""".format(hostname)

## score Code apply sent

    pyscore += """## loading sentimentAnalysis actionset and scoring"
conn.loadActionSet("sentimentAnalysis") \n
conn.sentimentAnalysis.applySent(
        table = {"name": in_castable, "caslib": in_caslib},
        docId = key_column,
        text = document_column,
        language = language,
        casOut = {"caslib": out_caslib, "name": out_castable_sentiment, "replace": True},
        matchOut = {"caslib": out_caslib, "name": out_castable_matches, "replace": True},
        featureOut = {"caslib": out_caslib, "name": out_castable_features, "replace": True}
    )\n
    """

## reading output table


    pyscore += """## Defining the scored cas table in Python (output)\n

scored_sentiment_table = conn.CASTable(name = \"{}\",
                             caslib = \"{}\")
\n
scored_sentiment_table.head()
""".format(out_castable_sentiment, out_caslib)

## saving to file

    f = open(out_file, "wt")
    f.writelines(pyscore)
    f.close()

    print("The file was successfully written to {}".format(out_file))

    return dict({
                "out_file": out_file,
                "py_code": pyscore,
                "out_caslib": out_caslib,
                "out_castable_sentiment": out_castable_sentiment,
                "out_castable_matches": out_castable_matches,
                "out_castable_features": out_castable_features
    })



##################################
### NLP Translate             ####
### category code translator ####
##################################


### TO DO
### AN Alternative version can be made using ASTORE actionset to upload to different environments
###

def nlp_category_translate(
                            in_file,
                            key_column, # ID column 
                            document_column, # Text variable column
                            in_caslib, in_castable,
                            out_caslib, out_castable_category, 
                            hostname = None,
                            out_castable_matches = None, 
                            out_castable_modeling_table = None,
                            out_file = "CategoryScoreCode.py"
):

    """It will read the score code that is written as SAS Code extract the mco binary and hostame information, 
       then write a python code equivalent using the `SWAT` package.
    
    Parameters
    ----------
    in_file : str
        The filepath of the .zip file downloaded through the SAS Viya GUI
    in_caslib : str
        Name of the input table caslib 
    in_castable : str 
        Name of the input table
    out_caslib : str
        Name of the output table caslib
    out_castable_category  : 
        category output table name
    out_castable_matches  : 
        matches output table name, if the argument is not defined the table name will be the same as `out_castable_category` with "_matches" added
    out_castable_modeling_table  : 
        modeling ready output table name, if the argument is not defined the table name will be the same as `out_castable_category` with "_modeling" added   
    key_column  : 
        Key column name for unique identifier
    document_column  : 
        text variable column name           

    out_file : str
        Name and path of the output file. Default: "CategoryScoreCode.py"
    
    Returns
    -------
    Dict
        A dict with the python score code, out castable, out caslib and the written file path.
    Example 
    -------
    nlp_category_translate("filepath.zip")
    """

## reading score code
    if out_castable_category is None:
        raise Exception("out_castable_category must be defined.")
    if out_castable_matches is None:
        out_castable_matches = out_castable_category + "_matches"
    if out_castable_modeling_table is None:
        out_castable_modeling_table = out_castable_category + "_modeling"

    if in_file is None:
        raise Exception("Read file must be specified")

    archives = zipfile.ZipFile(in_file, "r")
    rawScore = archives.read("ScoreCode.sas").decode("UTF-8")

### getting hostname
    if hostname is None:
        hostname = re.search('(?<=%let cas_server_hostname = ")(.*)(?=";)', rawScore).group(0)

## getting binaries/astore path
    mco_binary_caslib = re.search('(?<=%let mco_binary_caslib = ")(.*)(?=";)', rawScore).group(0)
    mco_binary_table_name = re.search('(?<=%let mco_binary_table_name = ")(.*)(?=";)', rawScore).group(0)

## writing code header 
    pyscore = """## SWAT package needed to run the codes, below the packages in pip and conda
# documentation: https://github.com/sassoftware/python-swat/
# pip install swat
# conda install -c sas-institute swat \n
import swat \n
"""

###### writing score code

## defining variables
    pyscore += """## Defining tables and models variables\n

in_caslib = \"{}\"
in_castable = \"{}\"
out_caslib = \"{}\"
out_castable_category = \"{}\"
out_castable_matches = \"{}\"
out_castable_modeling = \"{}\"
key_column = \"{}\"
document_column = \"{}\"
mco_binary_caslib = \"{}\"
mco_binary_table_name = \"{}\"\n
""".format(in_caslib, in_castable, out_caslib, 
            out_castable_category, out_castable_matches,
            out_castable_modeling_table, key_column, 
            document_column, mco_binary_caslib,
            mco_binary_table_name
            )

## Writing connection

    pyscore += """## Connecting to SAS Viya \n
conn = swat.CAS(hostname = \"{}\", ## change if needed
                port = 8777,
                protocol='http',  ## change protocol to cas and port to 5570 if using binary connection (unix)
                username='username', ## use your own credentials
                password='password') ## we encorage using .authinfo \n

""".format(hostname)

## score Code apply textRuleScore

    pyscore += """## loading textRuleScore actionset and scoring\n
conn.loadActionSet("textRuleScore") \n
conn.textRuleScore.applyCategory(
        model = {"caslib": mco_binary_caslib, "name": mco_binary_table_name},
        table = {"name": in_castable, "caslib": in_caslib},
        docId = key_column,
        text = document_column,
        casOut = {"caslib": out_caslib, "name": out_castable_category, "replace": True},
        matchOut = {"caslib": out_caslib, "name": out_castable_matches, "replace": True},
        modelOut = {"caslib": out_caslib, "name": out_castable_modeling, "replace": True}
    )\n
    
    """

## reading output table

    pyscore += """
## Defining the scored cas table in Python (output)\n

scored_category_table = conn.CASTable(name = \"{}\",
                             caslib = \"{}\")\n
scored_category_table.head()
""".format(out_castable_category, out_caslib)

## saving to file

    f = open(out_file, "wt")
    f.writelines(pyscore)
    f.close()

    print("The file was successfully written to {}".format(out_file))

    return dict({
                "out_file": out_file,
                "py_code": pyscore,
                "out_caslib": out_caslib,
                "out_castable_sentiment": out_castable_category,
                "out_castable_matches": out_castable_matches,
                "out_castable_modeling": out_castable_modeling_table
    })

##################################
######## DONE UP TO HERE #########
##################################


##################################
### NLP Translate             ####
### topics code translator    ####
##################################

### TO DO
### AN Alternative version can be made using ASTORE actionset to upload to different environments
###

def nlp_topics_translate(
                            in_file,
                            in_caslib, in_castable,
                            out_caslib, out_castable, 
                            hostname = None,
                            copyVars = None,
                            out_file = "topicsScoreCode.py"
):

    """This function the score code that is written as SAS Code extract the astore and hostame information, 
       then write a python code equivalent using the `SWAT` package.
    
    Parameters
    ----------
    in_file : str
        The filepath of the .zip file downloaded through the SAS Viya GUI
    in_caslib : str
        Name of the input table caslib 
    in_castable : str 
        Name of the input table
    out_caslib : str
        Name of the output table caslib
    out_castable  : 
        topics output table name
    out_file : str
        Name and path of the output file. Default: "topicsScoreCode.py"
    copyVars : list
        list of column names to copy to output table, if "ALL" will copy all score table data. Default: `None`
        
    Returns
    -------
    Dict
        A dict with the python score code, out castable, out caslib and the written file path.
        
    Example 
    -------
    nlp_topics_translate("filepath.zip")
    """

## reading score code

    if in_file is None:
        raise Exception("Read file must be specified")

    archives = zipfile.ZipFile(in_file, "r")
    rawScore = archives.read("AstoreScoreCode.sas").decode("UTF-8")

### getting hostname
    if hostname is None:
        hostname = re.search('(?<=%let cas_server_hostname = ")(.*)(?=";)', rawScore).group(0)

## getting language
    astore_caslib = re.search('(?<=%let input_astore_caslib_name = ")(.*)(?=";)', rawScore).group(0)
    astore_table_name = re.search('(?<=%let input_astore_name = ")(.*)(?=";)', rawScore).group(0)

## writing code header 
    pyscore = """## SWAT package needed to run the codes, below the packages in pip and conda
# documentation: https://github.com/sassoftware/python-swat/
# pip install swat
# conda install -c sas-institute swat \n
import swat \n
"""

###### writing score code

## creating copyVars acording to the input
    if type(copyVars) is list:
        pass
    elif (type(copyVars) is str):
        copyVars = [copyVars]
    else:
        Exception("copyVars must be a list, \"ALL\" or None")    
        

    if copyVars is None:
        copyVars_ = "column_names = None\n"

    if copyVars is not None:
        if (len(copyVars) == 1) and (copyVars[0] == "ALL"):
            copyVars_ = """## Defining scoring table obtaining column names"\n
score_table = conn.CASTable(name = in_castable,
                                caslib = in_caslib)\n
column_names = score_table.columns.tolist()\n
"""

        elif (len(copyVars) >= 1):
            copyVars_ = """## Defining scoring table obtaining column names"\n
column_names = {} \n
""".format(copyVars)

## defining variables
    pyscore += """## Defining tables and models variables\n

in_caslib = \"{}\"
in_castable = \"{}\"
out_caslib = \"{}\"
out_castable = \"{}\"
astore_caslib = \"{}\"
astore_table_name = \"{}\"\n
""".format(in_caslib, in_castable, out_caslib, 
            out_castable, astore_caslib,
            astore_table_name
            )

## Writing connection

    pyscore += """## Connecting to SAS Viya \n
conn = swat.CAS(hostname = \"{}\", ## change if needed
                port = 8777,
                protocol='http',  ## change protocol to cas and port to 5570 if using binary connection (unix)
                username='username', ## use your own credentials
                password='password') ## we encorage using .authinfo \n
""".format(hostname)

### Loading astore table into memory (astore should already be inside server)
    pyscore +="""## If Uploading model to a new server uncomment this section and add correct filepath\n
#conn.table.loadTable(caslib = "Models",
#path = "/path/to/TopicsModel.astore", ## case sensitive
#casout = {"name": astore_table_name,
#          "caslib": "Models"}) ## change caslib as well if needed\n
"""

## copyVars will define castable to get column names if needed
    pyscore += copyVars_

## score action

    pyscore += """## loading actionset actionset and scoring\n
conn.loadActionSet("astore") \n

## The input table column names must be the equal as the training table\n
conn.astore.score(
        table = {"name": in_castable, "caslib": in_caslib},
        casOut = {"caslib": out_caslib, "name": out_castable, "replace": True},
        copyVars = column_names,
        rstore = {"caslib": astore_caslib, "name": astore_table_name} ## if you uploaded manually, change may be needed
    )\n
    
    """

## reading output table

    pyscore += """
## Defining the scored cas table in Python (output)\n

scored_topics_table = conn.CASTable(name = \"{}\",
                             caslib = \"{}\")\n
scored_topics_table.head()
""".format(out_castable, out_caslib)

## saving to file

    f = open(out_file, "wt")
    f.writelines(pyscore)
    f.close()

    print("The file was successfully written to {}".format(out_file))

    return dict({
                "out_file": out_file,
                "py_code": pyscore,
                "out_caslib": out_caslib,
                "out_castable": out_castable
    })

##################################
### NLP Translate             ####
### Concepts code translator  ####
##################################

### TO DO
### AN Alternative version can be made using ASTORE actionset to upload to different environments
###

def nlp_concepts_translate(
                            in_file,
                            key_column, # ID column 
                            document_column, # Text variable column
                            in_caslib, in_castable,
                            out_caslib, out_castable_concepts, 
                            hostname = None,
                            out_castable_facts = None, 
                            out_file = "conceptsScoreCode.py"
):

    """It will read the score code that is written as SAS Code extract the mco binary and hostame information, 
       then write a python code equivalent using the `SWAT` package.
    
    Parameters
    ----------
    in_file : str
        The filepath of the .zip file downloaded through the SAS Viya GUI
    in_caslib : str
        Name of the input table caslib 
    in_castable : str 
        Name of the input table
    out_caslib : str
        Name of the output table caslib
    out_castable_concepts  : 
        concepts output table name
    out_castable_facts  : 
        matches output table name, if the argument is not defined the table name will be the same as `out_castable_concepts` with "_facts" added
    key_column  : 
        Key column name for unique identifier
    document_column  : 
        text variable column name           

    out_file : str
        Name and path of the output file. Default: "conceptsScoreCode.py"
    
    Returns
    -------
    Dict
        A dict with the python score code, out castable, out caslib and the written file path.
    Example 
    -------
    nlp_concepts_translate("filepath.zip")
    """

## reading score code
    if out_castable_concepts is None:
        raise Exception("out_castable_concepts must be defined.")
    if out_castable_facts is None:
        out_castable_facts = out_castable_concepts + "_facts"

    if in_file is None:
        raise Exception("Read file must be specified")

    archives = zipfile.ZipFile(in_file, "r")
    rawScore = archives.read("ScoreCode.sas").decode("UTF-8")

### getting hostname
    if hostname is None:
        hostname = re.search('(?<=%let cas_server_hostname = ")(.*)(?=";)', rawScore).group(0)

## getting binaries/astore path
    liti_binary_caslib = re.search('(?<=%let liti_binary_caslib = ")(.*)(?=";)', rawScore).group(0)
    liti_binary_table_name = re.search('(?<=%let liti_binary_table_name = ")(.*)(?=";)', rawScore).group(0)

## writing code header 
    pyscore = """## SWAT package needed to run the codes, below the packages in pip and conda
# documentation: https://github.com/sassoftware/python-swat/
# pip install swat
# conda install -c sas-institute swat \n
import swat \n
"""

###### writing score code

## defining variables
    pyscore += """## Defining tables and models variables\n

in_caslib = \"{}\"
in_castable = \"{}\"
out_caslib = \"{}\"
out_castable_concepts = \"{}\"
out_castable_facts = \"{}\"
key_column = \"{}\"
document_column = \"{}\"
liti_binary_caslib = \"{}\"
liti_binary_table_name = \"{}\"\n
""".format(in_caslib, in_castable, out_caslib, 
            out_castable_concepts, out_castable_facts,
            key_column, document_column, 
            liti_binary_caslib,
            liti_binary_table_name
            )

## Writing connection

    pyscore += """## Connecting to SAS Viya \n
conn = swat.CAS(hostname = \"{}\", ## change if needed
                port = 8777,
                protocol='http',  ## change protocol to cas and port to 5570 if using binary connection (unix)
                username='username', ## use your own credentials
                password='password') ## we encorage using .authinfo \n

""".format(hostname)

## score Code apply textRuleScore

    pyscore += """## loading textRuleScore actionset and scoring\n
conn.loadActionSet("textRuleScore") \n
conn.textRuleScore.applyConcept(
        model = {"caslib": liti_binary_caslib, "name": liti_binary_table_name},
        table = {"name": in_castable, "caslib": in_caslib},
        docId = key_column,
        text = document_column,
        casOut = {"caslib": out_caslib, "name": out_castable_concepts, "replace": True},
        factOut = {"caslib": out_caslib, "name": out_castable_facts, "replace": True}
    )\n
    
    """

## reading output table

    pyscore += """
## Defining the scored cas table in Python (output)\n

scored_concepts_table = conn.CASTable(name = \"{}\",
                             caslib = \"{}\")\n
scored_concepts_table.head()
""".format(out_castable_concepts, out_caslib)

## saving to file

    f = open(out_file, "wt")
    f.writelines(pyscore)
    f.close()

    print("The file was successfully written to {}".format(out_file))

    return dict({
                "out_file": out_file,
                "py_code": pyscore,
                "out_caslib": out_caslib,
                "out_castable_sentiment": out_castable_concepts,
                "out_castable_facts": out_castable_facts
    })