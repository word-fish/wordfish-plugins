# Plugins

** under development **

These are plugins that can generate corpus or terminology for use with [wordfish python](http://www.github.com/vsoch/wordfish-python). Each plugin should have its own folder. Plugin requirements are determined from the config.json, and deployed to user-specific applications with these modules installed. Plugins can have two use cases, and for each would include the following functions.

 - extract_terms: function to call to return a data structure of terms
 - extract_text: function to call to return a data structure of text
 - functions.py: is the file in the plugin folder to store these functions


### Format
The structure of a plugin is as follows:

      plugin
            functions.py
            __init__.py
            config.json


The minimum requirement for a new plugin functions.py is as follows:

      '''
      functions.py
      '''
      def extract_text(output_dir):
          return None
      def extract_terms(output_dir=None):
          return None
      def extract_relationships(output_dir=None)
          return None

#### Extract Text (from corpus)
Should do whatever functions you need to obtain your text, and any additional python modules you need should be defined in the config.json "dependencies" --> "python" section (see below). Currently, you should obtain user input interactively, or set as a default argument, and in the future we will implement a way to obtain these values from the user who is generating the application. Your function should prepare either a dictionary (in the case of having a unique ID you want to maintain) or a list (if you don't have unique ids). For example, if we are parsing something from pubmed, our script might prepare the following data structure:


     {"12345":"This is text from article 1 with pubmed id 12345",
      "12346":"This is text from article 2 with pubmed id 12346",
     }

In the case that you don't have any unique ids, just put your text objects into a list:

    ["This is text from article 1 with no id.",ou
    "This is text from article 2 with no id."]


The last line of your function should pass either the dictionary or list to the save_sentences function:

    
    # Save articles to text files in output folder     
    from wordfish.corpus import save_sentences
    save_sentences(corpus_input,output_dir=output_dir)

The output_dir comes from the higher level script running it, so just make sure to pass it along.

#### Extract terms
Your extract terms function should give the user an option to extract terms with relationships, or not. The simplest implementation will send a list of strings to the `save_terms` function:


      from wordfish.terms import save_terms
      save_terms(terms,output_dir=output_dir,extract_relationships=False)

The structure that is returned is a simple json that defines nodes:


        {"nodes":[{"name":"node1"},
                 {"name":"node2"}]
        }

Why does this make sense? Because that can go immediately into any javascript or d3, and it's a commonly used way to render a graph.


Again, the output file is passed from the script generating it, don't worry about it. This will save a terms.json in the terms output folder for your plugin. 

#### Extract relationships
Lots of these ontology things have relationships between terms, and so if you have some relationships that you want to define, whether a numerical value or a string that represents some kind of semantic relationship, you can. If this is the case, you should define a function called `extract_relationships` in your functions.py, and define set variable "relationships" in your config.json to True. Since relationship extraction could take a long time, we run these functions on the slurm cluster. The only thing you need to worry about is the function itself. It should take as input the same argument as `extract_terms` and within it, call the function `save_relationships` with a relationships variable that is a list of tuples that describe [(source,target,relationship)]. For example, in functions.py, within `extract_relationships`:

       from wordfish.terms import save_relationships
       relationships = [("node1","node2",0.5),("node1","node2","purl.ontology.org#isPartOf")]
       save_relationships(terms,output_dir=output_dir,relationships=relationships)

We will generate a slurm job to do this, so the user does not have to wait.


The structure that is returned is a simple json that defines links:


        {
         "links": [{"source":"node1","target":"node2","value":0.5}]
        }


For all of the above, the functions in functions.py and the config.json, don't worry about remembering all this, we give you a starter template to fill in.



#### Best Practices

- You should generally print to the screen what is going on, and how long it might take, as a courtesy to the user, if something needs review or debugging.

      "Extracting relationships, will take approximately 3 minutes"

- If you need a github repo, we have a function for that:

      from wordfish.vm import download_repo
      repo_directory = download_repo(repo_url="https://github.com/neurosynth/neurosynth-data")

- If you need a general temporary place to put things, use `tempfile`

      tmpdir = tempfile.mkdtemp()


### Config.json
Plugins will be understood by the application by way of the config.json. For example:


      [
            {
              "name": "NeuroSynth Database",
              "tag": "neurosynth",
              "corpus": "True",
              "terms": "True",
              "dependencies": {
                                "python": [ 
                                            "neurosynth",
                                            "pandas"
                                          
                                          ],
                                 "plugins": ["pubmed"]
                              },
              "arguments": {
                               "corpus":"email"
                           },
              "contributors": ["Vanessa Sochat"], 
              "doi": "10.1038/nmeth.1635",
    
            }
      ]

 - name: should be a human readable description of the plugin
 - tag: should be a term (no spaces or special characters) that corresponds with the folder name in the plugins directory. 
 - corpus/terms: boolean, each "True" or "False" should indicate if the plugin can return a corpus (text to be parsed by deepdive) or terms (a vocabulary to be used to find mentions of things.)
 - dependencies: should include "python" and "plugins." Python corresponds to python packages that are dependencies. "plugins" refers to other plugins that are required.
 - arguments: should be a dictionary with (optionally) corpus and/or terms. The user will be asked for these arguments to run the `extract_text` and `extract_terms` functions.
 - contributors: should be a name/orcid ID or email of researchers responsible for creation of the plugins. This is for future help and debugging.
 - doi: should be a reference or publication associated with the resource.


### Validation
Plugins will be validated and loaded by [wordfish-python](http://www.github.com/vsoch/deepdive-python). Plugins will be validated with tests that ensure that output is as is expected for use with wordfish-python. When generating an application, the user will be given choice to use only the valid plugins. Validation means that they pass some set of tests to return an expected output. Validation also means availability and successful installation of extra dependencies - any plugin that fails installation will not be included, and this is a good idea so that many plugins don't complicate the install process.

For some plugins, user arguments will be required, and these arguments will all be determined by the "arguments" variable, asked for at time of application generation.

Full documentation on adding plugins will be provided.