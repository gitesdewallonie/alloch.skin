# -*- coding: utf-8 -*-
from z3c.sqlalchemy import getSAWrapper
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.Five import BrowserView
# from collective.captcha.browser.captcha import Captcha

from alloch.skin.mailer import Mailer

LANG_MAP = {'en': 'Anglais',
            'fr': 'Français',
            'nl': 'Néerlandais'}


class SendMail(BrowserView):
    """
    Envoi de mail
    """

    def sendMailToProprio(self):
        """
        envoi d'un mail au proprio suite a un contact via hebergement description
        """
        hebPk = self.request.get('heb_pk')
        # captcha = self.request.get('captcha', '')
        # captchaView = Captcha(self.context, self.request)
        # isCorrectCaptcha = captchaView.verify(captcha)
        # if not isCorrectCaptcha:
        #     return self()

        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Hebergement = wrapper.getMapper('hebergement')
        heb = session.query(Hebergement).get(int(hebPk))
        hebNom = heb.heb_nom
        proprioMail = heb.proprio.pro_email
        proprioMail = "lasudry@gmail.com"
        if not proprioMail:
            proprioMail = u'info@gitesdewallonie.be'
        contactCivilite = self.request.get('contactCivilite')
        contactNom = self.request.get('contactNom', '')
        contactPrenom = self.request.get('contactPrenom', '')
        contactAdresse = self.request.get('contactAdresse', '')
        contactCp = self.request.get('contactCp')
        contactLocalite = self.request.get('contactLocalite', '')
        contactPays = self.request.get('contactPays', '')
        contactLangue = self.request.get('contactLangue', None)
        if not contactLangue or contactLangue.strip() == '...':
            language = self.request.get('LANGUAGE', 'en')
            contactLangue = LANG_MAP.get(language, '')
        contactTelephone = self.request.get('contactTelephone', '')
        contactFax = self.request.get('contactFax', '')
        contactEmail = self.request.get('contactEmail', None)
        nombrePersonne = self.request.get('nombrePersonne')
        remarque = self.request.get('remarque', '')

        fromMail = "info@gitesdewallonie.be"
        if contactEmail is not None:
            try:
                checkEmailAddress(contactEmail)
                fromMail = contactEmail
            except EmailAddressInvalid:
                pass

        mailer = Mailer("localhost", fromMail)
        mailer.setSubject("[Depuis allo chambre d'hôtes - réservation pour cette nuit]")
        mailer.setRecipients(proprioMail)
        mail = u""":: DEMANDE ::

Une demande vient d'être réalisée via le site pour %s référence %s.

Il s'agit de :

    * Civilité : %s
    * Nom : %s
    * Prénom : %s
    * Adresse : %s
    * Localité : %s %s
    * Pays : %s
    * Langue : %s
    * Téléphone : %s
    * Fax : %s
    * E-mail : %s
    * Nombre de personne : %s
    * Remarque : %s
""" \
              % (hebNom, \
                hebPk, \
                contactCivilite, \
                unicode(contactNom, 'utf-8'), \
                unicode(contactPrenom, 'utf-8'), \
                unicode(contactAdresse, 'utf-8'), \
                contactCp, \
                unicode(contactLocalite, 'utf-8'), \
                unicode(contactPays, 'utf-8'), \
                unicode(contactLangue, 'utf-8'), \
                contactTelephone, \
                contactFax, \
                unicode(contactEmail, 'utf-8'), \
                nombrePersonne,\
                unicode(remarque, 'utf-8'))
        mailer.sendAllMail(mail.encode('utf-8'), plaintext=True)

        portalUrl = getToolByName(self.context, 'portal_url')()
        self.context.plone_utils.addPortalMessage("Votre demande a bien ete envoyee.")
        self.request.response.redirect("%s/heb-detail?hebPk=%s" % (portalUrl,
                                                                   hebPk))
        return ''
