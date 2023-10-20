@echo off
rem   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
rem   Licensed under the Apache License, Version 2.0 (the "License");
rem   you may not use this file except in compliance with the License.
rem   You may obtain a copy of the License at
rem        http://www.apache.org/licenses/LICENSE-2.0  
rem   Unless required by applicable law or agreed to in writing, software
rem   distributed under the License is distributed on an "AS IS" BASIS,
rem   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
rem   See the License for the specific language governing permissions and
rem   limitations under the License.

rem   This code monitors SQL actitvity inside the Postgres container


cls
python queryDatabaseActivity.py