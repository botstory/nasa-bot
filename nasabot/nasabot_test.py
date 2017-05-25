import nasabot
import os


def test_version():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'version.txt')) as version_file:
        assert nasabot.__version__ == version_file.read().strip()
