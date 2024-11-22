import pandas as pd
import os
from glob import glob
from collections import Counter

# Ordnerpfad mit den CSV-Dateien
ordner_pfad = "dev_datasets"

# Liste aller CSV-Dateien im Ordner
csv_dateien = glob(os.path.join(ordner_pfad, "*.csv"))

# Zähler initialisieren
dateien_mit_placeholder_anzahl = 0
gesamt_placeholder = 0
gesamt_zeilen = 0
main_category_counter = Counter()

# Ergebnisse speichern
ergebnisse = []

# Über jede Datei iterieren
for datei in csv_dateien:
    try:
        # CSV-Datei laden
        df = pd.read_csv(datei)
        
        # Prüfen, ob die Spalte `log_line` existiert
        if 'log_line' in df.columns:
            # Identifizieren von Placeholder-Werten
            placeholder_rows = df['log_line'] == "no logging available"
            placeholder_anzahl = placeholder_rows.sum()
            
            # Statistik sammeln
            gesamt_placeholder += placeholder_anzahl
            gesamt_zeilen += len(df)
            
            # Werte in `main_category` sammeln, wenn `log_line` Placeholder ist
            if 'main_category' in df.columns:
                main_category_placeholder_values = df.loc[placeholder_rows, 'main_category']
                main_category_counter.update(main_category_placeholder_values.dropna())
            
            # Nur Dateien mit Placeholder-Werten hinzufügen
            if placeholder_anzahl > 0:
                dateien_mit_placeholder_anzahl += 1
                ergebnisse.append({
                    'Datei': os.path.basename(datei),
                    'Placeholder-Werte': placeholder_anzahl,
                    'Gesamt-Reihen': len(df)
                })
    except Exception as e:
        # Fehler beim Lesen/Schreiben der Datei ignorieren (kann optional geloggt werden)
        print(f"Fehler bei der Verarbeitung der Datei {os.path.basename(datei)}: {e}")

# Ergebnisse printen
print("Ergebnisse pro Datei:")
for eintrag in ergebnisse:
    print(f"- {eintrag['Datei']}: {eintrag['Placeholder-Werte']} Placeholder-Werte, {eintrag['Gesamt-Reihen']} Gesamt-Reihen")

# Gesamtstatistik printen
if gesamt_zeilen > 0:
    print(f"\nGesamtanzahl der Placeholder-Werte in der Spalte 'log_line': {gesamt_placeholder} ({(gesamt_placeholder / gesamt_zeilen) * 100:.2f}%)")
    print(f"Gesamtanzahl der geprüften Reihen: {gesamt_zeilen}")
else:
    print("\nKeine Reihen vorhanden.")

print(f"Dateien mit Placeholder-Werten: {dateien_mit_placeholder_anzahl}")

# Werte in der Spalte `main_category` für Placeholder anzeigen
print("\nHäufigkeiten der Werte in der Spalte 'main_category' für Placeholder in 'log_line':")
for category, count in main_category_counter.items():
    print(f"- {category}: {count} Mal")
