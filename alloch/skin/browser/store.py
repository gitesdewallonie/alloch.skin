# -*- coding: utf-8 -*-

from zope.publisher.browser import BrowserView


class Store(BrowserView):
    """
    """

    def redirectQRcode(self):
        """
        QR Code points to http://www.allochambredhotes.be/download/
        """
        self.request.response.redirect("http://itunes.apple.com/be/app/woodya-run/id302170850?mt=8")
        return ''
