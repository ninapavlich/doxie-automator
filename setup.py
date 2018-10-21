from setuptools import setup

setup(
    name='doxieautomator',    # This is the name of your PyPI-package.
    version='0.2',                          # Update the version number for new releases
    scripts=['doxieautomator'],                 # The name of your scipt, and also the command you'll be using for calling it
    url='https://github.com/ninapavlich/doxie-automator',
    author='Nina Pavlich',
    author_email='nina@ninalp.com',
    license = "MIT",
    include_package_data = True
)