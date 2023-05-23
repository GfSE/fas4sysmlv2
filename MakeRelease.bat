@echo off
REM   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
REM   Licensed under the Apache License, Version 2.0 (the "License");
REM   you may not use this file except in compliance with the License.
REM   You may obtain a copy of the License at
REM        http://www.apache.org/licenses/LICENSE-2.0  
REM   Unless required by applicable law or agreed to in writing, software
REM   distributed under the License is distributed on an "AS IS" BASIS,
REM   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM   See the License for the specific language governing permissions and
REM   limitations under the License.

MKDIR RELEASE

MKDIR RELEASE\src
MKDIR RELEASE\src\io
MKDIR RELEASE\src\core

ROBOCOPY /S src\io RELEASE\src\io
ROBOCOPY /S src\core RELEASE\src\core
COPY LICENSE RELEASE
COPY doc\user-manuals\FAS4SysMLv2_InstallationAndUse.txt RELEASE
ECHO FAS Plugin for SySML v2 version 0.9.2 > RELEASE\Version.txt
REM Version 1.x will be reserved for the time after release of a SysML v2 standard.