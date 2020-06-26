#!/usr/bin/env python3
"""
Run to generate Dockerfiles for desired PHP versions
"""
from pathlib import Path
from shutil import copyfile
from distutils.dir_util import copy_tree

from distutils.version import StrictVersion


head = """#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.py"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#
"""

files_to_copy = ("license.tmp", "makebuilds.py", "m2test.py", "deploypipeline.py", "entrypoint.sh", "hooks", "assets", "patch", "docker-compose.yml")

magento_versions = {
    "test-devops": {
        "exact_version": "2.3.4",
        "php_versions": ["7.4", "7.3", "7.2", "7.1"],
        "copy": files_to_copy
    },
    "test": {
        "exact_version": "2.3.4",
        "php_versions": ["7.4", "7.3", "7.2", "7.1"],
        "copy": files_to_copy
    }
}


with open('Dockerfile.template') as df:
    contents = df.read()

    for mage_ver, data in magento_versions.items():
        for php_ver in data['php_versions']:
            if mage_ver == 'latest':
                path = Path() / 'latest'
            else:
                path = (Path() / ("%s-%s" % (mage_ver, php_ver)))

            path.mkdir(exist_ok=True)

            new_content = contents.replace('%%PHP_VERSION%%', php_ver).replace('%%MAGENTO_VERSION%%', data['exact_version'])

            (path / 'Dockerfile').write_text(head + new_content)

            for p in Path().glob('*'):
                if p.name in data['copy']:
                    if (p.is_file()):
                        copyfile(p, path / p.name)
                    else:
                        copy_tree(p, str(path / p.name))