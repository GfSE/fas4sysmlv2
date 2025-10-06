//   Copyright 2022 Gesellschaft fuer Systems Engineering e.V. (GfSE)
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//        http://www.apache.org/licenses/LICENSE-2.0  
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.

// Example System, modelled manually. 
// It exemplifies the target model structure to be created by
// an envisioned future version of the FAS plugin.

package '00 Domain Model' {
    item def Backprogramm;
    item def Energie;
    item def KuchenEntnahmeCode;
    item def Kuchenliste;
    item def Kuchenpreis;
    item def Preisliste;
    item def ID;
}
package '01 Systems Analysis' {
    package 'Use Cases' {
        use case def BackAutomatenMitEnergieVersorgen {
            subject backSystem : System::Backsystem;
            perform backSystem.energieAufnehmen;
            perform backSystem.energieVerteilen;
            flow of '00 Domain Model'::Energie from energieAufnehmen.energie to energieVerteilen.energie;
            view BackAutomatenMitEnergieVersorgen;
        }
        use case def BackVorgangStarten {
            subject backSystem : System::Backsystem;
            perform backSystem.tagesAngebotLaden;
            perform backSystem.kuchenWahlAbfragen;
            perform backSystem.zahlungAnnehmen;
            perform backSystem.backProgrammErstellen;
            perform backSystem.energieZufuhrStarten;
            perform backSystem.kuchenCodeErzeugen;
            perform backSystem.kuchenCodeAusgeben;
            perform backSystem.backMaschineStarten;
            flow of '00 Domain Model'::Backprogramm from backProgrammErstellen.backprogramm to backMaschineStarten.backprogramm;
            flow of '00 Domain Model'::Energie from energieZufuhrStarten.energie to backMaschineStarten.energie;
            flow of '00 Domain Model'::KuchenEntnahmeCode from kuchenCodeErzeugen.kuchenentnahmecode to kuchenCodeAusgeben.kuchenentnahmecode;
            flow of '00 Domain Model'::Kuchenliste from kuchenWahlAbfragen.kuchenliste to backProgrammErstellen.kuchenliste;
            flow of '00 Domain Model'::Kuchenpreis from kuchenWahlAbfragen.kuchenpreis to zahlungAnnehmen.kuchenpreis;
            flow of '00 Domain Model'::Kuchenliste from tagesAngebotLaden.kuchenliste to kuchenWahlAbfragen.kuchenliste;
            flow of '00 Domain Model'::Preisliste from tagesAngebotLaden.preisliste to kuchenWahlAbfragen.preisliste;
            flow of '00 Domain Model'::ID from zahlungAnnehmen.id to backProgrammErstellen.id;
            flow of '00 Domain Model'::ID from zahlungAnnehmen.id to kuchenCodeErzeugen.id;
            view BackVorgangStarten;
        }
    }
    package Context {
        part def Backsystemkontext {
            part backSystem : System::Backsystem;
            part hungrigePerson;
            part internet;
            part zahlungsmittel;
            part stromnetz;
            connect hungrigePerson to backSystem;
            connect internet to backSystem;
            connect zahlungsmittel to backSystem;
            connect stromnetz to backSystem;
            use case backAutomatenMitEnergieVersorgen : 'Use Cases'::BackAutomatenMitEnergieVersorgen {
                subject :>> backSystem = backSystem;
                actor :>> stromnetz = stromnetz;
            }
            use case backVorgangStarten : 'Use Cases'::BackVorgangStarten {
                subject :>> backSystem = backSystem;
                actor :>> hungrigePerson = hungrigePerson;
                actor :>> zahlungsmittel = zahlungsmittel;
                actor :>> internet = internet;
            }
            view Backsystemkontext;
        }
    }
    package System {
        part def Backsystem {
            action backMaschineStarten {
                in backprogramm;
                in energie;
            }
            action backProgrammErstellen {
                in kuchenliste;
                in id;
                out backprogramm;
            }
            action energieZufuhrStarten { out energie; }
            action kuchenCodeAusgeben { in kuchenentnahmecode; }
            action kuchenCodeErzeugen {
                in id;
                out kuchenentnahmecode;
            }
            action kuchenWahlAbfragen {
                in kuchenliste;
                in preisliste;
                out kuchenliste1;
                out kuchenpreis;
            }
            action tagesAngebotLaden {
                out kuchenliste;
                out preisliste;
            }
            action zahlungAnnehmen {
                in kuchenpreis;
                out id;
                out id1;
            }
            action energieAufnehmen { out energie; }
            action energieVerteilen { in energie; }
        }
    }
}
package '03 System Architecture' {
    #functionalBlock part def functionalSystem :> '01 Systems Analysis'::System::Backsystem {
        #functionalBlock part Backautomatik {
            perform action backMaschineStarten;
            port p1;
            port p2;
        }
        #functionalBlock part Energieverteilung {
            perform action energieVerteilen;
            perform action energieZufuhrStarten;
            port p1;
            port p2;
        }
        #functionalBlock part IOHungrigePerson {
            perform action kuchenCodeAusgeben;
            perform action kuchenWahlAbfragen;
            port p1;
            port p2;
            port p3;
            port p4;
        }
        #functionalBlock part IOStromnetz {
            perform action energieAufnehmen;
            port p1;
        }
        #functionalBlock part IOZahlungsmittel {
            perform action zahlungAnnehmen;
            port p1;
            port p2;
        }
        #functionalBlock part Kuchenverwaltung {
            perform action kuchenCodeErzeugen;
            perform action tagesAngebotLaden;
            perform action backProgrammErstellen;
            port p1;
            port p2;
            port p3;
            port p4;
            port p5;
        }
        flow of '00 Domain Model'::Energie from Energieverteilung.p1 to Backautomatik.p1;
        flow of '00 Domain Model'::Kuchenpreis from IOHungrigePerson.p1 to IOZahlungsmittel.p2;
        flow of '00 Domain Model'::Kuchenliste from IOHungrigePerson.p2 to Kuchenverwaltung.p4;
        flow of '00 Domain Model'::Energie from IOStromnetz.p1 to Energieverteilung.p2;
        flow of '00 Domain Model'::ID from IOZahlungsmittel.p1 to Kuchenverwaltung.p5;
        flow of '00 Domain Model'::Backprogramm from Kuchenverwaltung.p1 to Backautomatik.p2;
        flow of '00 Domain Model'::KuchenEntnahmeCode from Kuchenverwaltung.p2 to IOHungrigePerson.p3;
        flow of '00 Domain Model'::Kuchenliste from Kuchenverwaltung.p2 to IOHungrigePerson.p3;
        flow of '00 Domain Model'::Preisliste from Kuchenverwaltung.p3 to IOHungrigePerson.p4;
        view functionalSystem;
    }
    part def FunctionalBlock;
    part functionalBlocks [*] : FunctionalBlock;
    metadata def <functionalBlock> FunctionalBlockMetadata :> Metaobjects::SemanticMetadata {
        :>> baseType = functionalBlocks meta SysML::Systems::PartUsage;
    }
}
