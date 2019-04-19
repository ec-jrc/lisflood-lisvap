import os
import sys
from glob import glob

from setuptools import setup, find_packages

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, './src/'))


setup(
    name='lisflood-lisvap',
    version='0.3',
    package_dir={'': 'src'},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    packages=find_packages('src'),
    description='LISVAP model python module',
    author='Ad de Roo, Peter Burek, Johan van der Knijff, Domenico Nappo',
    author_email='domenico.nappo@ext.ec.europa.eu',
    keywords='lisflood lisvap efas evapotranspiration evaporation',
    license='EUPL 1.2',
    url='https://github.com/ec-jrc/lisflood-lisvap',
    install_requires=['numpy>=1.15', 'pytest', 'netCDF4', 'python-dateutil'],
    entry_points={'console_scripts': ['lisvap = lisvap.lisvap1:main']},
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
        'Topic :: Scientific/Engineering :: Physics',
    ],
)
