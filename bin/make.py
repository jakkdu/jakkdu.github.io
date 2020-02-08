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
        entry['author'] = ', '.join(authors[:-1]) + ', and ' + authors[-1]

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

def make_pub():
    conf_dict, pub_entries = read_bib(md_highlight)
    texts = ['<pre>']

    count = 1
    for entry in pub_entries:
        # Skip non-top-tier paper in web site
        if 'top-tier' in entry and entry['top-tier'] == 'no':
            continue

        conf = conf_dict[entry['crossref']]

        opts = [ ]
        file_id = os.path.join(conf['year'], entry['ID'])
        paper_file = os.path.join('pubs', file_id + '.pdf')
        if os.path.exists(os.path.join(CONTENT_DIR, paper_file)):
            opts.append('[[paper]](%s)' % paper_file)

        slides_file = os.path.join('pubs', file_id + '-slides.pdf')
        if os.path.exists(os.path.join(CONTENT_DIR, slides_file)):
            opts.append('[[slides]](%s)' % slides_file)

        if 'www-git' in entry:
            opts.append('[[code]](%s)' % entry['www-git'])

        texts.append('%d. **%s** %s' % (count, entry['title'], ' '.join(opts)))
        contents = [
                entry['author'],
                conf['title'],
                '%s, %s %s' % (conf['address'], conf['month'], conf['year'])
        ]

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
