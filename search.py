index_dir = 'stories_index'


from whoosh.index import open_dir
from whoosh.qparser import QueryParser


def main():
    q = raw_input('Enter Event to search:')
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(unicode(q))
        results = searcher.search(query, limit=None)
        for res in results:
            print 'title : ',  res['title']


if __name__ == '__main__':
    main()
