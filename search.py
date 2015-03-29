index_dir = 'stories_index'


from whoosh.index import open_dir
from whoosh.qparser import QueryParser


def main():
    q = raw_input('Enter Event to search:')
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(unicode(q))
        corrected = searcher.correct_query(query,q)
        if corrected.query != query:
            print("Did you mean:", corrected.string)

        results = searcher.search(query, limit=None)
        for res in results:
            print 'title : ',  res['title']

def escape_aps(text):
    return text.replace("'", "&#39;")


if __name__ == '__main__':
    main()
