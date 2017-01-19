# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

name='fuman-category-dictionary-tools'
version='0.1'
description=''
author='Kensuke Mitsuzawa'
author_email='kensuke_mitsuzawa@fumankaitori.com'
url=''
license_name='MIT'

install_requires = [
    'JapaneseTokenizer',
    'wikipedia',
    'sqlitedict'
]

dependency_links = []

setup(
    name=name,
    version=version,
    description=description,
    author=author,
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email=author_email,
    url=url,
    license=license_name,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
