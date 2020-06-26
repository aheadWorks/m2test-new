#!/usr/bin/env python3
import subprocess
import os
import json


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def add_license_to_php_files(path, license_template):
    with cd(path):
        with open(path + '/composer.json') as f:
            composer = json.load(f)
        with open(path + "/registration.php") as reg:
            l = reg.readlines()
            for line in l:
                if line.find("Aheadworks_") != -1:
                    package_name =line.split("_")[1][:-2]
        license_result = list()
        for line in license_template:
            if line.find("package") != -1:
                print(line)
                print(package_name)
                line = line.replace("<PACKAGE_NAME>", package_name[:-1])
            if line.find("version") != -1:
                print(line)
                print(composer["version"])
                line = line.replace("<VERSION>", composer["version"])
            license_result.append(line)
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".php"):
                    with open(os.path.join(root, file)) as f:
                        original_lines = f.readlines()
                    result_lines = list()
                    result_lines.append(original_lines[0])
                    license_result[-1] += '\n'
                    for line in license_result:
                        result_lines.append(line)
                    for line in original_lines[1:]:
                        result_lines.append(line)
                    result = open(os.path.join(root, file), 'w')
                    result.writelines([item for item in result_lines])
                    result.close()


def ecommerce_build():
    with open('request') as r:
        request = r.readlines()[0]
    with open('./composer.json') as f:
        composer = json.load(f)
    with open("/license.tmp") as t:
        license_template = t.readlines()
    list_of_modules = list()
    core_module_name = composer['name']
    list_of_modules.append(core_module_name.split('/')[1])
    if composer.get('suggests') != None:
        for module in composer['suggests']:
            if module.find(core_module_name) != -1:
                list_of_modules.append(module.split('/')[1])
    os.system("mkdir -p app/code/Aheadworks")
    with cd('app/code/Aheadworks'):
        for module in list_of_modules:
            proc = subprocess.Popen(['git', 'clone', 'git@bitbucket.org:awm2ext/' + module + '.git'])
            proc.communicate()
            if proc.returncode != 0:
                raise click.ClickException("Failed download module " + module)
            path_to_composer = module + "/composer.json"
            path_to_registration = module + "/registration.php"
            ec1 = os.path.isfile(path_to_composer)
            ec2 = os.path.isfile(path_to_registration)
            if not (ec1) or not (ec2):
                raise click.ClickException(module + " haven't build")
            proc = subprocess.Popen(['rm', module + '/bitbucket-pipelines.yml'])
            proc.communicate()
            add_license_to_php_files(os.getcwd() + '/' + module, license_template)
            proc = subprocess.Popen(['rm', module + '/.gitignore'])
            os.system("rm -rf ./" + module + "/.git")
            os.system(
                "echo See https://ecommerce.aheadworks.com/end-user-license-agreement/ >> " + module + "/license.txt")
            proc.communicate()
            with open(path_to_registration) as f2:
                lines = f2.readlines()
            for line in lines:
                if line.find("headworks_") != -1:
                    module_directory_name = line.strip('\"\'').split('_')[1][0:-3]
            if core_module_name.split('/')[1] == module:
                result_name = module_directory_name + '-' + composer['version']
            os.system('mv ' + module + ' ' + module_directory_name)
    os.system('apk add zip')
    cd('../../..')
    os.system('echo $BB_AUTH_STRING')
    os.system('zip -r aw_m2_' + result_name + '.community-editon.zip app')
    ce = '"aw_m2_' + result_name + '.community-editon.zip"'
    os.system('zip -r aw_m2_' + result_name + '.enterprise-editon.zip app')
    ee = '"aw_m2_' + result_name + '.enterprise-editon.zip"'
    os.system(
        'curl -X POST "https://sednevIgor:KwkCyHNdwBHshNGtqtuy@' + request.strip() + '" ' + '--form files=@"' + ce + '"')
    os.system(
        'curl -X POST "https://sednevIgor:KwkCyHNdwBHshNGtqtuy@' + request.strip() + '" ' + '--form files=@"' + ee + '"')


ecommerce_build()