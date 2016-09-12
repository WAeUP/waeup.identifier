from setuptools import setup, find_packages
import os
import sys
import multiprocessing  # neccessary to keep setuptools quiet in tests


version = '0.1.dev0'
tests_path = os.path.join(os.path.dirname(__file__), 'tests')


tests_require = [
    'pytest >= 2.0.3',
    'pytest-cov',
]


setup(
    name='waeup.identifier',
    version=version,
    description="Identify WAeUP students biometrically.",
    long_description=open(
        "README.rst").read() + "\n\n" + open("CHANGES.txt").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        (
            "License :: OSI Approved :: GNU General Public "
            "License v3 or later (GPLv3+)"
        ),
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.2",
        "Operating System :: POSIX",
        "Framework :: Paste",
        "Environment :: X11 Applications",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
    ],
    keywords='fingerprint authentication identification security tcl tk ',
    author='Uli Fouquet',
    author_email='uli at gnufix.de',
    url='http://pypi.python.org/pypi/waeup.identifier',
    license='GPL',
    packages=find_packages('.', exclude=['ez_setup']),
    # package_dir = {'': 'src'},
    namespace_packages=['waeup', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=tests_require,
    extras_require=dict(
        dev=tests_require,
        docs=[
            'Sphinx',
            'sphinx_rtd_theme',
        ]
    ),
    entry_points="""
    [console_scripts]
    waeup_identifier = waeup.identifier:main
    fake_kofa_server = waeup.identifier.testing:start_fake_kofa
    """,
)
