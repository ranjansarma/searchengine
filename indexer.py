from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.index import exists_in
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import *
import os
import pickle
import sys

index_dir = 'stories_index'
extracted_dir = "extracted_docs/"


def main():
    try:
        os.mkdir(index_dir)
    except OSError:
        print '%s is already exists' % index_dir
    if exists_in(index_dir):
        choise = raw_input(
            'Previous Index Found\nOptions:\n1.Create new Index\n2.Incremental Indexing\nEnter your option:')
        if choise == '1':
            index_my_docs(index_dir, True)
        elif choise == '2':
            index_my_docs(index_dir)
            ch = raw_input('Do you want to optimize the index?(y/n):')
            if ch == 'y':
                print 'Optimizing.Please wait...'
                optimize_index()
                print 'Optimizing Completed'
        else:
            print 'Wrong Option.Exiting....'
            sys.exit(0)
    else:
        print 'No previous index found. Creating new....'
        index_my_docs(index_dir, True)
    print 'Indexing Completed!'


def create_schema():
    """
    Function to create schema for the index to be created
    """
    schema = Schema(path=ID(stored=True), content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                    link=TEXT(stored=True), title=TEXT(stored=True))
    return schema


def get_link_files():
    """
    Function to get the list of path of all the file to index

    :return: list of path
    """
    base_dir = os.path.abspath('.') + '/' + extracted_dir
    link_files = []
    print os.listdir(base_dir)
    for f in os.listdir(base_dir):
        link_files.append(base_dir + f)
    return link_files


def optimize_index(dir=index_dir):
    """
    Function to optimize the index i.e merges all the different segment of index created during incremental
    index creation
    :param dir:
    """
    ix = open_dir(dir)
    ix.optimize()


def index_my_docs(dirname, clean=False):
    if clean:
        clean_index(dirname)
    else:
        incremental_index(dirname)


def incremental_index(dirname):
    """
    Function to add new documents to a previously existed index
    :param dirname: path of the index directory
    """
    ix = open_dir(dirname)
    # The set of all paths in the index
    indexed_paths = set()
    with ix.searcher() as searcher:
        writer = ix.writer()

        # Loop over the stored fields in the index
        for fields in searcher.all_stored_fields():
            indexed_path = fields['path']
            indexed_paths.add(indexed_path)

        # Loop over the files in the filesystem
        for path in get_link_files():
            if path not in indexed_paths:
                print 'File addng to index: ', path
                add_doc(writer, path)
        print 'Committing :::'
        writer.commit()


def clean_index(dirname):
    """
    Function to create index from scratch
    :param dirname: path of the index_dir
    """
    ix = create_in(dirname, schema=create_schema())
    writer = ix.writer()
    link_files = get_link_files()
    for path in link_files:
        add_doc(writer, path)
    print 'Committing :::'
    writer.commit()


def add_doc(writer, path):
    """
    Function to add documents to the index
    :param writer: the index writer
    :param path: path of the file to add to index
    """
    print 'Opening ', path
    try:
        f_link = open(path, 'rb')
        stories_file = pickle.load(f_link)
        f_link.close()
    except IOError:
        print 'Unable to read %s file' % path
    else:
        try:
            writer.add_document(path=unicode(path), content=unicode(stories_file['content']), link=unicode('url'),
                                title=unicode(stories_file['title']))
        except Exception, e:
            print e


if __name__ == "__main__":
    main()
