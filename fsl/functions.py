'''
fsl: plugin for the wordfish python package
functions for extracting region names from standard anatomical 
atlases.

In the future we can have a wordfish-data plugin to work with the image
data itself. For now, just the terms.

'''
from wordfish.utils import get_json, has_internet_connectivity
from wordfish.standards.xml.functions import read_xml_url

# IMPORTS FOR ALL PLUGINS
from wordfish.corpus import save_sentences
from wordfish.terms import save_terms
from wordfish.terms import save_relations
from wordfish.plugin import generate_job

# REQUIRED WORDFISH FUNCTION
def go_fish():    
    generate_job(func="extract_terms",category="terms")

def extract_terms(output_dir):

    if has_internet_connectivity():    
       terms = dict()
       atlases = get_json("http://neurovault.org/api/atlases/?format=json")
       for atlas in atlases:
           label_description_file = "http://neurovault.org/media/images/291/Talairach-labels-2mm.xml"
           print "Parsing %s" %(label_description_file)
           xml_dict = read_xml_url(label_description_file)
           atlas_name = xml_dict["atlas"]["header"]["name"]
           atlas_name_label = atlas_name.replace(" ","_").lower()
           atlas_labels = xml_dict["atlas"]["data"]["label"]
           for l in range(len(atlas_labels)):
               label = atlas_labels[l]
               # We will use coordinate for unique ID
               unique_id = "%s_%s" %(atlas_name_label,l)
               terms[unique_id] = {"name":label["#text"],
                                   "x":label["@x"],
                                   "y":label["@y"],
                                   "z":label["@z"]}

       save_terms(terms,output_dir=output_dir)

    else:
       print "Cannot define fsl atlas terms, no internet connectivity."

    
def get_atlas_xml():
    # If > 100 atlases, we would need to get pagination pages here.
    return get_json("http://neurovault.org/api/atlases/?format=json")["results"]
