# nexus2-maven-metadata-fix

Add `maven-metadata.xml` in Nexus 2 artifacts

Some tools expect maven2 artifacts in Nexus to have a 
maven-metadata.xml even though e.g. sbt doesn't build that.

To provide fresh maven-metadata for a list of artifacts do:

    fab -H <nexus-server>  build_metas:<file with list of paths>,<group_id>

The `<file with list of paths>` is a text file with a path on
each line. The paths are absolute paths to directories where
the maven-metadata.* files should go, i.e. the parent directory
for the versions of artifacts.

To provide fresh maven-metadata for all subdirectories of a root
directory which match a certain glob pattern, do:

    fab -H <nexus-server>  build_metas_for:<root directory>,<glob pattern>,<group_id>

Asterisks etc in the `<glob pattern>` must be escaped.

Since there are files called `maven-metadata.xml` at several
levels in the file structure, either task will look for the string
`<latest>` in such files, and assume that it's a valid directory
to refresh the metadata in, if it finds that tag, and fail if not.

It will then create a new `maven-metadata.xml` with all
subdirectory names in order as `<versions>`, and the
last version as `<latest>` and `<release>`.

Besides the `maven-metadata.xml`, the tasks will also generate
appropriate `maven-metadata.xml.md5` and `maven-metadata.xml.sha1`.
