Mobile results JSON structure
=============================

You receive a dict with search_location and results


Search location
---------------

Search location is a dict with :
 - coordinates (list with longitude and latitude)
 - title (returned by geocoding or search for this location)


Results
-------

Results is a list of accomodation.
If an accomodation has several rooms (multiple accomodation in DB), you get a
list of rooms (same structure as an accomodation) instead of a single
accomodation.


Accomodation (room) dict
------------------------

 - name
 - type (depends on language)
 - latitude
 - longitude
 - distribution
 - classification (a list, because some accomodations can have eg. "3-4" epis)
 - capacity_min
 - capacity_max
 - description (depends on language)
 - address
    * address
    * zip (can contain letters, don't convert it to integer)
    * town
    * city
 - price
 - room_number
 - one_person_bed
 - two_person_bed
 - additionnal_bed
 - child_bed
 - smokers_allowed (true / false)
 - animal_allowed (true / false)
 - owner
    * title
    * firstname
    * name
    * language
    * phone
    * fax
    * mobile
    * email
    * website
 - thumb (URL)
 - photos (list of URLs)


TO DO
=====

 - use sessions to store search location and rooms PK
 - use real servers - URLs when we have the domain name
 - see how pages and results should display (for grouped hebs)
 - ...
