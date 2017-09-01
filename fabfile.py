import hashlib
import jinja2
from datetime import datetime
from fabric.api import task, env, run, sudo, put, cd
from os import unlink

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
    art = Artifact(group_id, artifact_id)
    art.versions(list_versions(directory).split())
    with cd(directory):
        for fn, content in art.files().items():
            with open(fn, 'w') as f:
                f.write(content)
            put(fn, fn, use_sudo=True)
            sudo('chown nexus:nexus ' + fn)
            unlink(fn)


@task
def build_metas(dirfile, group_id):
    with open(dirfile) as f:
        for directory in f:
            build_meta(directory.rstrip(), group_id)
