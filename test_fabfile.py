from datetime import datetime
import unittest
import fabfile


class ArtifactTests(unittest.TestCase):
    def test_one_version(self):
        a = fabfile.Artifact()
        a.versions(['1.0.0'])

        self.assertEqual(a['versions'], ['1.0.0'])
        self.assertEqual(a['latest'], '1.0.0')
        self.assertEqual(a['release'], '1.0.0')

    def test_four_versions(self):
        a = fabfile.Artifact()
        a.versions(['1.1-A', '1.10-B', '1.2-C', '0.9.9-X'])

        self.assertEqual(a['versions'], ['0.9.9-X', '1.1-A', '1.2-C', '1.10-B'])
        self.assertEqual(a['latest'], '1.10-B')
        self.assertEqual(a['release'], '1.10-B')

    def test_arguments(self):
        a = fabfile.Artifact(
            group_id='GRP',
            artifact_id='ART',
            timestamp=datetime(2017, 9, 1, 12, 44, 40)
        )

        self.assertEqual('GRP', a['group_id'])
        self.assertEqual('ART', a['artifact_id'])
        self.assertEqual('20170901124440', a['timestamp'])

    def test_files(self):
        a = fabfile.Artifact('G', 'A', datetime(2000, 1, 1, 0, 0, 0))
        a.versions(['1'])

        expected = {
            'maven-metadata.xml': (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<metadata modelVersion="1.1.0">\n'
                '  <groupId>G</groupId>\n'
                '  <artifactId>A</artifactId>\n'
                '  <versioning>\n'
                '    <latest>1</latest>\n'
                '    <release>1</release>\n'
                '    <versions>\n'
                '      <version>1</version>\n'
                '    </versions>\n'
                '    <lastUpdated>20000101000000</lastUpdated>\n'
                '  </versioning>\n'
                '</metadata>\n').encode(),
            'maven-metadata.xml.md5': '5b5f4083ad1371b0baa603278c157d55',
            'maven-metadata.xml.sha1': '255c1614a47eae658dfcf539a16849af8e2058da',
        }

        self.maxDiff = None
        self.assertEqual(a.files(), expected)


if __name__ == '__main__':
    unittest.main()
