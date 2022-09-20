# Copyright 2019 GEOSIRIS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os 
import re
import shutil
import sys

if __name__ == "__main__":
    print("USAGE : python renamePkg.py [PKG_NAME::VERSION]+")
    print("\t example : python renamePkg.py common::2.3 resqml::2.2")

    rgx_suffix_pkg = "(v2)?"

    pkg_versions = {}

    for arg in sys.argv[1:]:
        print("ARG found : " + arg)
        if arg is not None and "::" in arg:
            for result in re.findall(r"([\w]+)::([\d\w\.]+)", arg):
                pkg_versions[result[0]] = result[1].replace('.', '_')

    for pkg, version in pkg_versions.items():
        print(pkg, ":", version)

    try:
        os.makedirs("../target/generated-sources/jaxb", mode=0o777)
    except:
        pass

    for r, d, f in os.walk("../target/generated-sources/jaxb"):
        for file in f:
            if file.endswith('.java'):
                filePath = os.path.join(r, file).replace("\\", "/")

                f_content = ""

                with open(file=filePath, mode='r', encoding='utf8') as f:
                    f_content = f.read()

                # OPC Replacement
                f_content = re.sub(rf'org(?P<separator>[\./])openxmlformats[\./]schemas[\./]_package[\./]_2006[\./](metadata[\./])?(?P<package>relationships|content_types|core_properties)', rf'energyml\g<separator>\g<package>', f_content)

                # Packages Replacement
                for pkg, version in pkg_versions.items():
                    f_content = re.sub(rf'org(?P<separator>[\./])energistics[\./]energyml[\./]data[\./](?P<package>{pkg}){rgx_suffix_pkg}', rf'energyml\g<separator>\g<package>{version}', f_content)
                    
                    # In class comments
                    f_content = re.sub(r'type="{http://www.energistics.org/energyml[\./]data[\./](?P<package>'+pkg+r')'+rgx_suffix_pkg+r'}(?P<className>[\w]+)"', rf'type="energyml.\g<package>{version}.\g<className>"', f_content)

                with open(file=filePath, mode='w', encoding='utf8') as f:
                    f.write(f_content)

    for r, d, f in os.walk("../target/generated-sources/jaxb"):
        for directory in d:
            for pkg, version in pkg_versions.items():
                if re.match(rf"{pkg}{rgx_suffix_pkg}$", directory):
                    directoryPath = os.path.join(r, directory).replace("\\", "/")
                    newDir = re.sub(rf'org(?P<separator>[\./])energistics[\./]energyml[\./]data[\./](?P<package>{pkg}){rgx_suffix_pkg}', rf'energyml\g<separator>\g<package>{version}', directoryPath)
                    print("DIR : ", directoryPath)
                    print("\t-->", newDir)
                    shutil.move(directoryPath, newDir)
                    break

            # For OPC
            if re.match(rf"relationships$", directory):
                directoryPath = os.path.join(r, directory).replace("\\", "/")
                newDir = re.sub(rf'org(?P<separator>[\./])openxmlformats[\./]schemas[\./]_package[\./]_2006[\./](metadata[\./])?(?P<package>relationships|content_types|core_properties)', rf'energyml\g<separator>\g<package>', directoryPath)
                print("DIR : ", directoryPath)
                print("\t-->", newDir)
                shutil.move(directoryPath, newDir)
                break