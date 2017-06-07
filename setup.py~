try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='morphounit',
    version='0.1',
    author='Shailesh Appukuttan',
    author_email='shailesh.appukuttan@unic.cnrs-gif.fr',
        packages=[
            'morphounit',
            'morphounit.capabilities',
            'morphounit.tests'],
    url='https://github.com/appukuttan-shailesh/morphounit',
    license='MIT',
    description='A SciUnit library for data-driven testing of neuronal morphologies.',
    long_description="",
    install_requires=['scipy>=0.17',
                      'matplotlib>=1.5',
                      'neo==0.4',
                      'elephant',
                      'sciunit==0.1.5.8',
                      'allensdk==0.12.4.1',
                      'pyneuroml>=0.2.3',
                      'scoop'],
    dependency_links = ['https://github.com/scidash/sciunit/tarball/dev#egg=sciunit-0.1.5.8',
                        'https://github.com/rgerkin/AllenSDK/tarball/python3.5#egg=allensdk-0.12.4.1',
                        'https://github.com/rgerkin/pyNeuroML/tarball/master#egg=pyneuroml-0.2.3']
)
