# -*- coding: utf-8 -*-

import re
from mobile.sniffer.utilities import get_user_agent
from zope.publisher.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from alloch.skin import AlloCHMessage as _

_mobilePlatforms = r'android|blackberry|ip(hone|od|ad)|palm|symbian|webos|windows'
_mobilePlatforms = re.compile(_mobilePlatforms, re.IGNORECASE)


class Store(BrowserView):
    """
    """

    def redirectFromQRcode(self):
        """
        QR Code points to http://www.allochambredhotes.be/download/
        """
        userAgent = get_user_agent(self.request)
        if _mobilePlatforms.search(userAgent) is None:
            portalUrl = getToolByName(self.context, 'portal_url')()
            message = _("unable_detect_device", "We were unable to detect your device system.")
            message = self.context.translate(message)
            self.context.plone_utils.addPortalMessage(message)
            self.request.response.redirect(portalUrl)
            return ''

        if 'android' in userAgent.lower():
            portalUrl = getToolByName(self.context, 'portal_url')()
            self.context.plone_utils.addPortalMessage('ANDROID DEVICE WAS DETECTED !')
            self.request.response.redirect(portalUrl)
            return ''
        if 'blackberry' in userAgent.lower():
            portalUrl = getToolByName(self.context, 'portal_url')()
            self.context.plone_utils.addPortalMessage('BLACKBERRY DEVICE WAS DETECTED !')
            self.request.response.redirect(portalUrl)
            return ''
        if 'iphone' or 'ipad' or 'ipod' in userAgent.lower():
            portalUrl = getToolByName(self.context, 'portal_url')()
            self.context.plone_utils.addPortalMessage('APPLE DEVICE WAS DETECTED !')
            self.request.response.redirect(portalUrl)
            return ''
            # self.request.response.redirect("http://itunes.apple.com/be/app/woodya-run/id302170850?mt=8")
            # return ''
        if 'palm' or 'webos' in userAgent.lower():
            portalUrl = getToolByName(self.context, 'portal_url')()
            self.context.plone_utils.addPortalMessage('WEBOS (PALM) DEVICE WAS DETECTED !')
            self.request.response.redirect(portalUrl)
            return ''
        if 'symbian' in userAgent.lower():
            portalUrl = getToolByName(self.context, 'portal_url')()
            self.context.plone_utils.addPortalMessage('SYMBIAN DEVICE WAS DETECTED !')
            self.request.response.redirect(portalUrl)
            return ''
        if 'windows' in userAgent.lower():
            portalUrl = getToolByName(self.context, 'portal_url')()
            self.context.plone_utils.addPortalMessage('WINDOWS DEVICE WAS DETECTED !')
            self.request.response.redirect(portalUrl)
            return ''
