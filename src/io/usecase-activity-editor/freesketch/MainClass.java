/* #   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0  
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
*/

import de.gfse.RealMainClass;


class MainClass {
	  public  static void main(String[] args){
		  RealMainClass theMain = new RealMainClass();
			theMain.realmain(args[0], args[1], args[2]); //args[0] = name of the folder for establishing the temporary local file structure with images and snippet geometries
			                                    //args[1] = name of the model element to link with an image snippet
			                                    //args[2] = Free Sketch Plugin Name
	  }

}

