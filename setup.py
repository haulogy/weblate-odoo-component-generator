# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from setuptools import setup, find_packages


setup(
    name='weblate-odoo-component-generator',
    description='Weblate component generator for Odoo modules',
    long_description='\n'.join((
        open('README.md').read(),
    )),
    use_scm_version=True,
    packages=find_packages(),
    install_requires=[
        # "Weblate",
    ],
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta'
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    setup_requires=[
        'setuptools-scm',
    ],
    entry_points='''
        [console_scripts]
        wocg=wocg.main:main
    ''',
)