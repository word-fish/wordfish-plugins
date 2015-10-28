# Plugins

** under development **

These are plugins that can generate corpus or terminology for use with [deepdive python](http://www.github.com/vsoch/deepdive-python). Each plugin should have its own folder. Plugin requirements are determined from the config.json, and deployed to user-specific applications with these modules installed. Plugins can have two use cases, and for each would include the following functions.

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
      def extract_text():
          return None
      def extract_terms():
          return None


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
Plugins will be validated and loaded by [deepdive-python](http://www.github.com/vsoch/deepdive-python). Plugins will be validated with tests that ensure that output is as is expected for use with deepdive-python. When generating an application, the user will be given choice to use only the valid plugins. Validation means that they pass some set of tests to return an expected output. Validation also means availability and successful installation of extra dependencies - any plugin that fails installation will not be included, and this is a good idea so that many plugins don't complicate the install process.

For some plugins, user arguments will be required, and these arguments will all be determined by the "arguments" variable, asked for at time of application generation.

Full documentation on adding plugins will be provided.
