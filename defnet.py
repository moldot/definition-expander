from nltk.corpus import wordnet as wn

class Defnet:
    def __init__(self):
        self.defnet = {}
        self.defnet[wn.synset('entity.n.01')] = {
                'hypernyms': set(),
                'children': set()
        }

    def new_def(self, definition):
        map(lambda synset: self.add(synset, definition), wn.synsets(definition, pos=wn.NOUN))

    def add(self, parent, child):
        if self.defnet.has_key(parent):
            self.defnet[parent]['children'].add(child)
        else:
            self.defnet[parent] = {
                    'hypernyms': set(parent.hypernyms()),
                    'children': set([child])
            }
            map(lambda synset: self.add(synset, parent), parent.hypernyms())

    def print_tree(self, root=wn.synset('entity.n.01'), indent=''):
        if type(root) == str: return
        print indent + str(root) + ' ' + str(self.defs_at(root))
        map(lambda synset: self.print_tree(root=synset, indent=indent+'    '), self.hyponyms_at(root))

    def defs_at(self, node):
        try:
            return set(filter(lambda child: type(child) is str, self.defnet[node]['children']))
        except KeyError:
            return set()

    def hyponyms_at(self, node):
        try:
            return set(filter(lambda child: True or type(child) is not str, self.defnet[node]['children']))
        except KeyError:
            return set()

    def expand_def(self, definition, full_sentence=None): # in the future, might use full sentence to get word sense
        defs = set()
        map(defs.update, map(self.defs_under, wn.synsets(definition, pos=wn.NOUN)))
        return defs

    def defs_under(self, node):
        defs = self.defs_at(node)
        map(defs.update, map(self.defs_under, self.hyponyms_at(node)))
        return defs


def construct(definitions):
    defnet = Defnet()
    map(defnet.new_def, definitions)
    return defnet
