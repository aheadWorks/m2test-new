
import json
import subprocess
import os

def removeDeployPipeline():
    readFile = open("bitbucket-pipelines.yml")
    lines = readFile.readlines()
    readFile.close()
    firstInstructionIndex = lines.index('    - step: &deployPipelines') - 1
    lastInstructionIndex = lines.index('          - python3 /deploypipline.py')
    del lines[firstInstructionIndex:lastInstructionIndex]
    firstIndex = lines.index('    # copy this file to all modules') - 1
    lastIndex = lines.index('      - step: *deployPipelines')
    del lines[firstIndex:lastIndex]
    w = open("bitbucket-pipelines.yml", 'w')
    w.writelines([item for item in lines])
    w.close()


def push():
    subprocess.Popen(['git', 'rm', '--cached', 'bitbucket-pipelines.yml']).communicate()
    readFile = open("bitbucket-pipelines.yml")
    lines = readFile.readlines()
    readFile.close()
    if lines[-1][0:1] == '#':
        w = open("bitbucket-pipelines.yml", 'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
    os.system('echo "#" `date` >> bitbucket-pipelines.yml')
    subprocess.Popen(['git', 'add', 'bitbucket-pipelines.yml']).communicate()
    subprocess.Popen(['git', 'commit', '-m', '[skip ci] update pipeline'])
    os.system('git remote -v')
    os.system('git fetch --unshallow')
    os.system('git push --force')

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
    process = subprocess.Popen(['git', 'remote', 'set-url', '--add', '--push', 'origin', url]).communicate()
    if url.find('module-boilerplate') != -1:
        push()
removeDeployPipeline()
push()