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


def get_class_ontology(from_cache=True):
    """
    Return a recursive dictionary that represent ontology of
    wikipedia classes and their infoboxes

    format:
    {
        'class': class_name:str
        'parent': its parent class pointer:dict
        'children': list of children:list of dict
        'infoboxes': list of infoboxes:list of str
    }
    """

    cache_path = HTML_CACHE_PATH_PREFIX + 'ontology-classes.html'

    if from_cache:
        page = open(cache_path, 'r').read()
    else:
        page = get_page_and_store(ONTOLOGY_URL, cache_path)

    class OntologyHTMLParser(HTMLParser):
        def __init__(self, infoclass, ontology):
            HTMLParser.__init__(self)
            self.pointer = ontology
            self.newClass = ontology
            self.infoclass = infoclass
        
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'ul':
                self.pointer = self.newClass
            elif tag == 'a' and attrs.has_key('name') and attrs['name'] != 'owl:Thing':
                self.newClass = {
                        'class': attrs['name'],
                        'parent': self.pointer,
                        'children': [],
                        'infoboxes': map(lambda x: x[0], filter(lambda x: x[1] == attrs['name'], self.infoclass))
                }
                self.pointer['children'].append(self.newClass)

        def handle_endtag(self, tag):    
            if tag == 'ul':
                if self.pointer != None: self.pointer = self.pointer['parent']

        def handle_data(self, data):
            pass
        
    
    ontology = {
            'class': 'owl:Thing',
            'parent': None,
            'children': [],
            'infoboxes': []
    }
    
    infoclass = get_infobox_class_pairs(True)
    
    OntologyHTMLParser(infoclass, ontology).feed(page)

    return ontology

if __name__ == '__main__':
    pairs = get_infobox_class_pairs();
    ontology = get_class_ontology(True)
