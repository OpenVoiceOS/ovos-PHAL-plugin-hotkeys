#!/usr/bin/env python3
from setuptools import setup

from ovos_utils.xdg_utils import XDG_DATA_HOME

BASEDIR = os.path.abspath(os.path.dirname(__file__))
PLUGIN_ENTRY_POINT = 'ovos-PHAL-plugin-hotkeys=ovos_phal_plugin_hotkeys:HotKeysPlugin'


def get_version():
    """ Find the version of the package"""
    version = None
    version_file = os.path.join(BASEDIR, 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace(
                '~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


setup(
    name='ovos-PHAL-plugin-hotkeys',
    version=get_version(),
    description='map keypresses to OVOS bus events',
    url='https://github.com/OpenVoiceOS/ovos-PHAL-plugin-hotkeys',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['ovos_phal_plugin_hotkeys',
              'ovos_phal_plugin_hotkeys.keyboard',
              "ovos_phal_plugin_hotkeys.config"],
    package_data={"config": ["*.json"]},
    include_package_data=True,
    install_requires=required("requirements.txt"),
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    keywords='OVOS plugin',
    entry_points={'ovos.plugin.phal': PLUGIN_ENTRY_POINT}
)
