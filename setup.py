from setuptools import setup, find_packages

setup(
    name='PJC_tournament_manager',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    url='http://www.pobot.org',
    license='LGPLv3',
    author='Eric Pascual',
    author_email='eric@pobot.org',
    description='Web application for POBOT Junior Cup tournament management',
    install_requires=['tornado>=3.0'],
    zip_safe=True
)
