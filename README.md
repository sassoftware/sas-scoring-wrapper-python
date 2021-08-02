pysct - SAS Scoring Code Translator for Python
================

# Overview

This package was made to facilitate the translation of scoring codes
which SAS outputs from its interfaces, specially Model Studio and Visual
Text Analytics. The functions will wrap an DS/DS2 code or make
equivalent call using the `SWAT` package and SAS Viya API. The output is
a Python code, ready or almost ready to use in any other application, as a
good starting point for integration.

## What can be translated

This package will translate (or wrap) some Scoring Codes that are export
through some of Viya interfaces. All the output R codes are based on the
[Python SWAT](https://github.com/sassoftware/python-swat/) package. It’s not
necessary for this package translation to run, but is necessary to run
the output code.

The following table will help you to know which function to user for
which kind of code:

-   **Interface**: Where you can obtain the sas generated score code
    (not the only place)

-   **Code Type**: The code type expected by the translator

-   **Base File Name**: The file which the translator will read from
    inside the exported zip File. You can also use that to identify which kind of
    code it is. (dataStep is usually called `dmcas_scorecode.sas` and
    DS2 `dmcas_epscorecode.sas`)

-   **Translation Function**: Name of the function to translate it
    properly

-   **Output Type**: The way the R code is going to be translated to be
    used outside of the SAS environment

-   **Sample File**: Sample of the usual name that is exported by the SAS visual interfaces


| Interface             | Code Type                  | Base File Name         | Translation Function        | Output Type                                                             | Sample File                          |
|:----------------------|:---------------------------|:-----------------------|:----------------------------|:------------------------------------------------------------------------|:-------------------------------------|
| Model Studio          | DataStep                   | dmcas\_scorecode.sas   | `pysct.DS_translate()`            | Python code that calls a DataStep using `dataStep` actionset                 | score\_code\_Logistic Regression.zip |
| Model Studio          | DS2                        | dmcas\_epscorecode.sas | `pysct.EPS_translate()`           | Python code that calls `astore` actionSet instead of calling the DS2 wrapper  | score\_code\_Gradient Boosting.zip   |
| Visual Text Analytics | Sentiment - CAS Procedure  | scoreCode.sas          | `pysct.nlp_sentiment_translate()` | Python code that calls the `sentimentAnalysis` actionset                     | SentimentScoreCode.zip               |
| Visual Text Analytics | Categories - CAS Procedure | scoreCode.sas          | `pysct.nlp_category_translate()`  | Python code that calls `textRuleScore` actionset with `applyCategory` action | CategoriesScoreCode.zip              |
| Visual Text Analytics | Topics - CAS Procedure     | AstoreScoreCode.sas    | `pysct.nlp_topics_translate()`    | Python code that calls `astore` actionSet                                    | TopicsScoreCode.zip                  |
| Visual Text Analytics | Concepts - CAS Procedure   | ScoreCode.sas          | `pysct.nlp_concepts_translate()`  | Python code that calls `textRuleScore` actionset with `applyConcept` action  | ConceptsScoreCode.zip                |

## Installing

``` python
# Since it's not on Pipy, you will to install from git using pip:
pip install git+https://github.com/sassoftware/sas-scoring-translator-python.git

# loading the package
import pysct
```

## Running 

For this example here we've used the `hmeq` dataset available in SAS support [examples datasets](https://support.sas.com/documentation/onlinedoc/viya/examples.htm). You can use this data to generate a model in SAS Model Studio (Gradient Boosting) and export to do this first example, you don't have to unzip the code, but opening it to know which type was exporte may be useful. 


``` python
## For models that generates DS2 code such as Gradient Boosting

## it will show the place where the file was written to


out = pysct.EPS_translate(
            in_file = "/path/to/score_code_Forest.zip",    
            out_caslib = "casuser",
            out_castable = "hmeq",
            in_caslib = "public",
            in_castable = "hmeq",
            out_file="dmcas_scorecode.py"
)

out.keys()

```

    The file was successfully written to dmcas_scorecode.py

    dict_keys(['data_step', 'py_code', 'out_caslib', 'out_castable', 'out_file'])



And here is a sample of the generated code, as you will see, credentials
and servers may be needed to be tweaked manually, other than that, it’s
fully operational:

``` python
## SWAT package needed to run the codes, below the packages in pip and conda
# documentation: https://github.com/sassoftware/python-swat/
# pip install swat
# conda install -c sas-institute swat

import swat

## Defining tables and models variables
in_caslib = "public"
in_castable = "hmeq"
out_caslib = "casuser"
out_castable = "hmeq"
astore_name = "_6ZIHG08DFQVM4TBXHX2XEDAY4_ast"
astore_file_name = "_6ZIHG08DFQVM4TBXHX2XEDAY4_ast.sashdat"

## Connecting to SAS Viya
conn = swat.CAS(hostname = "sasserver.com", ## change if needed
                port = 8777,
                protocol='http',  ## change protocol to cas and port to 5570 if using binary connection (unix)
                username='username', ## use your own credentials
                password='password') ## we encorage using .authinfo \n

## Loading model to memory
## assuming the model is already inside the viya server
conn.table.loadTable(caslib= "Models",
                      path = astore_file_name, #case sensitive
                      casOut = {"name": astore_name,
                                "caslib": "Models"}
                                )

column_names = None

## loading astore actionset and scoring
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

```

Each of the functions follows similar structure but have some different
variables to have consistant naming, due to that, reference the
documentation of the one you want to use to know more about minimun
specifications (Using Python helper function: `help(pysct.nlp_sentiment_translate())`).

``` r
## For models that generates simple DataStep code such as Logistic Regression or Decision Trees

out = pysct.DS_translate(
                in_file = "/path/to/score_code_Stepwise Logistic Regression.zip",    
                out_caslib = "casuser",
                out_castable = "hmeq",
                in_caslib = "public",
                in_castable = "hmeq"
)

## For models that generates astores code such as Forest and Gradient Boosting

out2 = pysct.EPS_translate(
            in_file = "/path/to/score_code_Forest.zip",    
            out_caslib = "casuser",
            out_castable = "hmeq",
            in_caslib = "public",
            in_castable = "hmeq",
            copyVars="ALL",
            out_file="forest_test2.py"
)

## For Sentiment model generated from VTA
sentSc = pysct.nlp_sentiment_translate(
                in_file= "/path/to/SentimentScoreCode.zip",
                key_column= "ID",
                document_column= "text",
                in_caslib= "public",
                in_castable= "reports",
                out_caslib= "public",
                out_castable_sentiment= "reports_sentiment"
)


## For Category model generated from VTA

catSc = pysct.nlp_category_translate(
            in_file = "/path/to/CategoriesScoreCode.zip",
            key_column = "ID",
            document_column = "text",
            in_castable= "reports",
            in_caslib = "public",
            out_caslib= "public",
            out_castable_category="reports_nlp_cats"
)


## For topic model generated from VTA

topSc = pysct.nlp_topics_translate(
            in_file= "/path/to/TopicsScoreCode.zip",
            in_caslib= "Public",
            in_castable= "reports",
            out_caslib= "public",
            out_castable= "reports_topics"
)

## For concepts model generated from VTA

conceptSc = pysct.nlp_concepts_translate(
                in_file = "/path/to/ConceptsScoreCode.zip",
                key_column = "ID",
                document_column = "text",
                in_castable= "repots",
                in_caslib = "public",
                out_caslib= "public",
                out_castable_concepts="reports_nlp_con"
)
```

## Troubleshooting

Most of the work here assumes that the code is going to be used in the
same server that the model was generated, therefore, not needing to upload astores binaries. Some codes generates the uploading code, but it is not fully implemented yet.

## Contributing

We welcome your contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit contributions to this project.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

## Additional Resources

 - A similar library is available for [R](https://github.com/sassoftware/sas-scoring-translator-r)
 
 - SAS Communities Post (coming soon)
