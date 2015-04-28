import urllib2
import re
from wikiscout import infobox_parser
from HTMLParser import HTMLParser

MAPPINGS_URLS = [
    'http://mappings.dbpedia.org/index.php?title=Special:AllPages&namespace=204&from=1930s-UK-film-stub&to=Infobox_darts_player',
    'http://mappings.dbpedia.org/index.php?title=Special:AllPages&namespace=204&from=Infobox_diocese&to=US-child-writer-stub',
    'http://mappings.dbpedia.org/index.php?title=Special:AllPages&namespace=204&from=US-company-stub&to=Year_dab'
]

ONTOLOGY_URL = "http://mappings.dbpedia.org/server/ontology/classes/"

URL_PREFIX = 'http://mappings.dbpedia.org/'
HTML_CACHE_PATH_PREFIX = 'dbpedia/'

def get_page_and_store(url, cache_path=None):
    """
    Fetch a html page from url and store in store_path
    """
    page = urllib2.urlopen(url).read()

    if cache_path is not None:
        open(cache_path, 'w').write(page)

    return page


def get_infobox_urls(mapping_page):
    """
    Return list of urls of infobox pages
    """
    pattern = re.compile('index\.php/Mapping_en:Infobox_[-\w\./]+')
    return pattern.findall(mapping_page)


def get_class(infobox_page):
    """
    Return class of the infobox, given the HTML DBpedia infobox_page

    class is in CamelCase (possibly with colon and space), exactly as appear in the infobox_page
    """
    pattern = re.compile('OntologyClass:[-\w: ]+')
    wiki_class = pattern.findall(infobox_page)

    if len(wiki_class) == 0:
        return None
    else:
        return wiki_class[0].replace('OntologyClass:', '')


def get_infobox_class_pairs(from_cache=True):
    """
    Return pairs of (infobox, class)

    infobox format is lower case with hyphen (e.g. 'afl-player-2')
    class format is as returbed by get_class.
    """
    infobox_urls = []
    infobox_class_pairs = []
    
    for i, mapping_url in enumerate(MAPPINGS_URLS):
        cache_path = HTML_CACHE_PATH_PREFIX + 'main_mapping_en_' + str(i+1) + '.html'
        
        if from_cache:
            mapping_page = open(cache_path, 'r').read()
        else:
            mapping_page = get_page_and_store(mapping_url, cache_path)

        infobox_urls += get_infobox_urls(mapping_page)
    
    for i, infobox_url in enumerate(infobox_urls):
        full_url = URL_PREFIX + infobox_url
        infobox = infobox_parser.get_class(infobox_url.split(':')[1]).replace('wikipedia-', '')
        cache_path = HTML_CACHE_PATH_PREFIX + 'infobox-' + infobox + '.html'

        #print '(%d/%d) %s' % (i+1, len(infobox_urls), infobox)
        
        if from_cache:
            infobox_page = open(cache_path, 'r').read()
        else:
            infobox_page = get_page_and_store(URL_PREFIX + infobox_url, cache_path)

        infobox_class_pairs.append((infobox, get_class(infobox_page)))

    return infobox_class_pairs

class InfoOntology():
    def __init__(self):
        self.ontology = {}
        self.root = 'owl:Thing'
        self.ontology[self.root] = {
                'parent': self.root,
                'subclasses': [],
                'infoboxes': []
        }
        self.phase_to_class = {InfoOntology.to_phase(self.root): self.root}

    def parent(self, wiki_class):
        return self.ontology[wiki_class]['parent']

    def subclasses_of(self, wiki_class):
        """
        Return a list of subclasses of wiki_class node.

        wiki_class may be in CamelCase or space-delimited lowercase string
        that can be mapped to a class

        return an empty list if wiki_class does not exist
        """
        wiki_class = self.phase_to_class.get(wiki_class, wiki_class)
        try:
            return self.ontology[wiki_class]['subclasses']
        except KeyError:
            return []

    def infoboxes_of(self, wiki_class):
        """
        Return a list of infoboxes of wiki_class node.

        wiki_class may be in CamelCase or space-delimited lowercase string
        that can be mapped to a class

        return an empty list if wiki_class does not exist
        """
        wiki_class = self.phase_to_class.get(wiki_class, wiki_class)
        try:
            return self.ontology[wiki_class]['infoboxes']
        except KeyError:
            return []

    def classes_under(self, wiki_class):
        """
        Return a list of all classes under wiki_class subtree.

        wiki_class may be in CamelCase or space-delimited lowercase string
        that can be mapped to a class

        return an empty list if wiki_class does not exist
        """
        wiki_class = self.phase_to_class.get(wiki_class, wiki_class)
        try:
            return [wiki_class] + \
                    reduce(list.__add__, map(self.classes_under, self.subclasses_of(wiki_class)), [])
        except KeyError:
            return []

    def infoboxes_under(self, wiki_class):
        """
        Return a list of all infoboxes under wiki_class subtree.

        wiki_class may be in CamelCase or space-delimited lowercase string
        that can be mapped to a class

        return an empty list of wiki_class does not exist
        """
        wiki_class = self.phase_to_class.get(wiki_class, wiki_class)
        try:
            return self.ontology[wiki_class]['infoboxes'] + \
                    reduce(list.__add__, map(self.infoboxes_under, self.subclasses_of(wiki_class)) ,[])
        except KeyError:
            return []

    def print_tree(self, wiki_class, indent=''):
        print indent + wiki_class + ' ' + str(self.infoboxes_of(wiki_class))
        map(lambda subclass: self.print_tree(subclass, indent+'    '), self.subclasses_of(wiki_class))

    @staticmethod
    def to_phase(wiki_class):
        """
        Return space-delimited lowercase string given CamelCase wiki class
        """
        if wiki_class == 'foaf:Person': 
            return 'person (foaf)' # special class, conflint with Person class

        str = re.sub('(.*:_*)', '', wiki_class)
        str = re.sub('([a-z])([A-Z])', r'\1 \2', str)
        str = re.sub('([A-Z])([A-Z][a-z])', r'\1 \2', str)
        return str.lower()


    def add_class(self, wiki_class, parent, subclasses=[], infoboxes=[]):
        if self.ontology.has_key(wiki_class):
            raise ValueError('Class already exists')
        self.ontology[wiki_class] = {
                'parent': parent,
                'subclasses': subclasses[:],
                'infoboxes': infoboxes[:]
        }
        self.phase_to_class[InfoOntology.to_phase(wiki_class)] = wiki_class

    def add_subclass(self, wiki_class, subclass):
        if subclass in self.ontology[wiki_class]['subclasses']:
            return
        self.ontology[wiki_class]['subclasses'].append(subclass)

    def add_infobox(self, wiki_class, infobox):
        if infobox in self.ontology[wiki_class]['infoboxes']:
            return
        self.ontology[wiki_class]['infoboxes'].append(infobox)


def get_info_ontology(from_cache=True):
    """
    Return an InfoOntology instance that represents ontology of
    wikipedia classes and their infoboxes
    """
    cache_path = HTML_CACHE_PATH_PREFIX + 'ontology-classes.html'

    if from_cache:
        page = open(cache_path, 'r').read()
    else:
        page = get_page_and_store(ONTOLOGY_URL, cache_path)

    class OntologyHTMLParser(HTMLParser):
        def __init__(self, infoclass, ontology):
            HTMLParser.__init__(self)
            self.ontology = ontology
            self.current = ontology.root
            self.last_subclass = ontology.root
            self.infoclass = infoclass
        
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'ul':
                self.current = self.last_subclass
            elif tag == 'a' and attrs.has_key('name') and attrs['name'] != 'owl:Thing':
                self.ontology.add_class(attrs['name'], self.current, 
                        infoboxes=map(lambda x: x[0], filter(lambda x: x[1] == attrs['name'], self.infoclass)))
                self.ontology.add_subclass(self.current, attrs['name'])
                self.last_subclass = attrs['name']

        def handle_endtag(self, tag):    
            if tag == 'ul':
                self.current = self.ontology.parent(self.current)

    infoclass = get_infobox_class_pairs(True)
    ontology = InfoOntology()
    OntologyHTMLParser(infoclass, ontology).feed(page)

    return ontology

if __name__ == '__main__':
    pairs = get_infobox_class_pairs();
    ontology = get_info_ontology(True)
