#   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0  
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

The code in this folder is made for calling the free sketch plugin.

To make it run, do the following:

1.) Get "GSON" and place the corresponding .jar file as "gson.jar" into the current folder

2.) Get the Free Sketch Plugin source code and binary* and do the following:
- Place the imageplugin.jar file into the current folder
- Copy the "rectangledesign" and "global" source folders including their subfolder structure into the current folder

3.) On Linux only: It is very important for this functionality to work that a
suitable JDK is installed and registered with the "alternatives" system
Here is one example for installing jdk-8u202-linux-x64.rpm on Ubuntu
(Precondition: jdk-8u202-linux-x64.rpm is available in the current directory):

 sudo apt-get install alien
 sudo alien --scripts jdk-8u202-linux-x64.rpm
 sudo apt install ./jdk1.8_1.8.0202-1_amd64.deb #ignore message that /usr/sbin/alternatives does not exist
 sudo update-alternatives --install "/usr/bin/java" "java" "/usr/java/jdk1.8.0_202-amd64/bin/java" 1
 sudo update-alternatives --install "/usr/bin/javac" "javac" "/usr/java/jdk1.8.0_202-amd64/bin/javac" 1

 NOTE: To remove: sudo apt purge jdk1.8


* Free Sketch Plugin home: https://sourceforge.net/projects/freesketches-for-magicdraw/