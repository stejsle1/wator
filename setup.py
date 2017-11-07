from setuptools import setup, find_packages


with open('README') as f:
    long_description = ''.join(f.readlines())


setup(
   name='wator',
   version='0.1',
   keywords='wator simulation numpy',
   description='Python simulation of WaTor',
   long_description=long_description,
   author='Lenka Stejskalova',
   author_email='stejsle1@fit.cvut.cz',
   license='Public Domain',
   url='https://github.com/stejsle1/wator',
   install_requires=[
        'numpy',
        'pytest',
   ],
   classifiers=[
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
        ],
   zip_safe=False,
   packages=find_packages(), 
)

