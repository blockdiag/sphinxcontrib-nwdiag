# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requires = ['blockdiag>=1.5.0', 'nwdiag>=1.0.3', 'Sphinx>=0.6']

setup(
    name='sphinxcontrib-nwdiag',
    version='0.9.3',
    url='http://github.com/tk0miya/sphinxcontrib-nwdiag',
    license='BSD',
    author='Takeshi KOMIYA',
    author_email='i.tkomiya@gmail.com',
    description='Sphinx "nwdiag" extension',
    long_description=open('README.rst').read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
