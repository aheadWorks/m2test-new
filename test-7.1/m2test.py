#!/usr/bin/env python3
import subprocess
import click
from os.path import join as _
import os
import re
import json
import pathlib


BASIC_PATH = pathlib.Path(os.environ.get('MAGENTO_ROOT', '/var/www/html'))


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def remove_listeners(path):
    with open(path) as phpunit_config:
        data = phpunit_config.read()
        reg = re.compile("<listeners.*</listeners>", re.S)
        data = re.sub(reg, '', data)
    with open(path, 'w') as phpunit_config:
        phpunit_config.write(data)


def di_compile():
    proc = subprocess.Popen(['php', '/var/www/html/bin/magento', 'module:enable', '--all'])
    proc.communicate()
    ec3 = proc.returncode
    proc = subprocess.Popen(['php', '/var/www/html/bin/magento', 'setup:di:compile'])
    proc.communicate()
    ec4 = proc.returncode
    
    if ec3 or ec4:
        raise click.ClickException("Failed to di:compile")
    




def install(path):
    """
    Install extension(s) to path from path or zip
    """
    repo_type = 'path'

    click.echo("Installing from %s" % path)

    with open(path / 'composer.json') as f:
        composer = json.load(f)
        repo_name = re.sub(r'[^a-z0-9_]', '_', composer['name'])

    with cd(BASIC_PATH):
        f = open('auth.json.sample')
        composer_auth = json.load(f)
        f.close()
        composer_auth["http-basic"]["repo.magento.com"]["username"] = "ca6f970bb96d25614c90874edc90f42b"
        composer_auth["http-basic"]["repo.magento.com"]["password"] = "74ce69e7288fc3232fb3b038410e9ae6"
        os.system('touch auth.json')
        with open('auth.json', 'w') as file:
            json.dump(composer_auth, file, indent=2)
        os.system('composer config repositories.magento composer https://repo.magento.com/')
        proc = subprocess.Popen(['composer', 'config', 'repositories.' + repo_name, repo_type, path])
        proc.communicate()
        ec1 = proc.returncode
        proc = subprocess.Popen(['composer', 'require', '--prefer-dist', '{e[name]}:{e[version]}'.format(e=composer)])
        proc.communicate()
        ec2 = proc.returncode

        if ec1 or ec2:
            raise click.ClickException("Failed to install extension")

    return BASIC_PATH / 'vendor' / composer['name']



@click.group()
def cli():
    click.echo("Removing phpunit listeners")
    remove_listeners(BASIC_PATH / 'dev' / 'tests' / 'static' / 'phpunit.xml.dist')
    remove_listeners(BASIC_PATH / 'dev' / 'tests' / 'unit' / 'phpunit.xml.dist')


@cli.command()
@click.option('--severity', default=10, help='Severity level.')
@click.option('--report', default="junit", help='Report type.', type=click.Choice(["full", "xml", "checkstyle", "csv",
                                                                             "json", "junit", "emacs", "source",
                                                                             "summary", "diff", "svnblame", "gitblame",
                                                                             "hgblame", "notifysend"]))
@click.argument('path', type=click.Path(exists=True))
@click.argument('report_file', type=click.Path(), required=False)
def eqp(severity, report, path, report_file):
    """Run EQP tests for path"""

    proc = subprocess.Popen([_('/magento-coding-standard', 'vendor/bin/phpcs'), path, '--standard=Magento2',
                             '--severity='+str(severity), '--extensions=php,phtml', '--report='+report],
                            stdout=subprocess.PIPE
                            )
    stdout, stderr = proc.communicate()

    if report_file:
        with open(report_file, 'wb') as fp:
            fp.write(stdout)
    else:
        click.echo(stdout)
    exit(proc.returncode)


@cli.command()
@click.option('--report', default="junit", help='Report type.', type=click.Choice(["junit"]))
@click.argument('path', type=click.Path(exists=True))
@click.argument('report_file', type=click.Path(), required=False)
def unit(report, path, report_file):
    """Run unit tests for extension at path"""

    path = pathlib.Path(path)
    path = install(path)
    di_compile()

    options = [
        _(BASIC_PATH, 'vendor/bin/phpunit'),
        '--configuration',  _(BASIC_PATH, 'dev/tests/unit/phpunit.xml.dist')
    ]

    if report_file:
        options += ['--log-%s' % report, report_file]

    proc = subprocess.Popen(options + [_(path, 'Test/Unit')])
    proc.communicate()

    if not report_file:
        exit(proc.returncode)

    exit(proc.returncode)



@cli.command()
@click.option('--report', default="junit", help='Report type.', type=click.Choice(["junit"]))
@click.argument('path', type=click.Path(exists=True))
@click.argument('report_path', type=click.Path(), required=False)
def static(report, path, report_path):
    """
    Run static tests against path
    :param report:
    :param path:
    :param report_file:
    :return:
    """

    path = pathlib.Path(path)

    path = install(path)

    di_compile()

    with open(path / 'composer.json') as f:
        composer = json.load(f)

    path_changed_files = BASIC_PATH / 'dev' / 'tests' / 'static' / 'testsuite' / 'Magento' / 'Test' / 'Php' / '_files' / 'whitelist' / 'common.txt'

    options = [os.path.join(BASIC_PATH, 'vendor/bin/phpunit'), '--configuration', BASIC_PATH / 'dev/tests/static/phpunit.xml.dist']

    output_base = report_path or os.environ.get('RESULTS_DIR', '/results')

    with open(os.path.join(BASIC_PATH, 'dev/tests/static/phpunit.xml.dist')) as phpunit_config:
        suites = {}
        reg = re.compile('<testsuite[^>]+name="([^"]+)"')
        for line in phpunit_config:
            try:
                suite = re.search(reg, line).groups()[0]
                suites[suite.lower().replace(' ', '_')] = suite
            except (IndexError, AttributeError):
                pass

    # Collect php iles
    with open(path_changed_files, 'w') as fp:
        for root, dirs, files in os.walk(path):

            fp.writelines([os.path.relpath(os.path.abspath(os.path.join(root, f)), BASIC_PATH) + '\n' for f in files if os.path.splitext(f)[1] in (
                '.php',
                '.phtml'
            )])

    exit_code = 0
    for fname, name in suites.items():

        outfile = os.path.join(output_base, fname + '.xml')

        if re.search(re.compile('integrity'), fname):
            continue

        args = options + ['--testsuite=%s' % name]
        args += ['--log-%s' % report, outfile]
        proc = subprocess.Popen(args)
        proc.communicate()

        # Remove copy-paste results from report
        with open(os.path.join(output_base, fname + '.xml')) as f:
            data = f.read()
            data = re.sub('<testcase[^>]+name="testCopyPaste".+</testcase>', '', data,
                          flags=re.MULTILINE and re.DOTALL)

        with open(outfile, 'w') as f:
            f.write(data)

        exit_code = proc.returncode or exit_code

    exit(exit_code)

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def validate_m2_package(path):
    """
    Test marketplace package
    :param path:
    :return:
    """
    #proc = subprocess.Popen(['php', '-f', '/usr/local/bin/validate_m2_package.php', path])
    #proc.communicate()
    #exit(proc.returncode)

if __name__ == '__main__':
    cli()
