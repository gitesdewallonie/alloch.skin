# -*- coding: utf-8 -*-

import re
import simplejson
from datetime import date
from operator import attrgetter
from plone.memoize import view
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import and_, or_, exists, func
from zope.publisher.browser import BrowserView
from pygeocoder import Geocoder, GeocoderError
from Products.CMFCore.utils import getToolByName

from alloch.skin.pymaps import PyMap, Map, Icon
from alloch.skin import AlloCHMessage as _


TYPES_HEB = [5, 6, 9]  # chambres d'hôtes : 'CH', 'MH', 'CHECR'
HEB_PHOTOS_URL = "http://www.allochambredhotes.be/photos_heb/"
HEB_THUMBS_URL = "http://www.allochambredhotes.be/vignettes_heb/"
GOOGLE_API_KEY = "AIzaSyBSIA3vqZCw3EzaKcA8Bgynvj2pD4gGlXk"
BOUNDS = "49.439557,2.103882|51.110420,6.256714"
EPIS_TRANSLATIONS = {'fr': {'epi': u'épi',
                            'epis': u'épis',
                            'chambre_d_hotes': u"Chambre d'hôtes"},
                     'nl': {'epi': u'korenaar',
                            'epis': u'korenaren',
                            'chambre_d_hotes': u'Gastenkamer'},
                     'en': {'epi': u'corn ear',
                            'epis': u'corn ears',
                            'chambre_d_hotes': u'Guestroom'}}
LAT_LONG_PATTERN = r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$'


def convertToInt(str):
    """
    Convert database informations to int ... and handle invalid data !
    """
    res = 0
    if str:
        try:
            res = int(str)
        except:
            pass
    return res


class Location:
    pass


class GroupingAwareHebergement:
    """
    """
    def __init__(self, hebs, distance):
        self.grouped = False
        if len(hebs) > 1:
            self.grouped = True
        self.rooms = hebs
        self.hebergement = hebs[0]
        self.distance = distance

    def getFormattedRoomsPk(self):
        pks = [str(room.heb_pk) for room in self.rooms]
        return "|".join(pks)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        else:
            return getattr(self.hebergement, attr)


class SearchHebergements(BrowserView):
    """
    """

    def _convertToEntities(self, text):
        return ''.join(['&#%d;' % ord(ch) for ch in text])

    def _getEpisIcons(self, number):
        result = []
        url = getToolByName(self.context, 'portal_url')()
        for i in range(number):
            result.append('<img src="%s/++resource++1_epis.gif"/>' % url)
        return " ".join(result)

    def getEpis(self, heb):
        """
        Get the epis icons
        """
        l = [self._getEpisIcons(i.heb_nombre_epis) for i in heb.epis]
        return " - ".join(l)

    def getPhotosURL(self, codeGDW):
        """
        Returns photos URLs list
        """
        vignettes = []
        listeImage = self.context.photos_heb.fileIds()
        for i in range(15):
            if i < 10:
                photo = "%s0%s.jpg" % (codeGDW, i)
            else:
                photo = "%s%s.jpg" % (codeGDW, i)
            if photo in listeImage:
                vignettes.append("%s%s" % (HEB_PHOTOS_URL, photo))
        return vignettes

    @view.memoize
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

    def getHebItineraryURL(self, heb):
        baseUrl = "http://maps.google.com/maps?"
        origin = self.getSearchLocation().formatted_address
        dest = "%s %s %s (%s)" % (heb.heb_adresse, heb.commune.com_cp, heb.heb_localite, heb.heb_nom)
        language = self.request.get('LANGUAGE', 'fr')
        parameters = "saddr=%s&daddr=%s&hl=%s" % (origin, dest, language)
        return "%s%s" % (baseUrl, parameters)

    @view.memoize
    def getSearchLocation(self):
        form = self.request.form
        address = form.get('address', None)
        if address is not None:
            pattern = r'[a-zA-Z]'
            language = self.request.get('LANGUAGE', 'fr')
            belgiumStr = (language == 'fr' and 'Belgique') or \
                         (language == 'en' and 'Belgium') or \
                         (language == 'nl' and 'Belgïe')
            if re.search(pattern, address) and not belgiumStr in address:
                address = '%s, %s' % (address, belgiumStr)
            return self._getGeoSearchLocation(address)
        else:
            session = self.request.SESSION
            if session.has_key('search_location'):
                return session['search_location']
            else:
                return None

    def _getGeoSearchLocation(self, address):
        """
        Transform an address into GPS coordinates and name
        """
        gcoder = Geocoder(GOOGLE_API_KEY)
        language = self.request.get('LANGUAGE', 'fr')
        if re.search(LAT_LONG_PATTERN, address):
            # We have a lat long couple
            lat, lng = address.split(',')
            lat = float(lat)
            lng = float(lng)
            try:
                result = gcoder.reverse_geocode(lat, lng, language=language,
                                                region='be')
            except GeocoderError:
                return None
        else:
            try:
                result = gcoder.geocode(address, language=language,
                                        region='be', bounds=BOUNDS)
            except GeocoderError:
                return None
        # returned result must be serializable
        location = Location()
        location.coordinates = result.coordinates
        location.formatted_address = result.formatted_address
        return location

    def getCompleteMap(self):
        location = self.getSearchLocation()
        if location is None:
            return ""
        hebs = self.getSearchResults()
        return self._getMapJS(location, hebs)

    def getRoomsMap(self):
        location = self.getSearchLocation()
        if location is None:
            return ""
        hebs = self.getRooms()
        return self._getMapJS(location, hebs)

    def getHebMap(self):
        location = self.getSearchLocation()
        hebs = [self.getHebergement()]
        return self._getMapJS(location, hebs)

    def shouldDisplayNumberedMarkers(self, hebs):
        if len(hebs) < 2:
            return False
        if hebs[0].heb_gps_long == hebs[1].heb_gps_long and \
           hebs[0].heb_gps_lat == hebs[1].heb_gps_lat:
            return False
        return True

    def _getMapJS(self, location, hebs):
        map1 = Map(id='map')
        if location is not None:
            coordinates = location.coordinates
            map1.center = coordinates
            currentLocation = self._convertToEntities(location.formatted_address)
            searchLocationTitle = _('your_search_location', 'Your search location')
            searchLocationTitle = self.context.translate(searchLocationTitle)
            center = [coordinates[0], coordinates[1],
                      u"<strong>%s</strong><br /><i>&rarr; %s</i>" % (searchLocationTitle,
                                                                      currentLocation),
                      'location']
            map1.setpoint(center)
        counter = 0
        portalUrl = getToolByName(self.context, 'portal_url')()
        withNb = self.shouldDisplayNumberedMarkers(hebs)
        for heb in hebs:
            counter += 1
            grouped = getattr(heb, 'grouped', False)
            if grouped:
                href = "%s/rooms-list?group=%s" % (portalUrl, heb.heb_pro_fk)
            else:
                href = "%s/heb-detail?hebPk=%s" % (portalUrl, heb.heb_pk)
            imageSrc = str("%s/vignettes_heb/%s" % (portalUrl, heb.getVignette()))
            name = self._convertToEntities(heb.heb_nom)
            tooltip = "<a href='%s'><strong>%s. %s</strong><br /><img src='%s'></a>" % (href, counter, name, imageSrc)
            point = [heb.heb_gps_lat, heb.heb_gps_long, tooltip,
                     'marker%s' % (withNb and counter or '')]
            map1.setpoint(point)
        g = PyMap(maplist=[map1])
        locationIcon = Icon('location')
        locationIcon.image = "%s/++resource++%s" % (portalUrl, 'location.png')
        locationIcon.shadow = "%s/++resource++%s" % (portalUrl, 'location_shadow.png')
        g.addicon(locationIcon)
        for i in range(1, len(hebs) + 1):
            icon = Icon('marker%s' % i)
            icon.image = "%s/++resource++%s" % (portalUrl, 'marker%s.png' % i)
            icon.shadow = "%s/++resource++%s" % (portalUrl, 'marker_shadow.png')
            g.addicon(icon)
        g.key = GOOGLE_API_KEY
        language = self.request.get('LANGUAGE', 'fr')
        return g.pymapjs(language)

    def useExistingSession(self, session, searchLocation):
        if searchLocation:
            if session.has_key('search_location') and \
               session['search_location'] is not None and \
               session['search_location'].__dict__ == searchLocation.__dict__:
                return True
            else:
                return False
        else:
            form = self.request.form
            address = form.get('address', None)
            if address is not None:
                return False
            if session.has_key('search_location'):
                return True
            else:
                return False

    def getSearchResults(self):
        session = self.request.SESSION
        searchLocation = self.getSearchLocation()
        if not self.useExistingSession(session, searchLocation):
            session['search_location'] = searchLocation
            session['search_results'] = self.getClosestHebs()
        return session['search_results']

    def getRooms(self):
        session = self.request.SESSION
        if not session.has_key('search_location') or \
           not session.has_key('search_results'):
            return []
        form = self.request.form
        proprioPk = form.get('group', None)
        for heb in session['search_results']:
            if heb.heb_pro_fk == int(proprioPk):
                return heb.rooms
        return []

    def getClosestHebs(self):
        """
        Search for the closests available hebs
        """
        searchLocation = self.getSearchLocation()
        if not searchLocation:
            return []
        return self._getClosestHebsForLocation(searchLocation)

    @view.memoize
    def _getClosestHebsForLocation(self, searchLocation):
        today = date.today()
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        proprioTable = wrapper.getMapper('proprio')
        reservationsTable = wrapper.getMapper('reservation_proprio')

        distance = func.ST_distance_sphere(func.makepoint(hebergementTable.heb_gps_lat,
                                                          hebergementTable.heb_gps_long),
                                           func.ST_MakePoint(searchLocation.coordinates[0],
                                                             searchLocation.coordinates[1]))

        query = session.query(distance.label('distance'),
                              hebergementTable).join('proprio')
        query = query.filter(hebergementTable.heb_site_public == '1')
        query = query.filter(hebergementTable.heb_desactivation_alloch == False)
        query = query.filter(proprioTable.pro_etat == True)
        query = query.filter(hebergementTable.heb_typeheb_fk.in_(TYPES_HEB))

        # on ne considère que les hébergements pour lequel le calendrier
        # est utilisé et qui sont libres
        query = query.filter(or_(hebergementTable.heb_calendrier_proprio == 'actif',
                                 hebergementTable.heb_calendrier_proprio == 'searchactif'))
        query = query.filter(~exists().where(and_(reservationsTable.res_date == today,
                                                  hebergementTable.heb_pk == reservationsTable.heb_fk)))

        # et on prend les 5 structures les plus proches de la localisation
        query = query.order_by(distance)
        results = self._handleGroupedRooms(query)
        return results

    def _handleGroupedRooms(self, hebsQuery):
        """
        We need to consider multiple rooms of an owner as one heb
        and continue grouping them, even if we already have 5 different hebs
        """
        propriosHebs = {}
        for res in hebsQuery:
            # group rooms by owner
            proPk = res.Hebergement.heb_pro_fk
            if not res.Hebergement.heb_pro_fk in propriosHebs:
                if len(propriosHebs) == 5:
                    # we completed our 5 closest hebs grouping
                    break
                propriosHebs[proPk] = {'distance': int(res.distance / 1000),
                                       'hebs': [res.Hebergement]}
            else:
                propriosHebs[proPk]['hebs'].append(res.Hebergement)
        results = []
        for propHeb in propriosHebs.values():
            results.append(GroupingAwareHebergement(propHeb['hebs'],
                                                    propHeb['distance']))
        results = sorted(results, key=attrgetter('distance'))
        return results

    def _buildDictForHeb(self, heb, distance):
        form = self.request.form
        lang = form.get('LANGUAGE', 'fr')
        hebDict = {'name': heb.heb_nom}
        hebDict['type'] = heb.type.getTitle(lang)
        # Invert longitude and latitude due to DB correction
        # (otherwise, should be fixed in all mobile applications)
        hebDict['latitude'] = heb.heb_gps_long
        hebDict['longitude'] = heb.heb_gps_lat
        hebDict['distribution'] = heb.getDistribution(lang)
        hebDict['classification'] = [e.heb_nombre_epis for e in heb.epis]
        hebDict['capacity_min'] = convertToInt(heb.heb_cgt_cap_min)
        hebDict['capacity_max'] = convertToInt(heb.heb_cgt_cap_max)
        hebDict['description'] = heb.getDescription(lang)
        address = {'address': heb.heb_adresse,
                   'zip': heb.commune.com_cp,
                   'town': heb.heb_localite,
                   'city': heb.commune.com_nom}
        hebDict['address'] = address
        price = heb.heb_tarif_chmbr_avec_dej_2p
        # Price should be formatted as "XX.XX" string
        formattedPrice = str("{0:.2f}".format(float(price)))
        hebDict['price'] = formattedPrice
        hebDict['room_number'] = convertToInt(heb.heb_cgt_nbre_chmbre)
        hebDict['one_person_bed'] = convertToInt(heb.heb_lit_1p)
        hebDict['two_person_bed'] = convertToInt(heb.heb_lit_2p)
        hebDict['additionnal_bed'] = convertToInt(heb.heb_lit_sup)
        hebDict['child_bed'] = convertToInt(heb.heb_lit_enf)
        phone = heb.proprio.pro_tel_priv
        if not phone:
            phone = heb.proprio.pro_gsm1
        owner = {'title': heb.proprio.civilite.civ_titre,
                 'firstname': heb.proprio.pro_prenom1,
                 'name': heb.proprio.pro_nom1,
                 'language': heb.proprio.pro_langue,
                 'phone': phone,
                 'fax': heb.proprio.pro_fax_priv,
                 'mobile': heb.proprio.pro_gsm1,
                 'email': heb.proprio.pro_email,
                 'website': heb.heb_url}
        hebDict['owner'] = owner
        vignette = heb.getVignette()
        vignetteURL = "%s%s" % (HEB_THUMBS_URL, vignette)
        hebDict['thumb'] = vignetteURL
        hebDict['photos'] = self.getPhotosURL(heb.heb_code_gdw)
        epis = heb.epis
        if epis:
            nbEpis = epis[0].heb_nombre_epis
            description = hebDict['description']
            if nbEpis == 1:
                description = "%s 1 %s. %s" % (EPIS_TRANSLATIONS[lang]['chambre_d_hotes'],
                                               EPIS_TRANSLATIONS[lang]['epi'],
                                               description)
            elif nbEpis > 1:
                description = "%s %s %s. %s" % (EPIS_TRANSLATIONS[lang]['chambre_d_hotes'],
                                                nbEpis,
                                                EPIS_TRANSLATIONS[lang]['epis'],
                                                description)
            hebDict['description'] = description
        return hebDict

    def getMobileClosestHebs(self):
        """
        Return the closests available hebs for mobile use
        """
        searchLocation = self.getSearchLocation()
        if searchLocation is None:
            return
        results = self._getClosestHebsForLocation(searchLocation)
        hebs = []
        for heb in results:
            if not heb.grouped:
                hebDict = self._buildDictForHeb(heb, heb.distance)
                hebs.append(hebDict)
            else:
                distance = heb.distance
                roomsList = []
                for room in heb.rooms:
                    roomDict = self._buildDictForHeb(room, distance)
                    roomsList.append(roomDict)
                hebs.append(roomsList)
        searchLocationDict = {'coordinates': [searchLocation.coordinates[0],
                                              searchLocation.coordinates[1]],
                              'title': searchLocation.formatted_address}
        jsonResult = simplejson.dumps({'search_location': searchLocationDict,
                                       'results': hebs})
        return jsonResult
