# nexus2-maven-metadata-fix
Add maven-metadata.xml in Nexus 2 artifacts

Some tools expect maven2 artifacts in Nexus to have a 
maven-metadata.xml even though e.g. sbt doesn't build that.
