# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import common


# Handle other languages later
MESSAGE = u"Si vous ne consentez pas à ou que vous ne pouvez pas autoriser " \
u"la collecte ou le traitement de vos Données tels que décrits dans la " \
u"<a href='{{cookiePolicyLink}}'>Charte de Confidentialité des données</a>, " \
u"n'utilisez pas le Site."

JS_TEMPLATE = """
<script id="cookiecuttr" type="text/javascript">
    (function($) {
        $(document).ready(function () {
            if($.cookieCuttr) {
                $.cookieCuttr({cookieAnalytics: false,
                               cookieNotificationLocationBottom: true,
                               cookiePolicyLink: "https://www.gitesdewallonie.be/charte-de-confidentialite",
                               cookieMessage: "%s",
                               cookieAcceptButtonText: "OK"
                               });
                }
        })
    })(jQuery);
</script>
"""


class CookiecuttrViewlet(common.ViewletBase):

    def available(self):
        return True

    def render(self):
        return JS_TEMPLATE % MESSAGE
