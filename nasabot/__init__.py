import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
