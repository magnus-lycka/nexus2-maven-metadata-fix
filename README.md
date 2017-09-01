# nexus2-maven-metadata-fix
Add maven-metadata.xml in Nexus 2 artifacts

Some tools expect maven2 artifacts in Nexus to have a 
maven-metadata.xml even though e.g. sbt doesn't build that.

To provide fresh maven-metadata for a list of artifacts do:

    fab -H <nexus-server>  build_metas:<list of paths>,<group_id>

The paths are absolute paths to directories where the
maven-metadata.* files should go, i.e. the parent directory
for the versions of artifacts.
