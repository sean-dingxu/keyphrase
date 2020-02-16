# Create your models here.
"""
    Create your models here.
    the models corresponding to the db
    including:
        fields
        functions to handle db
"""

from django.db import models


class PDFContent(models.Model):
    # title of the PDF
    title = models.CharField(max_length=100, unique=True)
    # url of the PDF
    url = models.CharField(max_length=200, default='')
    # content = models.CharField(max_length=100000)
    # keyPhrases of this PDF
    keyPhrase = models.TextField(null=False)
    # the number of how many times this PDF has been searched
    num = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def getByFields(self, field, content):
        """
        get the record of PDF in db and check if the record exists or not
        :param field: search by which field, only title or url
        :param content: content
        :return: {'url': url,
                'title': title,
                'keyPhrases': keyPhrasesList, [(phrase, frequency)]
                'num': num,
                'result': True or False
                }
        """
        if field == 'title':
            tmp = PDFContent.objects.filter(title=content)
            if tmp.exists():
                p = tmp.get(title=content)
            else:
                return {'result': False}
        elif field == 'url':
            tmp = PDFContent.objects.filter(url=content)
            if tmp.exists():
                p = tmp.get(url=content)
            else:
                return {'result': False}
        else:
            return {'result': False}

        keyPhraseStr = p.keyPhrase.strip('[(').strip('])')
        keyPhrases = keyPhraseStr.split('), (')
        keyPhrasesList = []
        for i in keyPhrases:
            tmp = i.split(',')
            keyPhrasesList.append((eval(tmp[0]), tmp[1]))
        p.num += 1
        p.save()
        return {'url': p.url,
                'title': p.title,
                'keyPhrases': keyPhrasesList,
                'num': p.num,
                'result': True
                }

    def getHotPDFList(self, limit):
        """
        get the top hot PDF in the db, the limit is the number
        :return: [pdf]
        """
        pdfs = PDFContent.objects.all().order_by('-num')[:limit]
        pdfList = []
        for i in pdfs:
            pdfList.append({'title': i.title,
                            'url': i.url,
                            'num': i.num,
                            'result': True,
                            })
        return pdfList

    class Meta:
        ordering = ["num"]
        verbose_name = "title"
        verbose_name_plural = "title"


class TotalKeyPhrases(models.Model):
    # the content of keyPhrase
    content = models.CharField(max_length=200, unique=True)
    # the accumulated frequency of KeyPhrase
    frequency = models.FloatField(default=0.0)
    # titles of PDF which has this keyPhrase
    titles = models.TextField(null=False)

    def __str__(self):
        return self.content

    def getAll(self):
        """
        get all the KeyPhrases
        :return: all the KeyPhrases: [(phrase,frequency)]
        """
        # search all the db
        tmp = TotalKeyPhrases.objects.all()
        # process all the keyPhrase
        allKeyPhrases = []
        for i in tmp:
            allKeyPhrases.append((i.content, i.frequency))
        return allKeyPhrases

    def getPDFListByKeyPhrase(self, keyPhrase):
        """
        get the titles of pdf with certain keyPhrase
        :return: [titles]
        """
        titlesStr = TotalKeyPhrases.objects.get(content=keyPhrase).titles
        titles = titlesStr.split(';;')
        return titles

    def updateNewPDF(self, keyPhrases, title):
        """
        update db when the Pdf is new
        :param keyPhrases: [(phrase, frequency)]
        :param title: title of the Pdf
        :return:
        """
        for i in keyPhrases:
            tmp = TotalKeyPhrases.objects.get_or_create(content=i[0])
            tmp[0].frequency += i[1]
            tmp[0].titles += ';;' + title
            tmp[0].save()

    def getHotKeyPhraseList(self, limit):
        """
        get the top10 hot PDF in the db
        :return: [KeyPhrase]
        """
        keyPhraseList = TotalKeyPhrases.objects.all().order_by('-frequency')[:limit]
        k = []
        for i in keyPhraseList:
            k.append({'content': i.content,
                      'frequency': i.frequency
                      })
        return k

    class Meta:
        ordering = ['frequency']
        verbose_name = "content"
        verbose_name_plural = "content"
