# Create your tests here.
"""

    used for unit test of the project, based on the django framework

"""
from django.test import TestCase

from app01.models import PDFContent, TotalKeyPhrases
from app01.worker import getKeyPhraseByTitle, getKeyPhraseByURL, getHotPDFList, getPDFListByKeyPhrase, \
    getHotKeyPhraseList


def createPDFContent():
    title = 'The Stanford CoreNLP Natural Language Processing Toolkit'
    url = 'https://www.aclweb.org/anthology/P14-5010.pdf'
    keyPhrasesStr = "[('annotators', 0.03843168585021394), ('stanford corenlp toolkit', 0.019823544019182036)] "
    PDFContent.objects.create(title=title, url=url, keyPhrase=keyPhrasesStr)


# test /search/
class ViewTestsSearch(TestCase):

    def test_search_by_url_invalid(self):
        """
        search by an invalid url, the response html file should be the search page
        """
        url_invalid = 'The Stanford CoreNLP Natural Language Processing Toolkit'
        response = self.client.post('/search/', {'type': 'URL', 'url_pdf': url_invalid})
        self.assertContains(response.content, 'key-phrase-search')

    def test_search_by_url_new(self):
        """
        search by the url of pdf, if succeed, the return html file should contain the url
        """
        url_new = 'https://www.aclweb.org/anthology/P14-5010.pdf'
        title = 'The Stanford CoreNLP Natural Language Processing Toolkit'
        response = self.client.post('search/', {'type': 'URL', 'url_pdf': url_new})
        #self.assertEqual(PDFContent.objects.get(url=url_new).title, title)
        self.assertContains(response.content, url_new)

    def test_search_by_url_exsiting(self):
        """
        search by an exsiting url of pdf, if succeed, the num should be 2+1
        """
        createPDFContent()
        url = 'https://www.aclweb.org/anthology/P14-5010.pdf'
        response = self.client.post('/search/', {'type': 'URL', 'url_pdf': url})
        self.assertEqual(PDFContent.objects.get(url=url).num, 2)
        self.assertContains(response.content, url)

    def test_search_by_title(self):
        """
        search by the title of pdf, if succeed, the return html file should contain the title, the num should be 3
        """
        createPDFContent()
        title = 'The Stanford CoreNLP Natural Language Processing Toolkit'
        response = self.client.post('/search/', {'type': 'Title', 'url_pdf': title})
        self.assertEqual(PDFContent.objects.get(title=title).num, 2)
        self.assertContains(response.content, title)

    def test_search_by_title_invalid(self):
        """
        search by the title of pdf, if succeed, the return html file should contain the title
        """
        title = '111'
        response = self.client.post('/search/', {'type': 'Title', 'url_pdf': title})
        self.assertContains(response.content, 'key-phrase-search')


# test /keyPhraseList/
class ViewTestsKeyPhraseList(TestCase):

    def test_keyPhrase_list(self):
        response = self.client.get('/keyPhraseList/')
        self.assertEqual(response.status_code, 200)


# test /searchPage/
class ViewTestsSearchPage(TestCase):

    def test_searchPage(self):
        response = self.client.get('/searchPage/', follow=True)
        self.assertEqual(response.status_code, 200)


# test /indexPage/
class ViewTestsIndexPage(TestCase):

    def test_click_to_return(self):
        """
        get to index.html by url homepage
        """
        response = self.client.get('/homepage/')
        self.assertEqual(response.status_code, 200)

    def test_the_index_page(self):
        """
        get to index.html by url /
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


# test /pdfListByKeyPhrase/
class ViewTestsPdfListByKeyPhrase(TestCase):

    def test_pdf_list_by_keyPhrase(self):
        TotalKeyPhrases.objects.create(content='annotators', frequency=4.0, titles=';;The Stanford CoreNLP Natural '
                                                                                   'Language Processing Toolkit')
        response = self.client.get('/pdfListByKeyPhrase/', {'keyPhrase': 'annotators'})
        self.assertEqual(response.status_code, 200)


class ModelTestsPDFContent(TestCase):

    def test_getByFields(self):
        """
        get the record of PDF in db and check if the record exists or not
        """
        createPDFContent()
        title = 'The Stanford CoreNLP Natural Language Processing Toolkit'
        url = 'https://www.aclweb.org/anthology/P14-5010.pdf'
        p = PDFContent()
        tmp = p.getByFields(field='title', content=title)
        self.assertEqual(tmp.get('url'), url)

    def test_getHotPDFList(self):
        """
        get the top hot PDF in the db, the limit is the number
        """
        title = 'The Stanford CoreNLP Natural Language Processing Toolkit'
        url = 'https://www.aclweb.org/anthology/P14-5010.pdf'
        createPDFContent()
        p = PDFContent()
        pdfs = p.getHotPDFList(10)
        self.assertEqual(pdfs[0].get('url'), url)
        self.assertEqual(pdfs[0].get('title'), title)


class ModelTestsTotalKeyPhrases(TestCase):

    def test_getPDFListByKeyPhrase(self):
        """
        get the titles of pdf with certain keyPhrase, compare the length and title
        """
        TotalKeyPhrases.objects.create(content='0.4', frequency=4.0, titles=';;0.1;;0.2;;0.3')
        tmp = TotalKeyPhrases().getPDFListByKeyPhrase('0.4')
        self.assertEqual(len(tmp), 4)
        self.assertEqual(tmp[2], '0.2')
        self.assertEqual(tmp[0], '')

    def test_updateNewPDF(self):
        """
        update db when the Pdf is new
        """
        TotalKeyPhrases.objects.create(content='0.5', frequency=5.0, titles='0.5')
        TotalKeyPhrases.objects.create(content='0.6', frequency=6.0, titles='0.5')
        keyPhrases = [('0.5', 5.0), ('0.6', 6.0)]
        TotalKeyPhrases().updateNewPDF(keyPhrases, '0.7')
        self.assertEqual(TotalKeyPhrases.objects.get(content='0.5').frequency, 10.0)
        self.assertEqual(TotalKeyPhrases.objects.get(content='0.5').titles, '0.5;;0.7')
        self.assertEqual(TotalKeyPhrases.objects.get(content='0.6').frequency, 12.0)

    def test_getHotKeyPhraseList(self):
        """
        get the top10 hot PDF in the db
        :return: [KeyPhrase]
        """
        TotalKeyPhrases.objects.create(content='0.7', frequency=0.7, titles='0.5')
        TotalKeyPhrases.objects.create(content='0.8', frequency=0.8, titles='0.5')
        keyPhraseList = TotalKeyPhrases().getHotKeyPhraseList(10)
        self.assertEqual(keyPhraseList[0].get('content'), '0.8')

    def test_getAll(self):
        """
        get all the KeyPhrases, compare the numbers
        """
        TotalKeyPhrases.objects.create(content='0.7', frequency=0.7, titles='0.5')
        TotalKeyPhrases.objects.create(content='0.8', frequency=0.8, titles='0.5')
        # search all the db
        tmp = TotalKeyPhrases().getAll()
        # process all the keyPhrase
        self.assertEqual(len(tmp), 2)


class Tests_worker(TestCase):

    def test_getKeyPhraseByURL(self):
        """
        search keyPhrase by the url and return the required information
        """
        # the url already exsits
        url1 = 'https://www.aclweb.org/anthology/P14-5010.pdf'
        p1 = getKeyPhraseByURL(url1)
        self.assertEqual(p1.get('result'), True)

        # the url does not exsits
        url2 = 'https://arxiv.org/pdf/1702.01923.pdf'
        p2 = getKeyPhraseByURL(url2)
        self.assertEqual(p2.get('result'), True)

    def test_getKeyPhraseByTitle(self):
        """
        search the db to find keyPhrase by the title and return the required information
        """
        # search the db
        createPDFContent()
        title = 'The Stanford CoreNLP Natural Language Processing Toolkit'
        url = 'https://www.aclweb.org/anthology/P14-5010.pdf'
        getKeyPhraseByURL(url)
        p = getKeyPhraseByTitle(title)
        self.assertEqual(p.get('url'), url)
        self.assertEqual(p.get('result'), True)

    def test_getHotPDFList(self):
        """
        get the top hot PDF in the db, we have 2, so the return should be 2
        """
        createPDFContent()
        pdfs = getHotPDFList()
        self.assertEqual(len(pdfs), 1)

    def test_getPDFListByKeyPhrase(self):
        """
        get pdf with certain keyPhrase
        """
        TotalKeyPhrases.objects.create(content='0.4', frequency=4.0, titles=';;0.1;;0.2;;0.3')
        PDFContent.objects.create()
        PDFContent.objects.create(title='0.1', url='url',
                                  keyPhrase="[('annotators', 0.03843168585021394), ('stanford corenlp toolkit', "
                                            "0.019823544019182036)]")
        PDFContent.objects.create(title='0.2', url='url',
                                  keyPhrase="[('annotators', 0.03843168585021394), ('stanford corenlp toolkit', "
                                            "0.019823544019182036)]")
        PDFContent.objects.create(title='0.3', url='url',
                                  keyPhrase="[('annotators', 0.03843168585021394), ('stanford corenlp toolkit', "
                                            "0.019823544019182036)]")

        titles = getPDFListByKeyPhrase('0.4')
        self.assertEqual(len(titles), 3)

    def test_getHotKeyPhraseList(self):
        """
        get the top10 hot PDF in the db
        """
        TotalKeyPhrases.objects.create(content='0.4', frequency=4.0, titles=';;0.1;;0.2;;0.3')
        keyPhraseList = getHotKeyPhraseList()
        self.assertEqual(keyPhraseList[0].get('content'), '0.4')
