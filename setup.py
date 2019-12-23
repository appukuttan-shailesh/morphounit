try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='morphounit',
    version='1.0.4',
    author='Shailesh Appukuttan, Pedro Garcia-Rodriguez',
    author_email='shailesh.appukuttan@cnrs.fr, pedro.garcia@cnrs.fr',
    packages=['morphounit',
              'morphounit.capabilities',
              'morphounit.tests',
              'morphounit.scores',
              'morphounit.plots'],
    url='https://github.com/appukuttan-shailesh/morphounit',
    keywords = ['morphology', 'structure', 'circuit', 'testing', 'validation framework'],
    license='MIT',
    description='A SciUnit library for data-driven testing of neuronal morphologies.',
    long_description="",
    install_requires=['neo','elephant','sciunit>=0.1.5.2', 'neurom==1.4.6', 'tabulate', 'seaborn'],
    dependency_links = ['git+http://github.com/neuralensemble/python-neo.git#egg=neo-0.4.0dev',
                        'https://github.com/scidash/sciunit/tarball/dev']
)
