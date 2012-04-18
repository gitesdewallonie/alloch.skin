# -*- coding: utf-8 -*-

import re
from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

_mobilePlatforms = r'android|blackberry|ip(hone|od|ad)|palm|symbian|webos|windows ce; (iemobile|ppc)'
_mobilePlatforms = re.compile(_mobilePlatforms, re.IGNORECASE)


LINKS = {
'android': 'https://play.google.com/store/apps/details?id=be.gitesdewallonie.allochambresdhotes',
'ios': 'http://itunes.apple.com/be/app/allo-chambre-dhotes/id509470840?mt=8',
'blackberry': 'http://appworld.blackberry.com/webstore/content/96277/',
'symbian': 'http://clavius.affinitic.be/mobile/be.gitesdewallonie.allochambresdhotes.wgz',
'webos': 'http://clavius.affinitic.be/mobile/be.gitesdewallonie.allochambresdhotes.ipk',
}


class Store(BrowserView):
    """
    """
    storeTemplate = ViewPageTemplateFile("templates/stores.pt")

    def getStoreLink(self, device):
        """
        """
        if device in LINKS:
            return LINKS[device]
        return ""

    def redirectFromQRcode(self):
        """
        QR Code points to http://www.allochambredhotes.be/download/
        """
        userAgent = get_user_agent(self.request)
        if _mobilePlatforms.search(userAgent) is None or \
           not detect_mobile_browser(userAgent):
            return self.storeTemplate()

        if 'android' in userAgent.lower():
            self.request.response.redirect(LINKS['android'])
        if 'blackberry' in userAgent.lower():
            self.request.response.redirect(LINKS['blackberry'])
        if 'iphone' or 'ipad' or 'ipod' in userAgent.lower():
            self.request.response.redirect(LINKS['ios'])
        if 'palm' or 'webos' in userAgent.lower():
            self.request.response.redirect(LINKS['webos'])
        if 'symbian' in userAgent.lower():
            self.request.response.redirect(LINKS['symbian'])
        if 'windows' in userAgent.lower():
            self.context.plone_utils.addPortalMessage('WINDOWS DEVICE WAS DETECTED !')
            return self.storeTemplate()
