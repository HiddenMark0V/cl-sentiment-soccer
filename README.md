# Sentimentanalyse deutscher Fußballkommentare

## Ziel und aktueller Stand

Das Projekt untersucht die Stimmung in deutschen Fußballkommentaren aus Sportschau-Transkripten. Der aktuelle Stand umfasst einen Loader für die Transkriptdateien sowie eine reproduzierbare kontinuierliche Zeitlogik über beide Halbzeiten.

## Installation unter Windows PowerShell

Vorausgesetzt wird Python 3.11. Die virtuelle Umgebung wird im Projektordner erstellt, aktiviert und anschließend mit den Abhängigkeiten aus `requirements.txt` ausgestattet:

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Datenstruktur

- Primärer Analysebestand: `data/cleaned_data/Sportschau`
- Referenzbestand: `data/raw_data/Sportschau`
- Umfang des Cleaned-Bestands: 39 Spiele, 78 Halbzeitdateien und 32.668 Segmente
- Dateinamenschema: `[optionaler_numerischer_Präfix_]TEAM_TEAM_(first|second)_half.json`

Der Cleaned-Bestand dient als primäre Grundlage, weil Raw viel wiederholtes Boilerplate und mutmaßliche ASR-Fehler enthält. Cleaned reduziert dieses Rauschen, vereinfacht jedoch deutsche Sonderzeichen und enthält teilweise Spieler-Platzhalter. Raw bleibt daher unverändert als Referenz- und Sensitivitätsdatensatz erhalten.

## Loader verwenden

```python
from src.load_data import load_data

dataframe, issues = load_data("data/cleaned_data/Sportschau")
```

Der Daten-DataFrame besitzt neun Spalten:

- `match_id`: Spielkennung aus den beiden Mannschaftskürzeln
- `half`: Halbzeit (`1` oder `2`)
- `file`: Name der Quelldatei
- `segment_id`: ursprünglicher nullbasierter Index im jeweiligen JSON-Array
- `start`: unveränderter Startzeitwert des Segments
- `end`: unveränderter Endzeitwert des Segments
- `time_mid`: Mittelpunkt eines gültigen Zeitintervalls
- `time_continuous`: kontinuierliche Transkriptzeit über beide Halbzeiten
- `text`: unveränderter Segmenttext

Eine CSV wird nur erzeugt, wenn `output_csv` ausdrücklich angegeben wird:

```python
dataframe, issues = load_data(
    "data/cleaned_data/Sportschau",
    output_csv="outputs/processed/sportschau_segments.csv",
)
```

## Zeitlogik

`start`, `end` und `time_mid` bleiben halbzeitrelative Sekunden. Für ein gültiges Intervall gilt:

```text
time_mid = (start + end) / 2
```

In Halbzeit 1 entspricht `time_continuous` dem Wert von `time_mid`. Für Halbzeit 2 wird folgende Berechnung verwendet:

```text
offset = max(2700, größtes gültiges end der ersten Halbzeit)
time_continuous = time_mid + offset
```

Liegt keine gültige erste Halbzeit vor, wird reproduzierbar `2700` als Offset verwendet. `time_continuous` ist eine reproduzierbare kontinuierliche Transkript-Zeitachse und keine exakte offizielle Spieluhr.

## Validierung

Ungültige Segmente bleiben im Daten-DataFrame erhalten. Erkannte Probleme werden zusätzlich im Issues-DataFrame mit Datei, `segment_id` und Problembeschreibung ausgegeben.

Im aktuellen Cleaned-Gesamtlauf wurden 32.668 Segmente geladen. Dabei wurde genau ein leerer Text gemeldet: `07_POL_NED_first_half.json`, `segment_id` 29. Fehlende Werte in `time_mid` oder `time_continuous` traten im aktuellen Korpuslauf nicht auf.

## Tests

```powershell
python -m pytest -v
```

Aktueller Stand: 10 Tests bestanden. Geprüft werden Dateinamen, Mittelpunktberechnung, Validierungsprobleme, Sortierung, Reproduzierbarkeit sowie Offset- und Fallback-Logik.

## Transparenz zum KI-Einsatz

- ChatGPT unterstützte Planung, methodische Entscheidungen und Code-Review.
- Codex führte angeleitete Datenprüfungen durch und erzeugte den Loader sowie die zugehörigen Tests.
- Ergebnisse und Diffs wurden vom Bearbeiter kontrolliert.
- Rohdaten wurden nicht verändert.
- Es erfolgten keine automatischen Commits oder Pushes.
