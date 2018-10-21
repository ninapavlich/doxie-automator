from setuptools import setup, find_packages

setup(
    name = 'doxieautomator',
    version = '0.21',
    author = 'Nina Pavlich',
    author_email='nina@ninalp.com',
    url = 'https://github.com/ninapavlich/doxie-automator',
    license = "MIT",
    description = 'Retrieves scans on your Doxie Go or Doxie Q, places them in a local directory.',
    keywords = ['libraries', 'scanning'],
    include_package_data = True,
    packages = ['doxieautomator'],

    install_requires=[
        'Pillow',
    ],
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)