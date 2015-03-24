# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 09:17:34 2013

@author: topic
"""
index_dir = 'stories_index'

import os
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh import sorting
import pickle
import json


def main():
    q = raw_input('Enter Event to search:')
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(unicode(q))
        corrected = searcher.correct_query(query,q)
        if corrected.query != query:
            print("Did you mean:", corrected.string)

        results = searcher.search(query, limit=None)
        print results[0]

def escape_aps(text):
    return text.replace("'", "&#39;")


if __name__ == '__main__':
    main()
