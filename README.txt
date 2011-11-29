Introduction
============

Mobile results json structure
-----------------------------

You receive a dict of dicts, one for each accommodation found.


Accomodation dict
-----------------

 - name
 - type (depends on language)
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
