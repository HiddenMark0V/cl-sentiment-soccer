"""Sportschau-Rohdaten inventarisieren, ohne sie zu verändern.

Aufruf im Projektordner (Python >= 3.9, keine Zusatzpakete):
    python src/data_inventory.py
Andere Ordner: --raw-dir PFAD --output docs/data_inventory.csv

Alle Zeiten bleiben Sekunden. 'vollständig' ist eine technische Heuristik,
kein Nachweis einer lückenlosen Aufnahme. 'geprüft' bleibt immer 'nein'.
"""

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["match_id", "half", "file", "segments", "start_min", "end_max",
          "vollständig", "geprüft"]
NAME = re.compile(r"(?:\d+_)?([A-Z]{3}_[A-Z]{3})_(first|second)_half\.json", re.I)
# Transparente Prüfschwellen, keine gesicherten Grenzen der Aufnahmedauer.
MAX_START = 60
MIN_SPAN = 45 * 60
MAX_SPAN = 70 * 60
MAX_GAP = 60


def is_number(value):
    """Boolesche Werte, NaN und Unendlich sind keine gültigen Zeitangaben."""
    return type(value) in (int, float) and math.isfinite(value)


def reject_constant(value):
    """Python akzeptiert sonst NaN/Infinity, obwohl sie kein gültiges JSON sind."""
    raise ValueError(f"Ungültige JSON-Konstante: {value}")


def inspect_file(path):
    """Eine Zeile sowie gezählte Fehler und Hinweise für eine Datei erzeugen."""
    row = dict.fromkeys(FIELDS, "")
    row.update(file=path.name, vollständig="nein", geprüft="nein")
    errors, notes = Counter(), Counter()
    match = NAME.fullmatch(path.name)
    if match:
        row["match_id"] = match[1].upper()
        row["half"] = 1 if match[2].lower() == "first" else 2
    else:
        notes["Dateiname nicht zuordenbar"] += 1

    try:
        # Ausschließlich lesender Zugriff; utf-8-sig toleriert einen UTF-8-BOM.
        content = path.read_text(encoding="utf-8-sig")
        if not content.strip():
            row["segments"] = 0
            errors["Leere Datei"] += 1
            return row, errors, notes
        data = json.loads(content, parse_constant=reject_constant)
    except (OSError, UnicodeError, ValueError) as exc:
        errors[f"Nicht lesbar / ungültiges JSON: {exc}"] += 1
        return row, errors, notes
    if not isinstance(data, list):
        errors["Oberste JSON-Ebene ist keine Liste"] += 1
        return row, errors, notes

    # Auch fehlerhafte oder leere Listeneinträge zählen als Segmente.
    row["segments"] = len(data)
    if not data:
        errors["Leere Segmentliste"] += 1
        return row, errors, notes

    starts, ends, intervals = [], [], []
    previous_start = None
    has_text = False
    for segment in data:
        if not isinstance(segment, dict):
            errors["Segment ist kein Objekt"] += 1
            continue
        for key in ("start", "end", "text"):
            if key not in segment:
                errors[f"Pflichtfeld fehlt: {key}"] += 1
        start, end = segment.get("start"), segment.get("end")
        for key, value, values in (("start", start, starts), ("end", end, ends)):
            if is_number(value):
                values.append(value)
                if value < 0:
                    errors[f"Negativer {key}-Wert"] += 1
            elif key in segment:
                errors[f"Ungültiger {key}-Wert"] += 1
        if "text" in segment:
            if not isinstance(segment["text"], str):
                errors["text ist keine Zeichenkette"] += 1
            elif not segment["text"].strip():
                notes["Leerer Text"] += 1
            else:
                has_text = True
        if is_number(start):
            if previous_start is not None and start < previous_start:
                notes["Rücksprung der Startzeit in Dateireihenfolge"] += 1
            previous_start = start
        if is_number(start) and is_number(end):
            if end < start:
                errors["end liegt vor start"] += 1
            elif end == start:
                notes["Segmentdauer null"] += 1
            elif start >= 0:
                intervals.append((start, end))

    row["start_min"] = min(starts) if starts else ""
    row["end_max"] = max(ends) if ends else ""
    if not has_text:
        errors["Kein nichtleerer Text vorhanden"] += 1
    if errors:
        return row, errors, notes

    uncertain = match is None
    span = row["end_max"] - row["start_min"]
    if row["start_min"] > MAX_START:
        notes["Später Beginn: mehr als 60 s"] += 1
        uncertain = True
    if span < MIN_SPAN:
        notes["Kurze Zeitspanne: weniger als 2700 s"] += 1
        uncertain = True
    if span > MAX_SPAN:
        notes["Lange Zeitspanne: mehr als 4200 s; Zusatzphasen möglich"] += 1
        uncertain = True
    # Nur die Hilfsliste sortieren. Überlappungen sind kein Beweis für Datenverlust.
    covered_until = None
    for start, end in sorted(intervals):
        if covered_until is not None and start - covered_until > MAX_GAP:
            notes["Zeitlücke zwischen Segmenten über 60 s"] += 1
            uncertain = True
        covered_until = max(covered_until or 0, end)
    row["vollständig"] = "unklar" if uncertain else "ja"
    return row, errors, notes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path,
                        default=ROOT / "SocCor/Textdata/raw_data/Games/Sportschau")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/data_inventory.csv")
    args = parser.parse_args()
    if not args.raw_dir.is_dir():
        parser.error(f"Rohdatenordner fehlt: {args.raw_dir}")
    files = sorted(p for p in args.raw_dir.rglob("*")
                   if p.is_file() and p.suffix.lower() == ".json")
    if not files:
        parser.error("Keine JSON-Dateien gefunden; keine Ausgabe geschrieben.")
    output = args.output.resolve()
    report = output.with_name(output.stem + "_notes.md")
    if any(p.is_relative_to(args.raw_dir.resolve()) for p in (output, report)):
        parser.error("Ausgabedateien dürfen nicht im Rohdatenordner liegen.")

    rows, details = [], []
    for path in files:
        row, errors, notes = inspect_file(path)
        rows.append(row)
        detail = "; ".join(f"{key}: {count}" for key, count in (errors + notes).items())
        details.append(f"- `{path.relative_to(args.raw_dir)}`: {detail or 'Keine Auffälligkeiten.'}")

    pairs = Counter((row["match_id"], row["half"]) for row in rows)
    for match_id, half in sorted(pairs, key=str):
        if match_id and half:
            if pairs[(match_id, half)] > 1:
                details.append(f"- Mehrfach vorhanden: {match_id}, Halbzeit {half}.")
            if (match_id, 3 - half) not in pairs:
                details.append(f"- Fehlende Partnerdatei: {match_id}, Halbzeit {3 - half}.")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = Counter(row["vollständig"] for row in rows)
    report.write_text(
        "# Dateninventar: Prüfprotokoll\n\n"
        f"Quelle: `{args.raw_dir.resolve()}`\n\n"
        f"Dateien: {len(rows)}; Segmente: {sum(r['segments'] or 0 for r in rows)}. "
        f"Status: {dict(summary)}.\n\n"
        "## Wiederholen\n\n"
        "Python >= 3.9; ausschließlich Standardbibliothek. Im Projektordner: "
        "`python src/data_inventory.py`. Andere Pfade mit `--raw-dir PFAD` und "
        "`--output docs/data_inventory.csv` angeben. Vorhandene Ausgaben werden ersetzt. "
        "Alle JSON-Dateien im angegebenen Rohdatenordner werden rekursiv eingelesen.\n\n"
        "## Kriterien\n\n"
        "- Zeitwerte bleiben Sekunden; start_min bedeutet Minimum, nicht Minuten.\n"
        "- segments zählt sämtliche Listeneinträge, auch leere Texte. Unbekannte "
        "Werte bleiben in der CSV leer; eine leere Datei/Liste erhält segments=0.\n"
        "- nein: leer, nicht lesbar, ungültiges JSON, falsche Struktur, fehlende "
        "Pflichtfelder, falsche Datentypen, ungültige/negative Zeiten, end < start "
        "oder überhaupt kein nichtleerer Text.\n"
        "- unklar: sonst technisch lesbar, aber Dateiname nicht zuordenbar, Beginn "
        "> 60 s, Zeitspanne < 2700 s oder > 4200 s, oder Segmentlücke > 60 s. "
        "Zusatzphasen und Sprechpausen sind mögliche Ursachen, keine bestätigten Fehler.\n"
        "- ja: keine der obigen Bedingungen. Nur vorläufige technische Plausibilität; "
        "keine Garantie einer vollständigen Halbzeit oder korrekter Transkription.\n"
        "- Einzelne leere Texte, Nulldauern und Rücksprünge werden gezählt, ohne "
        "allein daraus fehlende Aufnahmeabschnitte abzuleiten.\n"
        "- geprüft bleibt nein: keine vollständige manuelle Prüfung gegen Audio. "
        "Ein erneuter Lauf übernimmt keine früheren manuellen CSV-Einträge.\n"
        "- Fehlende Partnerdateien und doppelte match_id/half-Kombinationen werden "
        "separat gemeldet; sie verändern nicht den Status der einzelnen Datei.\n"
        "- Die Inventur bezieht sich nur auf vorhandene Dateien, nicht auf einen "
        "externen Soll-Spielplan. Rohdaten werden ausschließlich gelesen.\n\n"
        "## Auffälligkeiten je Datei\n\n" + "\n".join(details) + "\n",
        encoding="utf-8")
    print(f"{len(rows)} Dateien inventarisiert: {output}")
    print(f"Status: {dict(summary)}; Prüfprotokoll: {report}")


if __name__ == "__main__":
    main()
