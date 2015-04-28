demonyms = []

for line in open('maps/nationalities.txt', 'r'):
    demonyms.append(line.split('" ')[0][1:].lower())

demonyms = frozenset(demonyms)

def is_demonym(word):
    return word in demonyms
