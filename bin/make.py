#!/usr/bin/env python3
import sys
import os
import bibtexparser
from bibtexparser.bparser import BibTexParser

ROOT = os.path.join(os.path.dirname(__file__), "..")

sys.path.append(os.path.join(ROOT, "./lib/biblib"))

PUB_BIB = os.path.join(ROOT, "pub.bib")
CONF_BIB = os.path.join(ROOT, "conf.bib")
CONTENT_DIR = os.path.join(ROOT, "content")

HOME_MD = os.path.join(ROOT, "home.md")
NEWS_MD = os.path.join(ROOT, "news.md")
AWARD_MD = os.path.join(ROOT, "award.md")

NEWS_NUM = 8
MY_NAME = 'Insu Yun'

def md_highlight(s):
    return '**%s**' % s

def authors_to_string(authors):
    if len(authors) == 1:
        return authors[0] # e.g., thesis
    else:
        return ', '.join(authors[:-1]) + ', and ' + authors[-1]

def purify_bib_entry(entry, highlight):
    for k, v in entry.items():
        entry[k] = v.strip().lstrip('{').rstrip('}')

    if 'author' in entry:
        # Change author1 and author2 and author3
        # -> author, author2, and author3
        # and highlight my name
        authors = entry['author'].split(' and ')
        index = authors.index(MY_NAME)
        assert(index != -1)
        authors[index] = highlight(authors[index])
        entry['author'] = authors_to_string(authors)

        if entry['ID'] == 'cui:rept':
            entry['author'] += ' (alphabetical)'
    return entry

def replace_text(text, key, content):
    tag = '{{ %s }}' % key
    assert(tag in text)
    return text.replace(tag, content)

def read_bib(highlight):
    conf_dict = {}
    parser = BibTexParser(common_strings=True)
    conf_entries = bibtexparser.load(open(CONF_BIB), parser).entries
    for entry in conf_entries:
        # Add year to its nick
        title = entry['title']
        assert(title.endswith(')'))
        entry['title'] = title[:-1] + ' ' + entry['year'] + title[-1:]
        conf_dict[entry['ID']] = entry

    parser = BibTexParser(common_strings=True)
    pub_entries = bibtexparser.load(open(PUB_BIB), parser).entries

    for i, entry in enumerate(pub_entries):
        pub_entries[i] = purify_bib_entry(entry, highlight)

    return conf_dict, pub_entries

def get_location(entry):
    if 'address' in entry:
        return entry['address']
    elif 'school' in entry:
        return entry['school'] # for thesis
    raise ValueError('Unexpected format')

def make_pub():
    conf_dict, pub_entries = read_bib(md_highlight)
    texts = ['<pre>']

    count = 1
    for entry in pub_entries:
        if 'crossref' in entry:
            metadata = conf_dict[entry['crossref']]
        else:
            metadata = entry

        opts = [ ]
        file_id = os.path.join(metadata['year'], entry['ID'])
        paper_file = os.path.join('pubs', file_id + '.pdf')
        if os.path.exists(os.path.join(CONTENT_DIR, paper_file)):
            opts.append('[[paper]](%s)' % paper_file)

        slides_file = os.path.join('pubs', file_id + '-slides.pdf')
        if os.path.exists(os.path.join(CONTENT_DIR, slides_file)):
            opts.append('[[slides]](%s)' % slides_file)

        if 'www-git' in entry:
            opts.append('[[code]](%s)' % entry['www-git'])

        if 'www-url' in entry:
            opts.append('[[web]](%s)' % entry['www-url'])

        texts.append('%d. **%s** %s' % (count, entry['title'], ' '.join(opts)))

        loc = get_location(metadata)

        contents = [entry['author']]
        if 'booktitle' in metadata:
            contents.append(metadata['booktitle'])
        elif entry['ENTRYTYPE'] == 'phdthesis':
            contents.append('Ph.D. thesis')
        contents.append('%s, %s %s' % (loc, metadata['month'], metadata['year']))

        if 'award' in entry:
            contents.append('** * %s **' % entry['award'])

        for content in contents:
            texts.append('    ' + content)

        count += 1

    texts += ['</pre>']
    return '\n'.join(texts)

def make_news():
    # TODO: Support folding
    lines = open(NEWS_MD).read().splitlines()[:NEWS_NUM]
    lines[0] = '**%s**' % lines[0]
    lines = list(map(lambda l: '- %s' % l, lines))
    return '\n'.join(lines)

def make_award():
    # TODO: Support folding
    lines = open(AWARD_MD).read().splitlines()

    for i, l in enumerate(lines):
        # Highlight title
        items = l.split(', ')
        items[0] = '%d. **%s**' % (i + 1, items[0])
        lines[i] = ', '.join(items)
    return '\n'.join(lines)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s output_path' % sys.argv[0])
        sys.exit(-1)

    with open(HOME_MD) as f:
        txt = f.read()
        txt = replace_text(txt, 'NEWS', make_news())
        txt = replace_text(txt, 'PUB', make_pub())
        txt = replace_text(txt, 'AWARD', make_award())

    with open(sys.argv[1], 'w') as f:
        f.write(txt)
