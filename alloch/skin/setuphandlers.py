import tempfile
from Products.LocalFS.LocalFS import manage_addLocalFS
from zope.component import getUtility, getMultiAdapter
from zope.app.component.interfaces import ISite
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from Products.CMFCore.utils import getToolByName
from Products.Five.component import enableSite

LANGUAGES = ['fr', 'nl', 'en']


def install(context):
    portal = context.getSite()
    if not ISite.providedBy(portal):
        enableSite(portal)
    deleteFolder(portal, 'news')
    deleteFolder(portal, 'events')
    deleteFolder(portal, 'Members')
    clearPortlets(portal)
    createLocalFS(portal)
    setupLanguages(portal)
    if not 'fr' in portal.objectIds():
        portal.restrictedTraverse('@@language-setup-folders')()
        frontPage = getattr(portal.fr, 'front-page')
        publishObject(frontPage)
        createTranslationsForObject(frontPage)
        for lang in LANGUAGES:
            langFolder = getattr(portal, lang)
            langFolder.setDefaultPage('front-page')
            changePageView(portal, getattr(langFolder, 'front-page'), 'search-page-view')


def createLocalFS(portal):
    if 'photos_heb' not in portal.objectIds():
        manage_addLocalFS(portal, 'photos_heb', 'Photos heb',
                          tempfile.gettempdir()) # /home/gites/photos_heb


def deleteFolder(portal, folderId):
    folder = getattr(portal, folderId, None)
    if folder is not None:
        portal.manage_delObjects(folderId)


def setupLanguages(portal):
    lang = getToolByName(portal, 'portal_languages')
    lang.supported_langs = LANGUAGES
    lang.setDefaultLanguage('fr')
    lang.display_flags = 0


def createTranslationsForObject(neutralObject):
    translatedObjects = []
    for lang in LANGUAGES:
        if not neutralObject.hasTranslation(lang):
            translated = neutralObject.addTranslation(lang)
            publishObject(translated)
            translated.reindexObject()
            translatedObjects.append(translated)
    return translatedObjects


def publishObject(obj):
    portal_workflow = getToolByName(obj, 'portal_workflow')
    if portal_workflow.getInfoFor(obj, 'review_state') in ['visible', 'private']:
        portal_workflow.doActionFor(obj, 'publish')


def clearPortlets(folder):
    clearColumnPortlets(folder, 'left')
    clearColumnPortlets(folder, 'right')


def clearColumnPortlets(folder, column):
    manager = getManager(folder, column)
    assignments = getMultiAdapter((folder, manager, ), IPortletAssignmentMapping)
    for portlet in assignments:
        del assignments[portlet]


def getManager(folder, column):
    if column == 'left':
        manager = getUtility(IPortletManager, name=u'plone.leftcolumn', context=folder)
    else:
        manager = getUtility(IPortletManager, name=u'plone.rightcolumn', context=folder)
    return manager


def addViewToType(portal, typename, templatename):
    pt = getToolByName(portal, 'portal_types')
    foldertype = getattr(pt, typename)
    available_views = list(foldertype.getAvailableViewMethods(portal))
    if not templatename in available_views:
        available_views.append(templatename)
        foldertype.manage_changeProperties(view_methods=available_views)


def changePageView(portal, page, viewname):
    addViewToType(portal, 'Document', viewname)
    if page.getLayout() != viewname:
        page.setLayout(viewname)
