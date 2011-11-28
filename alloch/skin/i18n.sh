#!/bin/sh
#
i18ndude rebuild-pot --pot locales/alloch.pot --create alloch .
msgmerge -U --backup=off locales/fr/LC_MESSAGES/alloch.po locales/alloch.pot
msgmerge -U --backup=off locales/nl/LC_MESSAGES/alloch.po locales/alloch.pot
msgmerge -U --backup=off locales/en/LC_MESSAGES/alloch.po locales/alloch.pot
