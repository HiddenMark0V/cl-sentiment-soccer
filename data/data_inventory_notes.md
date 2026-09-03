# Dateninventar: Prüfprotokoll

Quelle: `/workspace/scratch/a736993fd63c/SocCor-main/SocCor/Textdata/raw_data/Games/Sportschau`

Dateien: 78; Segmente: 44969. Status: {'ja': 70, 'unklar': 8}.

## Wiederholen

Python >= 3.9; ausschließlich Standardbibliothek. Im Projektordner: `python src/data_inventory.py`. Andere Pfade mit `--raw-dir PFAD` und `--output docs/data_inventory.csv` angeben. Vorhandene Ausgaben werden ersetzt. Alle JSON-Dateien im angegebenen Rohdatenordner werden rekursiv eingelesen.

## Kriterien

- Zeitwerte bleiben Sekunden; start_min bedeutet Minimum, nicht Minuten.
- segments zählt sämtliche Listeneinträge, auch leere Texte. Unbekannte Werte bleiben in der CSV leer; eine leere Datei/Liste erhält segments=0.
- nein: leer, nicht lesbar, ungültiges JSON, falsche Struktur, fehlende Pflichtfelder, falsche Datentypen, ungültige/negative Zeiten, end < start oder überhaupt kein nichtleerer Text.
- unklar: sonst technisch lesbar, aber Dateiname nicht zuordenbar, Beginn > 60 s, Zeitspanne < 2700 s oder > 4200 s, oder Segmentlücke > 60 s. Zusatzphasen und Sprechpausen sind mögliche Ursachen, keine bestätigten Fehler.
- ja: keine der obigen Bedingungen. Nur vorläufige technische Plausibilität; keine Garantie einer vollständigen Halbzeit oder korrekter Transkription.
- Einzelne leere Texte, Nulldauern und Rücksprünge werden gezählt, ohne allein daraus fehlende Aufnahmeabschnitte abzuleiten.
- geprüft bleibt nein: keine vollständige manuelle Prüfung gegen Audio. Ein erneuter Lauf übernimmt keine früheren manuellen CSV-Einträge.
- Fehlende Partnerdateien und doppelte match_id/half-Kombinationen werden separat gemeldet; sie verändern nicht den Status der einzelnen Datei.
- Die Inventur bezieht sich nur auf vorhandene Dateien, nicht auf einen externen Soll-Spielplan. Rohdaten werden ausschließlich gelesen.

## Auffälligkeiten je Datei

- `02_HUN_SUI_first_half.json`: Leerer Text: 6; Segmentdauer null: 6; Rücksprung der Startzeit in Dateireihenfolge: 2
- `02_HUN_SUI_second_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 5
- `03_ESP_CRO_first_half.json`: Leerer Text: 14; Segmentdauer null: 14; Rücksprung der Startzeit in Dateireihenfolge: 1
- `03_ESP_CRO_second_half.json`: Leerer Text: 9; Segmentdauer null: 9; Rücksprung der Startzeit in Dateireihenfolge: 1
- `04_ITA_ALB_first_half.json`: Leerer Text: 4; Segmentdauer null: 4
- `04_ITA_ALB_second_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 2
- `07_POL_NED_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 7; Leerer Text: 2; Segmentdauer null: 2
- `07_POL_NED_second_half.json`: Leerer Text: 11; Segmentdauer null: 11; Rücksprung der Startzeit in Dateireihenfolge: 4
- `08_AUT_FRA_first_half.json`: Leerer Text: 9; Segmentdauer null: 9; Rücksprung der Startzeit in Dateireihenfolge: 1
- `08_AUT_FRA_second_half.json`: Leerer Text: 12; Segmentdauer null: 12
- `09_BEL_SVK_first_half.json`: Leerer Text: 6; Segmentdauer null: 6; Rücksprung der Startzeit in Dateireihenfolge: 4
- `09_BEL_SVK_second_half.json`: Leerer Text: 4; Segmentdauer null: 4; Rücksprung der Startzeit in Dateireihenfolge: 4
- `11_TUR_GEO_first_half.json`: Leerer Text: 14; Segmentdauer null: 14; Rücksprung der Startzeit in Dateireihenfolge: 5
- `11_TUR_GEO_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 4; Leerer Text: 3; Segmentdauer null: 3
- `12_POR_CZE_first_half.json`: Leerer Text: 6; Segmentdauer null: 6; Rücksprung der Startzeit in Dateireihenfolge: 2
- `12_POR_CZE_second_half.json`: Leerer Text: 7; Segmentdauer null: 7; Rücksprung der Startzeit in Dateireihenfolge: 4
- `13_SCO_SUI_first_half.json`: Leerer Text: 11; Segmentdauer null: 11; Rücksprung der Startzeit in Dateireihenfolge: 1
- `13_SCO_SUI_second_half.json`: Leerer Text: 19; Segmentdauer null: 19
- `15_CRO_ALB_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 7; Leerer Text: 8; Segmentdauer null: 8
- `15_CRO_ALB_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 10; Leerer Text: 7; Segmentdauer null: 7
- `16_ESP_ITA_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 2; Leerer Text: 5; Segmentdauer null: 5
- `16_ESP_ITA_second_half.json`: Leerer Text: 3; Segmentdauer null: 3; Rücksprung der Startzeit in Dateireihenfolge: 1
- `17_DEN_ENG_first_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 2
- `17_DEN_ENG_second_half.json`: Leerer Text: 6; Segmentdauer null: 6; Rücksprung der Startzeit in Dateireihenfolge: 1
- `19_POL_AUT_first_half.json`: Leerer Text: 7; Segmentdauer null: 7; Rücksprung der Startzeit in Dateireihenfolge: 3
- `19_POL_AUT_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 2; Leerer Text: 6; Segmentdauer null: 6
- `20_NED_FRA_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 3; Leerer Text: 5; Segmentdauer null: 5
- `20_NED_FRA_second_half.json`: Leerer Text: 9; Segmentdauer null: 9; Rücksprung der Startzeit in Dateireihenfolge: 2
- `21_SVK_UKR_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 6; Leerer Text: 3; Segmentdauer null: 3
- `21_SVK_UKR_second_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 2
- `22_BEL_ROU_first_half.json`: Leerer Text: 1; Segmentdauer null: 1; Rücksprung der Startzeit in Dateireihenfolge: 6
- `22_BEL_ROU_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 7; Leerer Text: 1; Segmentdauer null: 1
- `23_TUR_POR_first_half.json`: Leerer Text: 15; Segmentdauer null: 15; Rücksprung der Startzeit in Dateireihenfolge: 3
- `23_TUR_POR_second_half.json`: Leerer Text: 14; Segmentdauer null: 14; Rücksprung der Startzeit in Dateireihenfolge: 2
- `24_GEO_CZE_first_half.json`: Leerer Text: 4; Segmentdauer null: 4
- `24_GEO_CZE_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 3; Leerer Text: 7; Segmentdauer null: 7
- `26_SCO_HUN_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 8; Leerer Text: 7; Segmentdauer null: 7
- `26_SCO_HUN_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 3; Leerer Text: 8; Segmentdauer null: 8
- `27_ALB_ESP_first_half.json`: Leerer Text: 9; Segmentdauer null: 9
- `27_ALB_ESP_second_half.json`: Leerer Text: 3; Segmentdauer null: 3; Rücksprung der Startzeit in Dateireihenfolge: 3
- `28_CRO_ITA_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 6; Leerer Text: 1; Segmentdauer null: 1
- `28_CRO_ITA_second_half.json`: Leerer Text: 4; Segmentdauer null: 4; Rücksprung der Startzeit in Dateireihenfolge: 1
- `29_ENG_SVN_first_half.json`: Leerer Text: 18; Segmentdauer null: 18; Rücksprung der Startzeit in Dateireihenfolge: 5
- `29_ENG_SVN_second_half.json`: Leerer Text: 20; Segmentdauer null: 20; Rücksprung der Startzeit in Dateireihenfolge: 3; Kurze Zeitspanne: weniger als 2700 s: 1
- `30_DEN_SRB_first_half.json`: Leerer Text: 10; Segmentdauer null: 10
- `30_DEN_SRB_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 2; Leerer Text: 8; Segmentdauer null: 8
- `31_NED_AUT_first_half.json`: Leerer Text: 6; Segmentdauer null: 6; Rücksprung der Startzeit in Dateireihenfolge: 3
- `31_NED_AUT_second_half.json`: Leerer Text: 8; Segmentdauer null: 8; Rücksprung der Startzeit in Dateireihenfolge: 3
- `32_FRA_POL_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 2; Leerer Text: 4; Segmentdauer null: 4
- `32_FRA_POL_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 1; Leerer Text: 1; Segmentdauer null: 1
- `33_SVK_ROU_first_half.json`: Leerer Text: 15; Segmentdauer null: 15; Rücksprung der Startzeit in Dateireihenfolge: 1
- `33_SVK_ROU_second_half.json`: Leerer Text: 7; Segmentdauer null: 7; Rücksprung der Startzeit in Dateireihenfolge: 2
- `34_UKR_BEL_first_half.json`: Leerer Text: 8; Segmentdauer null: 8; Rücksprung der Startzeit in Dateireihenfolge: 1
- `34_UKR_BEL_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 9; Leerer Text: 7; Segmentdauer null: 7; Zeitlücke zwischen Segmenten über 60 s: 1
- `35_GEO_POR_first_half.json`: Leerer Text: 9; Segmentdauer null: 9; Rücksprung der Startzeit in Dateireihenfolge: 1
- `35_GEO_POR_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 1; Leerer Text: 2; Segmentdauer null: 2; Zeitlücke zwischen Segmenten über 60 s: 1
- `36_CZE_TUR_first_half.json`: Leerer Text: 6; Segmentdauer null: 6; Rücksprung der Startzeit in Dateireihenfolge: 1
- `36_CZE_TUR_second_half.json`: Leerer Text: 7; Segmentdauer null: 7; Rücksprung der Startzeit in Dateireihenfolge: 2; Kurze Zeitspanne: weniger als 2700 s: 1
- `38_SUI_ITA_first_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 1
- `38_SUI_ITA_second_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 2
- `39_ESP_GEO_first_half.json`: Leerer Text: 8; Segmentdauer null: 8; Rücksprung der Startzeit in Dateireihenfolge: 2
- `39_ESP_GEO_second_half.json`: Leerer Text: 3; Segmentdauer null: 3; Rücksprung der Startzeit in Dateireihenfolge: 2
- `40_ENG_SVK_first_half.json`: Leerer Text: 6; Segmentdauer null: 6; Rücksprung der Startzeit in Dateireihenfolge: 2
- `40_ENG_SVK_second_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 3; Lange Zeitspanne: mehr als 4200 s; Zusatzphasen möglich: 1
- `41_POR_SVN_first_half.json`: Leerer Text: 10; Segmentdauer null: 10; Rücksprung der Startzeit in Dateireihenfolge: 1
- `41_POR_SVN_second_half.json`: Leerer Text: 33; Segmentdauer null: 33; Rücksprung der Startzeit in Dateireihenfolge: 7; Lange Zeitspanne: mehr als 4200 s; Zusatzphasen möglich: 1
- `42_FRA_BEL_first_half.json`: Leerer Text: 5; Segmentdauer null: 5
- `42_FRA_BEL_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 2; Leerer Text: 4; Segmentdauer null: 4
- `43_ROU_NED_first_half.json`: Leerer Text: 7; Segmentdauer null: 7; Rücksprung der Startzeit in Dateireihenfolge: 1
- `43_ROU_NED_second_half.json`: Leerer Text: 3; Segmentdauer null: 3; Rücksprung der Startzeit in Dateireihenfolge: 5
- `44_AUT_TUR_first_half.json`: Leerer Text: 5; Segmentdauer null: 5; Rücksprung der Startzeit in Dateireihenfolge: 6
- `44_AUT_TUR_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 3; Leerer Text: 4; Segmentdauer null: 4
- `46_POR_FRA_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 1; Leerer Text: 5; Segmentdauer null: 5
- `46_POR_FRA_second_half.json`: Leerer Text: 16; Segmentdauer null: 16; Rücksprung der Startzeit in Dateireihenfolge: 3; Lange Zeitspanne: mehr als 4200 s; Zusatzphasen möglich: 1
- `47_NED_TUR_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 3
- `47_NED_TUR_second_half.json`: Leerer Text: 2; Segmentdauer null: 2
- `48_ENG_SUI_first_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 1; Leerer Text: 1; Segmentdauer null: 1
- `48_ENG_SUI_second_half.json`: Rücksprung der Startzeit in Dateireihenfolge: 8; Leerer Text: 9; Segmentdauer null: 9; Lange Zeitspanne: mehr als 4200 s; Zusatzphasen möglich: 1
