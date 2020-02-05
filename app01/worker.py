# Import libraries
import ssl
import urllib
import logging
import pdf2image
import pke
import pytesseract
from pyecharts.charts import WordCloud

from app01.models import PDFContent, TotalKeyPhrases

ssl._create_default_https_context = ssl._create_unverified_context
logger = logging.getLogger(__name__)
MAX_NUM = 20
KEY_PHRASE_NUM = 50


def processContent(text):
    """
    process the output text of OCR, find the title
    :param text: the output text of OCR
    :return: {'title': title,
            'text': text
            }
    """
    logger.debug("Process the output text of OCR, find the title")
    title = ''
    for i in text.splitlines():
        if i == '':
            break
        else:
            title += i
    text = text.lower()
    # Process the lines
    text = ' '.join(text.split('\n'))
    text = text.replace('- ', '')
    return {'title': title,
            'text': text
            }


def generateWoldCloud(keyPhrases):
    """
    generate the word cloud to make the key-phrases visual

    :param keyPhrases:  in format of [(content, frequency),...)]
    :return: WordCloud
    """
    logger.debug("Start to generate the WoldCloud")
    myWordCloud = WordCloud()
    myWordCloud.add('', keyPhrases, shape='circle')
    return myWordCloud


def getKeyPhraseByTitle(title):
    """
    search the db to find keyPhrase by the title and return the required information
    :param title: the title of pdf
    :return: {
            "wordCloud": wordCloud,
            "title": title,
            'url': url,
            'result': 'T' or 'F'
            'message': if F
            }
    """
    logger.debug("Start to get KeyPhrase By Title")
    # search the db
    pdfContent = PDFContent()
    p = pdfContent.getByFields(field='title', content=title)
    # if the title exsits
    if p.get('result'):
        wordCloud = generateWoldCloud(p.get('keyPhrases'))
        p['wordCloud'] = wordCloud.render_embed()
    # if not exists
    else:
        logger.error("Fail to get KeyPhrase By title, title does not exsits")
        # return not found
        p['message'] = 'The title does not exsits'
    return p


def getWholeKeyPhraseWordCloud():
    """
    get the worldCloud html of all the KeyPhrases and save as the background
    :return: the worldCloud html of all the KeyPhrases
    """
    logger.debug("Start to get Whole KeyPhrase WordCloud")
    # process all the keyPhrase
    allKeyPhrases = TotalKeyPhrases().getAll()
    # draw the word cloud
    wordCloud = generateWoldCloud(allKeyPhrases)
    # imgkit.from_file(wordCloud.render(), 'app01/static/image/1ooo.jpg')
    return wordCloud.render_embed()


def getKeyPhraseByURL(url):
    """
    search the db to find keyPhrase by the url and return the required information
    :param url: the url of pdf
    :return: {
            "wordCloud": wordCloud,
            "title": title,
            'url': url,
            'result': 'S' or 'F'
            'message': if F
            }
    """
    logger.debug("Start to get KeyPhrase By URL")
    # search the db to see if the url already exsits
    pdfContent = PDFContent()
    p = pdfContent.getByFields(field='url', content=url)

    # if the title exsits
    if p.get('result'):
        logger.debug("The file already in the DB")
        wordCloud = generateWoldCloud(p.get('keyPhrases'))
        p['wordCloud'] = wordCloud.render_embed()
        return p
    # download the pdf by url and transfer to raw text
    text = ''
    try:
        logger.debug("fetch the PDF online")
        # fetch the PDF online
        web_file = urllib.request.urlopen(url)

        # Store all the pages of the PDF in a variable
        pages = pdf2image.convert_from_bytes(web_file.read())
        # Counter to store images of each page of PDF to image
        # Iterate through all the pages stored above
        for page in pages:
            # construct the raw text of the pdf
            text = text + str(pytesseract.image_to_string(page))
    # if the download failed
    except:
        logger.error("Fail to fetch the PDF online")
        return {
            'result': False,
            'message': 'Make sure the url is valid!'
        }

    # process the text to get the title, and turn to lower case
    tmp = processContent(text)
    title, text = tmp.get('title'), tmp.get('text')

    # Search the db to see if it is already exists
    pp = pdfContent.getByFields(field='title', content=title)
    if pp.get('result'):
        logger.debug("The file already in the DB, but with a different url")
        wordCloud = generateWoldCloud(pp.get('keyPhrases'))
        pp['wordCloud'] = wordCloud.render_embed()
        return pp

    logger.debug('Load TopicRank model and pick keyPhrase')
    # initialize keyphrase extraction model, here TopicRank
    extractor = pke.unsupervised.TopicRank()

    # load the content of the document, here document is expected to be in raw
    # format (i.e. a simple text file) and preprocessing is carried out using spacy
    extractor.load_document(input=text, language='en')

    # keyphrase candidate selection, in the case of TopicRank: sequences of nouns
    # and adjectives (i.e. `(Noun|Adj)*`)
    extractor.candidate_selection()

    # candidate weighting, in the case of TopicRank: using a random walk algorithm
    extractor.candidate_weighting()

    # N-best selection, keyphrases contains the 50 highest scored candidates as
    # (keyphrase, score) tuples
    keyPhrases = extractor.get_n_best(n=KEY_PHRASE_NUM)

    # create new record of PDFContent
    PDFContent.objects.create(title=title, url=url, keyPhrase=str(keyPhrases))

    logger.debug('update the new pdf into TotalKeyPhrases')
    # update db of the whole keyPhrase
    TotalKeyPhrases().updateNewPDF(keyPhrases=keyPhrases, title=title)
    # update the whole wordCloud png
    # getWholeKeyPhraseWordCloud()
    wordCloud = generateWoldCloud(keyPhrases).render_embed()
    return {
        "wordCloud": wordCloud,
        "title": title,
        'url': url,
        'result': True
    }


def getHotPDFList():
    """
    get the top10 hot PDF in the db
    :return: [pdf]
    """
    logger.debug('Get Hot'+ str(MAX_NUM)+' PDFList')
    pdfContent = PDFContent()
    return pdfContent.getHotPDFList(limit=MAX_NUM)


def getPDFListByKeyPhrase(keyPhrase):
    """
    get pdf with certain keyPhrase
    :return: [pdf]
    """
    logger.debug('Search PDF with keyPhrase' + keyPhrase )
    titles = TotalKeyPhrases().getPDFListByKeyPhrase(keyPhrase=keyPhrase)
    pdfList = []
    for i in titles:
        if i == '':
            continue
        pdf = PDFContent().getByFields(field='title', content=i)
        if pdf.get('result'):
            pdfList.append(pdf)
    return pdfList


def getHotKeyPhraseList():
    """
    get the top10 hot PDF in the db
    :return: [KeyPhrase]
    """
    logger.debug('Get Hot '+ str(MAX_NUM)+' KeyPhraseList')
    return TotalKeyPhrases().getHotKeyPhraseList(limit=MAX_NUM)
