# -*- coding: utf-8 -*-

import re
from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

_mobilePlatforms = r'android|blackberry|ip(hone|od|ad)|palm|symbian|webos|windows ce; (iemobile|ppc)'
_mobilePlatforms = re.compile(_mobilePlatforms, re.IGNORECASE)


class Store(BrowserView):
    """
    """
    storeTemplate = ViewPageTemplateFile("templates/stores.pt")

    def redirectFromQRcode(self):
        """
        QR Code points to http://www.allochambredhotes.be/download/
        """
        userAgent = get_user_agent(self.request)
        if _mobilePlatforms.search(userAgent) is None or \
           not detect_mobile_browser(userAgent):
            return self.storeTemplate()

        if 'android' in userAgent.lower():
            self.context.plone_utils.addPortalMessage('ANDROID DEVICE WAS DETECTED !')
            return self.storeTemplate()
        if 'blackberry' in userAgent.lower():
            self.context.plone_utils.addPortalMessage('BLACKBERRY DEVICE WAS DETECTED !')
            return self.storeTemplate()
        if 'iphone' or 'ipad' or 'ipod' in userAgent.lower():
            self.context.plone_utils.addPortalMessage('APPLE DEVICE WAS DETECTED !')
            return self.storeTemplate()
        if 'palm' or 'webos' in userAgent.lower():
            self.context.plone_utils.addPortalMessage('WEBOS (PALM) DEVICE WAS DETECTED !')
            return self.storeTemplate()
        if 'symbian' in userAgent.lower():
            self.context.plone_utils.addPortalMessage('SYMBIAN DEVICE WAS DETECTED !')
            return self.storeTemplate()
        if 'windows' in userAgent.lower():
            self.context.plone_utils.addPortalMessage('WINDOWS DEVICE WAS DETECTED !')
            return self.storeTemplate()
