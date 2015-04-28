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
        except: KeyError:
            return set()

    def defs_under(self, definition, full_sentence=None):a # in the future, might use full sentence to get word sense
        synsets = wn.synsets(definition, pos=wn.NOUN)





def construct(definitions):
    defnet = Defnet()
    map(defnet.new_def, definitions)
    return defnet

defnet = construct(['village', 'municipality', 'settlement', 'city', 'community', 'township', 'province'])
defnet.print_tree()
