
import json
import subprocess
import os

def removeDeployPipeline():
    readFile = open("bitbucket-pipelines.yml")
    lines = readFile.readlines()
    readFile.close()
    for index, line in enumerate(lines):
        if line.find('&deployPipelines') != -1:
            firstInstructionIndex = index
        elif line.find('deploypipeline.py') != -1:
            lastInstructionIndex = index + 1
        elif line.find('deploy-pipeline') != -1:
            firstIndex = index
        elif line.find('*deployPipelines') != -1:
            lastIndex = index + 1
    del lines[firstIndex:lastIndex]
    del lines[firstInstructionIndex:lastInstructionIndex]
    w = open("bitbucket-pipelines.yml", 'w')
    w.writelines([item for item in lines])
    w.close()


def push(url):
    subprocess.Popen(['git', 'clone', url, '-b', 'develop']).communicate()
    subprocess.Popen(['ls', '-la']).communicate()
    module = url.split('/')[-1].replace('.git', '')
    os.chdir(module)
    subprocess.Popen(['cp', '-f', '../../bitbucket-pipelines.yml', '.']).communicate()
    removeDeployPipeline()
    readFile = open("bitbucket-pipelines.yml")
    lines = readFile.readlines()
    readFile.close()
    if lines[-1][0:1] == '#':
        w = open("bitbucket-pipelines.yml", 'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
    os.system('git config --global user.email "bot@raveinfosys.com"')
    os.system('git config --global user.name "Automatic update"')
    subprocess.Popen(['git', 'add', "bitbucket-pipelines.yml"]).communicate()
    subprocess.Popen(['git', 'commit', '-m' "[SKIP CI] update bitbucket-pipelines.yml"]).communicate()
    subprocess.Popen(['git', 'push']).communicate()
    os.chdir("../..")



os.system('apk add git')
f = open('repositories')
repositories = json.load(f)
f.close()
repositories = repositories['values']
f = open('repositories2')
repositories2 = json.load(f)
f.close()
repositories2 = repositories2['values']
url_list = list()
for item in repositories + repositories2:
    url = item['links']['clone'][1]['href']
    if url.find('module') != -1:
        url_list.append(url)
for url in url_list:
    os.system('mkdir tmpgit')
    if url.find('module-boilerplate') == -1:
        os.chdir("./tmpgit")
        push(url)
    os.system('rm -r tmpgit')