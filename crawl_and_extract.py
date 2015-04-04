import os
import urllib2
import cookielib
import zlib
import socket
import time
import bs4
import pickle

document_dir = "html_docs/"                 # Directory of the html files
extracted_dir = "extracted_docs/"           # Directory of the pickle files after parsing the corresponding html files

import os


def main():
    crawl()
    extract()


def crawl():
    try:
        os.mkdir(document_dir)
    except OSError:
        print "Directory already exists !"
    browser = Browser()
    article_id = 1
    print "Crawling the links ..."
    with open("links.txt", 'r') as links_file:
        for link in links_file:
            link = link.strip()
            print 'Opening link %s ...' % link
            html_page = browser.get_html(link)
            if type(html_page) == 'dict':
                with open('error.txt', 'w') as error_file:
                    error_file.write(link)
            f = open(document_dir + str(article_id) + '.html', 'w')
            f.write(html_page)
            f.close()
            article_id += 1


def extract():
    temp_dict = dict()
    try:
        os.mkdir(extracted_dir)
    except OSError:
        print extracted_dir + ' already exists'
    for file in os.listdir(document_dir):
        with open(document_dir + file, 'r') as html_file:
            html = html_file.read()
            extractor = StoryExtractor(html)
            temp_dict['title'] = extractor.get_title()
            temp_dict['content'] = extractor.get_story_content()
            temp_dict['url'] = extractor.get_url()

            f = open(extracted_dir + file.split('.')[0] + '.pkl', 'w')
            pickle.dump(temp_dict, f)
            f.close()



class Browser:
    def __init__(self, newbrowser=None):
        """
        It initializes the Cookies  and modify user agent
        """
        # Initialize Cookies
        CHandler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.newbrowser = urllib2.build_opener(CHandler)
        self.newbrowser.addheaders = [
            ('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')]
        urllib2.install_opener(self.newbrowser)
        self.error_dict = {}  # to be returned by get_html if any thing goes wrong

    def get_html(self, link):
        """ Get html content of the link passed as argument """
        print 'opening  ' + link
        try:
            res = self.newbrowser.open(link)
            if res.headers.getheader('Content-Encoding') == 'gzip':
                data = zlib.decompress(res.read(),
                                       16 + zlib.MAX_WBITS)  # decompress to normal html if server returns content in 'gziped' form
            else:
                data = res.read()
            return data

        except urllib2.HTTPError as e:
            self.error_dict['e_code'] = e.code
            self.error_dict['e_reason'] = e.reason
            print 'HTTPError in link=%s' % link
            return self.error_dict

        except urllib2.URLError:
            self.error_dict['e_code'] = 404
            self.error_dict['e_reason'] = 'URLError'
            print 'UrlError in link=%s' % link
            return self.error_dict

        except socket.timeout:
            time.sleep(60 * 2)  # wait
            self.error_dict['e_code'] = 408
            self.error_dict['e_reason'] = 'SocketTimeOut'
            print 'SocketTimeout Error in link=%s' % link
            return self.error_dict


class StoryExtractor:
    """
    Class for parsing the html document and extract the desired contents from the html source
    For this tutorial this class is parsing news articles selected for REUTERS' archives and its specific to it.
    """
    def __init__(self, html):
        """ Takes the html page of story and intializes the soup for it """
        self.soup = bs4.BeautifulSoup(html)

    def get_story_content(self):
        article = ''
        content_block = self.soup.find('span', attrs={'id':'articleText'})
        story = content_block.findAll('p')
        if story is None:
            return "None"
        else:
            for paragraph in story:
                s = paragraph.get_text().strip()
                s = s.encode('ascii', 'ignore')
                article += ' ' + s.replace('\n', ' ')
            return article

    def get_url(self):
        meta_url = self.soup.find('meta', attrs={'property': 'og:url'})
        if meta_url is None:
            return "None"
        else:
            return meta_url.get('content').strip().encode('ascii', 'ignore')

    def get_title(self):
        meta_title = self.soup.find('meta', attrs={'property': 'og:title'})
        if meta_title is None:
            return "None"
        else:
            return meta_title.get('content').strip().encode('ascii', 'ignore')



if __name__ == "__main__":
    main()
