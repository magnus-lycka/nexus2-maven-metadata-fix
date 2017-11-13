from __future__ import print_function

import hashlib
import jinja2
from datetime import datetime
from fabric.api import task, env, run, sudo, put, cd
from os import unlink, path


if path.exists(path.expanduser('~/.ssh/config')):
    env.use_ssh_config = True


class Artifact(dict):
    def __init__(self, group_id='', artifact_id='', timestamp=None):
        self['group_id'] = group_id
        self['artifact_id'] = artifact_id
        if timestamp is None:
            timestamp = datetime.now()
        self['timestamp'] = timestamp.strftime('%Y%m%d%H%M%S')

    def versions(self, versions):
        self['versions'] = sorted(versions, key=self.version_key)
        self['latest'] = self['versions'][-1]
        self['release'] = self['versions'][-1]

    @staticmethod
    def version_key(version):
        def num(x):
            if x.isdigit():
                return int(x)
            return x

        return [num(x) for x in version.replace('-', '.').split('.')]

    def files(self):
        self._xml()
        return {
            'maven-metadata.xml': self.xml,
            'maven-metadata.xml.md5': self.md5(),
            'maven-metadata.xml.sha1': self.sha1()
        }

    def _xml(self):
        with open('./maven-metadata.xml.template') as f:
            template = jinja2.Template(f.read())
        self.xml = template.render(**self).encode()

    def md5(self):
        return hashlib.md5(self.xml).hexdigest()

    def sha1(self):
        return hashlib.sha1(self.xml).hexdigest()


@task
def find_meta(root):
    return run('find {} -name maven-metadata.xml'.format(root))


@task
def check(directory):
    with cd(directory):
        run("grep -q '<latest>' maven-metadata.xml")


@task
def list_versions(directory):
    with cd(directory):
        return run('find * -mindepth 0 -maxdepth 0 -type d')


@task
def build_meta(directory, group_id):
    check(directory)
    artifact_id = directory.split('/')[-1]
    versions = list_versions(directory).split()
    if not versions:
        print("Found no sub-directories in", directory)
        return
    art = Artifact(group_id, artifact_id)
    art.versions(versions)
    with cd(directory):
        for fn, content in art.files().items():
            with open(fn, 'w') as f:
                f.write(content)
            put(fn, fn, use_sudo=True)
            sudo('chown nexus:nexus ' + fn)
            unlink(fn)


@task
def find_dirs(parent, pattern):
    return run(
        "find {} -mindepth 1 -maxdepth 1 -name '{}' -type d".format(parent, pattern)
    )


@task
def build_metas(dirfile, group_id):
    """
    Build maven metadata for Nexus 2 artifacts.
    Needs access to file system.

    :param dirfile: Text file with a list of artifact paths
    :param group_id: Nexus group id
    """
    with open(dirfile) as f:
        for directory in f:
            build_meta(directory.rstrip(), group_id)


@task
def build_metas_for(parent, pattern, group_id):
    """
    Build maven metadata for Nexus 2 artifacts.
    Needs access to file system.

    :param parent: Parent directory for Nexus artifacts
    :param pattern: glob pattern for artifact names
    :param group_id: Nexus group id
    """
    for directory in find_dirs(parent, pattern).split():
        if directory.strip():
            build_meta(directory.strip(), group_id)
