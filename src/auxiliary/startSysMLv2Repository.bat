
@echo off
::   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
::   Licensed under the Apache License, Version 2.0 (the "License");
::   you may not use this file except in compliance with the License.
::   You may obtain a copy of the License at
::        http://www.apache.org/licenses/LICENSE-2.0  
::   Unless required by applicable law or agreed to in writing, software
::   distributed under the License is distributed on an "AS IS" BASIS,
::   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
::   See the License for the specific language governing permissions and
::   limitations under the License.

:: Replace with your own path:
set SYSMLV2APIPATH=C:\temp\SysML-v2-API-Services-master

echo Starting docker desktop...
:: Adapt path if necessary ...
start "x" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout 15 > nul
echo Done.

echo Starting docker container...
docker start sysml2-postgres > nul
echo Done.
c:
echo Starting SysML v2 API services ...
cd %SYSMLV2APIPATH%
start /b sbt run > nul 2>&1
timeout 15 > nul
echo Done.
echo Loading the the REST API interface in a web browser to initialize the API ..
start "x" "http://localhost:9000/docs/"
echo Done.
echo This window will stay open. 
echo To shut down the API, hit the return key in this window. Then close the window.
pause > nul