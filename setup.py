"""
Copyright 2019 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission  subsequent versions of the EUPL (the "Licence");

You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt

Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and limitations under the Licence.

---------------------------------------------------------------------------------------------------------------------------------------
Use python setup.py upload to publish versioned tags and pypi package

Manually step by step:

1. python setup.py sdist


2. python setup.py upload


3. In prod:
pip install lisflood-lisvap

# Test package

2a. To upload new package on PyPi Test:
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

3a. Test package install
pip install --index-url https://test.pypi.org/simple/ lisflood-lisvap==0.3.4


"""


import os
import sys
from glob import glob
from shutil import rmtree

from setuptools import setup, find_packages, Command


current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, './src/'))

from lisvap import __version__

readme_file = os.path.join(current_dir, 'README.md')

with open(readme_file, 'r') as f:
    long_description = f.read()


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Publish lisflood-lisvap package.'
    user_options = []

    @staticmethod
    def print_console(s):
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.print_console('Removing previous builds...')
            rmtree(os.path.join(current_dir, 'dist'))
        except OSError:
            pass

        self.print_console('Building Source and Wheel (universal) distribution...')
        os.system('{0} setup.py sdist'.format(sys.executable))

        self.print_console('Uploading the package to PyPI via Twine...')
        os.system('twine upload dist/*')

        self.print_console('Pushing git tags...')
        os.system('git tag v{0}'.format(__version__))
        os.system('git push --tags')

        sys.exit()


setup(
    name='lisflood-lisvap',
    version=__version__,
    package_dir={'': 'src'},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    packages=find_packages('src'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='LISVAP model python module',
    author='Ad de Roo, Peter Burek, Johan van der Knijff, Domenico Nappo',
    author_email='domenico.nappo@ext.ec.europa.eu',
    keywords='lisflood lisvap efas evapotranspiration evaporation',
    license='EUPL 1.2',
    url='https://github.com/ec-jrc/lisflood-lisvap',
    setup_requires=['future', 'nine'],
    install_requires=['numpy>=1.15', 'netCDF4', 'python-dateutil', 'future', 'nine', 'pathlib2'],
    python_requires=">=2.7,!=3.0.*,!=3.1.*",
    scripts=['bin/lisvap'],
    zip_safe=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    # setup.py publish to pypi.
    cmdclass={
        'upload': UploadCommand,
        'publish': UploadCommand,
    },
)
