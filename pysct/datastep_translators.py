# Copyright © 2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
 
import zipfile
import re

##################################
###### DS Translate         ######
###### DS code translator   ######
##################################

def DS_translate(in_file, 
                in_caslib, in_castable,
                out_caslib, out_castable,
                out_file = "dmcas_scorecode.py", 
                hostname = None):
    """ Writes a .py file, wrapping a simple DataSetp code (not DS2) to be run through `SWAT`. It's used
    for models that outputs the dmcas_scorecode.sas file.
    
    Parameters
    ----------
    in_file : str
        The filepath of the .zip file downloaded through the SAS Viya GUI
    in_caslib : str
        Name of the input table caslib 
    in_castable : str 
        Name of the input table
    out_caslib : str
        Name of the input table caslib
    out_castable  : 
        Name of the input table
    hostname : str
        Name of the hostname. Default: None, will try to guess from file.

    out_file : str
        Name and path of the output file. Default: "dmcas_scorecode.py"
    
    Returns
    -------
    Dict
        A dict with the python score code, out castable, out caslib and the written file path.

    Example 
    -------
    DS_translate("filepath.zip")
    """

## reading score code
    archives = zipfile.ZipFile(in_file, "r")
    rawScore = archives.read("dmcas_scorecode.sas").decode("UTF-8")

    DSScore = "data " + out_caslib + "." + out_castable + ";\n"
    DSScore = DSScore + "    set " + in_caslib + "." + in_castable + ";\n"
    DSScore = DSScore + "\n" + rawScore
    DSScore = DSScore + "\n" + "run;\n"

## writing code header 
    pyscore = """## SWAT package needed to run the codes, below the packages in pip and conda
# documentation: https://github.com/sassoftware/python-swat/
# pip install swat
# conda install -c sas-institute swat
                
import swat
"""

## reading score code hostname
    if (hostname is None):
        first_char = rawScore.find("Host:") + 5
        last_char = rawScore.find(";\n* Encoding:")
        hostname = rawScore[first_char:last_char].strip()

## writing score code
    pyscore += """
conn = swat.CAS(hostname = \"{}\", ## change if needed
                port = 8777,
                protocol='http',  ## change protocol to cas and port to 5570 if using binary connection (unix)
                username='username', ## use your own credentials
                password='password') ## we encorage using .authinfo \n

""".format(hostname)

    pyscore += "out = conn.dataStep.runCode("
    pyscore +=	'code = \"\"\"\n'
    pyscore += DSScore
    pyscore += '\"\"\")\n'

    pyscore += """
### uncomment following lines if you want to drop previous table

#conn.table.dropTable(name = \"{}\",
#					  caslib = \"{}\")

## Uncomment the following to promote a table to all users 
## will fail if there is already a promoted table with the same name

""".format(out_castable, out_caslib)

    pyscore += """
#conn.table.promote(name = \"{}\",
#                   caslib = \"{}\")
                   
""".format(out_castable, out_caslib)
    pyscore += """
## Defining the scored table in Python

scored_table = conn.CASTable(name = \"{}\",
                             caslib = \"{}\")

scored_table.head()
""".format(out_castable, out_caslib)

## saving to file

    f = open(out_file, "wt")
    f.writelines(pyscore)
    f.close()

    print("The file was successfully written to {}".format(out_file))

    return dict({"data_step": DSScore,
                "py_code": pyscore,
                "out_caslib": out_caslib,
                "out_castable": out_castable,
                "out_file": out_file})

##################################
###### EPS Translate        ######
###### DS2 code translator  ######
##################################

def EPS_translate(in_file, 
                in_caslib, in_castable,
                out_caslib, out_castable,
                hostname = "myserver.com",
                out_file = "dmcas_epscorecode.py",
                copyVars = None):

    """Writes a .py file, transforming the DS2 code, extract the astore name and
     create an astore call written using SWAT. The reason for that is because the DS2 is
     not reliable/self contained. It's used for models that outputs the dmcas_epscorecode.sas file.

    Parameters
    ----------
    in_file : str
        The filepath of the .zip file downloaded through the SAS Viya GUI
    in_caslib : str
        Name of the input table caslib 
    in_castable : str 
        Name of the input table
    out_caslib : str
        Name of the input table caslib
    out_castable  : 
        Name of the input table
    out_file : str
        Name and path of the output file. Default: "dmcas_epscorecode.py"
    hostname : str
        sas viya hostname to be used, not available inside the DS2 code
    copyVars : list
        list of column names to copy to output table, if "ALL" will copy all score table data. Default: `None`

    Returns
    -------
    Dict
        A dict with the python score code, out castable, out caslib and the written file path.

    Example 
    -------
    EPS_translate("filepath.zip")

    """

## reading score code
    archives = zipfile.ZipFile(in_file, "r")
    rawScore = archives.read("dmcas_epscorecode.sas").decode("UTF-8")

    astore_name = re.search('_\w+_ast', rawScore).group(0)

    if copyVars == None:
        copyVars_ = "column_names = None\n"
    else:
        if type(copyVars) == str and copyVars == "ALL":
            copyVars_ = """score_table = conn.CASTable(name = in_castable,
                            caslib = in_caslib
                                )

column_names = score_table.columns.tolist()

"""
        else:
            if type(copyVars) == list:
                copyVars_ = 'column_names = {}'.format(copyVars)


## writing code header 
    pyscore = """## SWAT package needed to run the codes, below the packages in pip and conda
# documentation: https://github.com/sassoftware/python-swat/
# pip install swat
# conda install -c sas-institute swat

import swat

"""
## defining variables
    pyscore += """## Defining tables and models variables
in_caslib = \"{}\"
in_castable = \"{}\"
out_caslib = \"{}\"
out_castable = \"{}\"
astore_name = \"{}\"
astore_file_name = \"{}\"

""".format(in_caslib, in_castable, out_caslib, out_castable, astore_name, astore_name + ".sashdat")

## writing connection
    pyscore += """## Connecting to SAS Viya
conn = swat.CAS(hostname = \"{}\", ## change if needed
                port = 8777,
                protocol='http',  ## change protocol to cas and port to 5570 if using binary connection (unix)
                username='username', ## use your own credentials
                password='password') ## we encorage using .authinfo \n

""".format(hostname)

## writing model call
    pyscore += """## Loading model to memory
## assuming the model is already inside the viya server
conn.table.loadTable(caslib= "Models",
                      path = astore_file_name, #case sensitive
                      casOut = {"name": astore_name,
                                "caslib": "Models"}
                                )

"""
    ## writing column names code
    pyscore += copyVars_ + "\n"

    ## writing astore
    pyscore +="""## loading astore actionset and scoring
conn.loadActionSet("astore")

conn.astore.score(table = {"caslib": in_caslib, "name": in_castable},
                   out = {"caslib": out_caslib, "name": out_castable, "replace": True},
                   copyVars = column_names,
                   rstore = {"name": astore_name, "caslib": "Models"}
              )

## Obtaining output/results table
scored_table = conn.CASTable(name = out_castable,
                              caslib = out_caslib)
                              
scored_table.head()

"""
    ## saving to file

    f = open(out_file, "wt")
    f.writelines(pyscore)
    f.close()

    print("The file was successfully written to {}".format(out_file))

    return dict({"ds2_raw": rawScore,
                "py_code": pyscore,
                "out_caslib": out_caslib,
                "out_castable": out_castable,
                "out_file": out_file})