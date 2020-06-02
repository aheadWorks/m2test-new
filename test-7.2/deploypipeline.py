
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
        elif line.find('deploy-pipelines') != -1:
            firstIndex = index
        elif line.find('*deployPipelines') != -1:
            lastIndex = index + 1
    print(firstIndex)
    print(lastIndex)
    del lines[firstIndex:lastIndex]
    del lines[firstInstructionIndex:lastInstructionIndex]
    w = open("bitbucket-pipelines.yml", 'w')
    w.writelines([item for item in lines])
    w.close()


def push(url):
    subprocess.Popen(['git', 'clone', url]).communicate()
    subprocess.Popen(['cp', '-f', '../bitbucket-pipelines.yml']).communicate()
    readFile = open("bitbucket-pipelines.yml")
    lines = readFile.readlines()
    readFile.close()
    if lines[-1][0:1] == '#':
        w = open("bitbucket-pipelines.yml", 'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
    subprocess.Popen(['git', 'add', "bitbucket-pipelines.yml"]).communicate()
    subprocess.Popen(['git', 'commit', '-m' "[SKIP CI] update bitbucket-pipelines.yml"]).communicate()
    subprocess.Popen(['git', 'push']).communicate()
    os.system('cd ..')



os.system('apk add git')
f = open('repositories')
repositories = json.load(f)
f.close()
repositories = repositories['values']
url_list = list()
for item in repositories:
    url = item['links']['clone'][1]['href']
    if url.find('module') != -1:
        url_list.append(url)
for url in url_list:
    os.system('mkdir tmpgit')
    if url.find('module-boilerplate') == -1:
        removeDeployPipeline()
        os.system('cd tmpgit')
        push(url)
    os.system('rm -r tmpgit')