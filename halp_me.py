import pandas as pd
import os
from glob import glob
from collections import Counter

# Ordnerpfad mit den CSV-Dateien
ordner_pfad = "datasets"

# Liste aller CSV-Dateien im Ordner
csv_dateien = glob(os.path.join(ordner_pfad, "*.csv"))

# Zähler initialisieren
dateien_mit_nones_anzahl = 0
keine_none_gesamt = 0
gesamt_zeilen = 0
gesamt_nones = 0
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
            # Identifizieren von None-Werten
            none_rows = df['log_line'].isna()
            none_anzahl = none_rows.sum()
            
            # Regel: Modifizieren der Dateien
            all_none = none_rows.all()  # Alle Reihen in `log_line` sind NaN?
            if all_none:
                # Alle Reihen haben NaN: Placeholder in `log_line` setzen
                df['log_line'] = "no logging available"
            else:
                # Nur NaN-Reihen entfernen
                df = df[~none_rows]
            
            # Werte in `main_category` sammeln, wenn `log_line` None war
            if 'main_category' in df.columns:
                main_category_none_values = df.loc[none_rows, 'main_category']
                main_category_counter.update(main_category_none_values.dropna())
            
            # Nach der Überarbeitung: Statistik berechnen
            none_anzahl = df['log_line'].isna().sum()  # Sollte nun 0 sein
            not_none_anzahl = len(df)  # Alle übrig gebliebenen Reihen
            
            # Gesamtzähler aktualisieren
            gesamt_zeilen += len(df)
            keine_none_gesamt += not_none_anzahl
            
            # Nur Dateien mit ursprünglichen None-Werten hinzufügen
            if none_rows.any():
                dateien_mit_nones_anzahl += 1
                ergebnisse.append({
                    'Datei': os.path.basename(datei),
                    'None-Werte': none_rows.sum(),
                    'Keine-None-Werte': not_none_anzahl
                })
        
        # DataFrame zurück in die Datei speichern
        df.to_csv(datei, index=False)
    except Exception as e:
        # Fehler beim Lesen/Schreiben der Datei ignorieren (kann optional geloggt werden)
        print(f"Fehler bei der Verarbeitung der Datei {os.path.basename(datei)}: {e}")

# Ergebnisse printen
print("Ergebnisse pro Datei (nach Überarbeitung):")
for eintrag in ergebnisse:
    print(f"- {eintrag['Datei']}: {eintrag['None-Werte']} None Reihen, {eintrag['Keine-None-Werte']} Reihen mit val. Werten")

# Gesamtstatistik printen
print(f"\nGesamtanzahl der samples ohne None-Werte in der Spalte 'log_line' (nach Überarbeitung): {keine_none_gesamt}")
print(f"Gesamtanzahl der samples mit 'None' in 'log_line' (vor Überarbeitung): {gesamt_nones}")
print(f"Gesamtanzahl der geprüften samples: {gesamt_zeilen}")
print(f"Dateien mit None samples (jetzt mit 'No logging information available): {dateien_mit_nones_anzahl}")

# Check assigned label for None / No loggging info available
print("\nHäufigkeiten der Werte in der Spalte 'main_category' für ursprüngliche None-Werte in 'log_line':")
for category, count in main_category_counter.items():
    print(f"- {category}: {count} Mal")

print("done")
