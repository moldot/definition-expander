from infoclass import *
from nationality import *
from maps import *

ontology = get_class_ontology()

CORRELATION_THRESHOLD = 100
WORDS = 2

def class_to_def(wiki_class):
    str = re.sub('(.*:_*)', '', wiki_class)
    str = re.sub('([a-z])([A-Z])', r'\1 \2', str)
    str = re.sub('([A-Z])([A-Z][a-z])', r'\1 \2', str)
    return str.lower()


def look_ontology(ontology):
    #print ontology['class'] + ' | ' + class_to_def(ontology['class'])
    print ontology['class'], ontology['infoboxes']
    for child in ontology['children']:
        look_ontology(child)

look_ontology(ontology)

def expand_by_infobox(definition):
    
    def search(ontology, definition, found=False):
        if class_to_def(ontology['class']) == definition or found:
            found = True
            definitions = [class_to_def(ontology['class'])]
            infoboxes = ontology['infoboxes']
        else:
            definitions = []
            infoboxes = []
        for child in ontology['children']:
             result = search(child, definition, found)
             definitions += result[0]
             infoboxes += result[1]
        return definitions, infoboxes

    def related(definition, infobox):
        """
        Determine whether definition is related enough to infobox
        """

        return float(def_to_inf[definition]['infoboxes'][infobox]) / def_to_inf[definition]['count'] > 0.8

    definitions, infoboxes = search(ontology, definition)
    definitions = set(definitions)

    print "Infoboxes:", infoboxes

    for infobox in infoboxes:
        if not inf_to_def.has_key(infobox):
            continue
        for definition in inf_to_def[infobox]['definitions'].items():
            #print infobox, definition
            if not is_demonym(definition[0]) and definition[0].count(' ') < WORDS and \
                    related(definition[0], infobox): 
                definitions.add(definition)

    return definitions


def expand_by_wordnet(definition):
    pass

