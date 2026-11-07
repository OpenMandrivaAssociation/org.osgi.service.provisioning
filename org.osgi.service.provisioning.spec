Name:		org.osgi.service.provisioning
Version:	1.2.0
Release:	1
Summary:	OSGi Initial Provisioning API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.provisioning/%{version}/org.osgi.service.provisioning-%{version}-sources.jar

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Initial Provisioning 1.2. ProvisioningService shares the
provisioning dictionary between the management agent and the bundles
that collect device information. The package version is 1.2. There are
no framework types. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
cp -p LICENSE LICENSE.osgi
cp -p about.html about.html.osgi
rm -rf META-INF org
mkdir -p src/main/java src/main/resources
mv LICENSE.osgi LICENSE
mv about.html.osgi about.html
python - %{SOURCE0} <<'PY'
import sys
import zipfile
from pathlib import Path

root = Path("src/main/java/org/osgi/service/provisioning")
res = Path("src/main/resources/org/osgi/service/provisioning")
root.mkdir(parents=True)
res.mkdir(parents=True)
with zipfile.ZipFile(sys.argv[1]) as zf:
    for name in (
        "org/osgi/service/provisioning/ProvisioningService.java",
        "org/osgi/service/provisioning/package-info.java",
    ):
        (root / Path(name).name).write_bytes(zf.read(name))
    info = zf.read("org/osgi/service/provisioning/packageinfo")
(res / "packageinfo").write_bytes(info)
if info != b"version 1.2\n":
    raise SystemExit("packageinfo " + repr(info))
javas = list(Path("src/main/java").rglob("*.java"))
if len(javas) != 2:
    raise SystemExit("java files " + str(len(javas)))
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.provisioning</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.provisioning</name>
  <description>OSGi Initial Provisioning.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
poms = sorted(str(path) for path in Path(".").rglob("pom.xml"))
if poms != ["pom.xml"]:
    raise SystemExit("poms " + str(poms))
for needle in (
    "<artifactId>org.osgi.service.provisioning</artifactId>",
    "<version>%{version}</version>",
    "<release>8</release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin", "<dependencies>"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.provisioning-%{version}.jar --describe-module org.osgi.service.provisioning > module-describe.txt
grep -q '^org.osgi.service.provisioning' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.provisioning-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    info = zf.read("org/osgi/service/provisioning/packageinfo")
if info != b"version 1.2\n":
    raise SystemExit("jar packageinfo " + repr(info))
PY

%files -f .mfiles
%doc LICENSE about.html
