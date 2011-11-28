# -*- coding: utf-8 -*-

import simplejson
from datetime import date
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import and_, select
from zope.publisher.browser import BrowserView
from pygeocoder import Geocoder, GeocoderError

TYPES_HEB = [5, 6, 9]  # chambres d'hôtes : 'CH', 'MH', 'CHECR'


class SearchHebergements(BrowserView):
    """
    """

    def getHebergement(self):
        """
        Return specified heb
        """
        hebPk = self.request.get('hebPk', None)
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        query = session.query(hebergementTable)
        heb = query.get(hebPk)
        return heb

    def getGPSForAddress(self, address):
        """
        Transform an address into GPS coordinates
        """
        gcoder = Geocoder('NO_API_KEY')
        try:
            result = gcoder.geocode(address, language='fr', region='be')
        except GeocoderError:
            return None
        return result.coordinates

    def getClosestHebs(self):
        """
        Search for the closests available hebs
        """
        form = self.request.form
        address = form.get('address', None)
        location = form.get('gpslocation', None)

        searchLocation = location and location or self.getGPSForAddress(address)
        print searchLocation
        # XXX use searchLocation with PostGIS

        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        proprioTable = wrapper.getMapper('proprio')
        reservationsTable = wrapper.getMapper('reservation_proprio')

        query = session.query(hebergementTable).join('proprio').outerjoin('reservations')
        query = query.filter(hebergementTable.heb_site_public == '1')
        query = query.filter(proprioTable.pro_etat == True)
        query = query.filter(hebergementTable.heb_typeheb_fk.in_(TYPES_HEB))

        # on ne considère que les hébergements pour lequel le calendrier
        # est utilisé et qui sont libres
        query = query.filter(hebergementTable.heb_calendrier_proprio != 'non actif')
        today = date.today()
        busyHeb = select([reservationsTable.heb_fk],
                         and_(reservationsTable.res_date >= today,
                              reservationsTable.res_date < today)).distinct().execute().fetchall()
        busyHebPks = [heb.heb_fk for heb in busyHeb]
        query = query.filter(~hebergementTable.heb_pk.in_(busyHebPks))

        query = query.order_by(hebergementTable.heb_nom)
        results = query.all()
        return results and results[0:5] or []

    def getMobileClosestHebs(self):
        """
        Return the closests available hebs for mobile use
        """
        results = self.getClosestHebs()
        hebs = []
        for heb in results:
            hebDict = {'name': heb.heb_nom}
            # XXX add more values in this dict ...
            hebs.append(hebDict)
        jsonResult = simplejson.dumps({'results': hebs})
        return jsonResult
