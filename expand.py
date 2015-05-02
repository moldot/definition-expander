import infoclass, defnet, nationality
from maps import all_defs

ontology = infoclass.get_info_ontology()
defnet = defnet.construct(all_defs.keys())

#CORRELATION_THRESHOLD = 100
#WORDS = 2

#def upward_by_infoclass(definition):

    #def related(definition, infobox):
        #"""
        #Determine whether definition is related enough to infobox
        #"""
        #return float(def_to_inf[definition]['infoboxes'][infobox]) / def_to_inf[definition]['count'] > 0.8

    #infoboxes = ontology.infoboxes_under(definition)
    #classes = ontology.classes_under(definition)
    #definitions = set(map(infoclass.InfoOntology.to_phase, classes))

    #print "Infoboxes:", infoboxes

    #for infobox in infoboxes:
        #if not inf_to_def.has_key(infobox):
            #continue
        #for definition in inf_to_def[infobox]['definitions'].items():
            ##print infobox, definition
            #if not nationality.is_demonym(definition[0]) and \
                    #definition[0].count(' ') < WORDS and \
                    #related(definition[0], infobox):
                #definitions.add(definition)

    #return definitions


def upward_by_defnet(definitions):
    definitions = filter(lambda x: not nationality.is_demonym(x), definitions)
    defs = set()
    map(defs.update, map(defnet.inherited_hypernyms_of_def, definitions))
    return map(lambda synset: synset.name(), defs)


def upward_by_infoclass(infoboxes):
    infoboxes = filter(lambda x: not nationality.is_demonym(x), infoboxes)
    classes = set()
    map(classes.update, map(ontology.classes_above_infobox, infoboxes))
    return map(ontology.to_phase, classes)

