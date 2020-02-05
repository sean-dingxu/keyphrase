import logging

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .worker import getKeyPhraseByTitle, getKeyPhraseByURL, getHotPDFList, getHotKeyPhraseList, getPDFListByKeyPhrase, \
    getWholeKeyPhraseWordCloud

logger = logging.getLogger(__name__)


def indexPage(request):
    """
    simply return index page
    :param request:
    :return: index.html
    """
    logger.debug("Going to Index page")
    pass
    return render(request, 'index.html')


def searchPage(request):
    """
    simply return search page
    :param request:
    :return: searchPage.html
    """
    logger.debug("Going to Search page")
    pass
    return render(request, 'searchPage.html')


def search(request):
    """
    deal with search
    POST: from searchPage.html, two ways: title or url
    GET: from href inside list pages
    :param request:
    :return: detail.html
    """
    logger.debug("Execute the search task, load template : detail.html")

    template = loader.get_template('detail.html')
    # search on the search page
    if request.method == "POST":
        # get the params
        search_type = request.POST.get('type').strip()
        input = request.POST.get('url_pdf').strip()
        # if search by url
        if search_type == 'URL':
            logger.debug("Search by POST and URL: " + input)
            # check the validation
            result = getKeyPhraseByURL(input)
        # if search by title
        elif search_type == 'Title':
            logger.debug("Search by POST and Title " + input)
            result = getKeyPhraseByTitle(input)
        # check the result
        if not result.get('result'):
            logger.error('Search failed')
            messages.warning(request, 'Invalid Input! plz retry!    ' + result.get('message'))
            return render(request, 'searchPage.html')
        return HttpResponse(template.render(result, request))
    else:
        # search from href inside list pages
        input = request.GET.get("title").strip()
        logger.debug("Search by POST and title: " + input)
        result = getKeyPhraseByTitle(input)
        # check the result
        if not result.get('result'):
            return HttpResponse(request, 'mission failed, plz retry')
        return HttpResponse(template.render(result, request))


def pdfList(request):
    """
    return hot pdf
    :param request:
    :return: pdfList.html
    """
    logger.debug("Execute the pdfList task, load template : pdfList.html")
    template = loader.get_template('pdfList.html')
    return HttpResponse(template.render({'data': getHotPDFList(),
                                         'header': 'Hot articles'}, request))


def keyPhraseList(request):
    """
    return hot keyPhrase
    :param request:
    :return: keyPhraseList.html
    """
    logger.debug("Execute the keyPhraseList task, load template : keyPhraseList.html")
    template = loader.get_template('keyPhraseList.html')
    return HttpResponse(template.render({'data': getHotKeyPhraseList(),
                                         'header': 'Hot keyPhrases'}, request))


def keyPhraseWordCloud(request):
    """
    return the wordCloud of all the keyPhrases in our system
    :param request:
    :return: detail.html with certain title and no url
    """
    logger.debug("Execute the keyPhraseWordCloud task, load template : detail.html")
    template = loader.get_template('detail.html')
    wordCloud = getWholeKeyPhraseWordCloud()
    return HttpResponse(template.render({"wordCloud": wordCloud,
                                         "title": 'WordCloud of all the KeyPhrases',
                                         'url': ''}, request))


def pdfListByKeyPhrase(request):
    """
    get pdf list of a certain keyPhrase from href inside the keyPhraseList.html
    :param request:
    :return:
    """
    logger.debug("Execute the pdfListByKeyPhrase task, load template : pdfList.html")
    template = loader.get_template('pdfList.html')
    input = request.GET.get("keyPhrase").strip()
    result = getPDFListByKeyPhrase(input)
    # check the result
    return HttpResponse(template.render({'data': result,
                                         'header': 'Articles with KeyPhrase:  ' + input}, request))
