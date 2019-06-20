#!/usr/bin/env python3
import subprocess
import click
from os.path import join as _
import os
import re
from m2tools.extension import Extension
import tempfile
import shutil


BASIC_PATH = os.environ.get('MAGENTO_ROOT', '/var/www/html')


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def install(path):
    """
    Install extension(s) to path from path or zip
    """
    e = Extension()
    temp_path = tempfile.mkdtemp()

    try:
        subprocess.check_call(["cp", "-R", path, temp_path])
    
        path = os.path.join(temp_path, os.path.basename(path))
    
        if os.path.isdir(path):
            e.init_from_path(path)
            repo_type = 'path'
        else:
            repo_type = 'artifact'
            e.init_from_zip(path)
            path = os.path.dirname(path)
    
        with cd(BASIC_PATH):
            repo_name = re.sub(r'[^a-z0-9_]', '_', e.meta.name)
            proc = subprocess.Popen(['composer', 'config', 'repositories.' + repo_name, repo_type, path])
            proc.communicate()
            ec1 = proc.returncode
            proc = subprocess.Popen(['composer', 'require', '--prefer-dist', '{e.name}:{e.version}'.format(e=e.meta)])
            proc.communicate()
            ec2 = proc.returncode
    finally:
        shutil.rmtree(temp_path)

    return os.path.join(BASIC_PATH, 'vendor', e.meta.name)


@click.group()
def cli():
    pass


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

    with Extension(path) as e:
        proc = subprocess.Popen([_('/magento-coding-standard', 'vendor/bin/phpcs'), e.path, '--standard=Magento2',
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

    path = install(path)

    options = [
        _(BASIC_PATH, 'vendor/bin/phpunit'),
        '--configuration',  _(BASIC_PATH, 'dev/tests/unit/phpunit.xml.dist')
    ]

    if report_file:
        options += ['--log-%s' % report, report_file]

    with Extension(path) as e:
        proc = subprocess.Popen(options + [_(e.path, 'Test/Unit')])
        proc.communicate()

    if not report_file:
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

    path = install(path)

    with Extension(path) as e:
        vendor_path = os.path.join(BASIC_PATH, 'vendor', e.meta.name)

    path_changed_files = os.path.join(BASIC_PATH, 'dev', 'tests', 'static', 'testsuite', 'Magento', 'Test',
                                          'Php', '_files', 'whitelist', 'common.txt')

    options = [os.path.join(BASIC_PATH, 'vendor/bin/phpunit'), '--configuration','dev/tests/static/phpunit.xml.dist']

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
        for root, dirs, files in os.walk(vendor_path):

            fp.writelines([os.path.relpath(os.path.abspath(os.path.join(root, f)), BASIC_PATH) + '\n' for f in files if os.path.splitext(f)[1] in (
                '.php',
                '.phtml'
            )])

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

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def validate_m2_package(path):
    """
    Test marketplace package
    :param path:
    :return:
    """
    proc = subprocess.Popen(['php', '-f', '/usr/local/bin/validate_m2_package.php', path])
    proc.communicate()
    exit(proc.returncode)

if __name__ == '__main__':
    cli()