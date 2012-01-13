from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='alloch.skin',
      version=version,
      description="Allo CH skin",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Affinitic Sprl',
      author_email='laurent.lasudry@affinitic.be',
      url='http://svn.affinitic.be/plone/gites/alloch.skin',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['alloch'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          'plone.app.themingplugins',
          'plone.memoize',
          'collective.js.jqueryui',
          'collective.captcha',
          'simplejson',
          'pygeocoder',
          'mobile.sniffer',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
