# Markdown to PDF Converter

Dieses Verzeichnis enthält Markdown-Dokumentationen und ein Makefile zur PDF-Konvertierung mit pandoc.

## Voraussetzungen

```bash
# Pandoc installieren
sudo apt install pandoc

# PDF-Engine installieren (eine der folgenden):
sudo apt install texlive-latex-base texlive-fonts-recommended texlive-latex-recommended texlive-xetex  # LaTeX/XeTeX (beste Qualität, Unicode)
# ODER
sudo apt install wkhtmltopdf   # Leichtgewichtig (~20MB)
# ODER
sudo apt install weasyprint    # Modernes CSS
```

Alternativ: `make install` führt eine interaktive Installation durch.

## Makefle verstehen

Ein **Makefile** ist ein Automatisierungstool für wiederholte Terminal-Befehle.
Statt lange Shell-Befehle zu tippen, schreibst du `make befehl` und das Makefile erledigt den Rest.

### Wie ein Makefile funktioniert:

1. **Variablen** — Einstellungen speichern (z.B. `PDF_DIR = pdf`)
2. **Targets (Ziele)** — was soll gebaut werden? (z.B. `pdf/home-assistant.pdf`)
3. **Dependencies (Abhängigkeiten)** — worauf basiert das Ziel? (z.B. die `.md`-Datei)
4. **Recipes (Rezepte)** — welche Befehle führen zum Ziel? (die eingerückten Zeilen)

### Was passiert beim `make` befehl:

```
make homeassistant-howto
  ↓
Makefile findet das Target "homeassistant-howto"
  ↓
Prüft: Existiert homeassistant-howto.md? → JA ✓
  ↓
Führt aus:
  1. Erstelle pdf/-Verzeichnis
  2. Kombiniere Markdown-Dateien (combine-markdown.py)
  3. Konvertiere zu PDF mit pandoc
  4. Öffne die PDF
```

### Pattern Rules (Muster-Ziele):

Die Regel `$(PDF_DIR)/%.pdf: %.md` sagt:
- Baue jede `.pdf`-Datei aus ihrer entsprechenden `.md`-Datei
- Das `%` ist ein Wildcard: homeassistant-howto, CLAUDE, etc.

### Platzhalter im Makefile:

| Platzhalter | Bedeutung |
|-------------|----------|
| `$<` | Erste Abhängigkeit (z.B. `homeassistant-howto.md`) |
| `$@` | Das Ziel (z.B. `pdf/homeassistant-howto.pdf`) |
| `$*` | Wildcard-Teil (z.B. `homeassistant-howto`) |
| `$(VAR)` | Wert einer Variable |

## Markdown Recursive: Das neue System

Das `make.py` Skript automatisiert die Dokumentation:

1. **Scanner**: Lädt eine Markdown-Datei (Standard: README.md)
2. **Link-Analyse**: Scannt nach allen `[text](file.md)` Links
3. **Rekursion**: Verfolgt Links auch in eingebundenen Dateien
4. **Deduplizierung**: Verhindert Duplikate und Endlosschleifen
5. **Inhaltsverzeichnis**: Generiert ein TOC mit funktionierenden PDF-Ankern
6. **PDF-Export**: Baut die PDF mit pandoc und öffnet sie

### Verwendung

#### Mit Make (einfach):
```bash
make              # Baue PDF aus README.md → pdf/README.pdf
make recurse      # Zeige gefundene Dateien (ohne PDF)
make list         # Zeige alle .md-Dateien
make clean        # Lösche PDFs
```

#### Direktes Skript (erweiterte Optionen):
```bash
# Standard: README.md suchen und PDF bauen → pdf/README.pdf
./make.py

# Spezifische Datei: homeassistant-howto.md → pdf/homeassistant-howto.pdf
./make.py homeassistant-howto.md

# Mit Sortierung
./make.py homeassistant-howto.md -s a-z

# Ohne Auto-Open
./make.py -n

# Benutzerdefinierte PDF-Ausgabe
./make.py README.md -o pdf/custom.pdf

# Alle Optionen
./make.py CLAUDE.md -s depth -o pdf/meine-pdf.pdf -n
```

### Sortierungsoptionen (-s)

| Option | Effekt |
|--------|--------|
| `depth` (default) | Tiefensuche (erste Datei, dann deren Links) |
| `first` | Reihenfolge des ersten Auftretens |
| `a-z` | Alphabetisch nach Dateinamen |

### Funktionsweise im Detail

```
START: make.py README.md
  ↓
1. Finde README.md (case-insensitive) → `pdf/README.pdf` wird Output
  ↓
2. Extrahiere alle [text](file.md) Links
  ↓
3. Für jede verlinkte Datei:
   - Prüfe Dateiexistenz
   - Checke auf Duplikate
   - Öffne Datei rekursiv (Schritt 2)
  ↓
4. Erstelle eindeutige PDF-Anker für jede Datei
  ↓
5. Generiere Inhaltsverzeichnis:
   # Inhaltsverzeichnis
   - [Deploy Anleitung](#sec-deploy-anleitung)
   - [FAQ](#sec-faq)
  ↓
6. Baue kombiniertes Markdown:
   - README.md (mit konvertierten Links)
   - [TOC mit Ankern]
   - deploy-anleitung.md mit Anker #sec-deploy-anleitung
   - faq.md mit Anker #sec-faq
  ↓
7. Konvertiere mit pandoc zu PDF
   pandoc combined.md -o pdf/README.pdf --pdf-engine=xelatex --toc
  ↓
8. Öffne PDF (xdg-open pdf/README.pdf)
END ✅
```

### Was sind PDF-Anker?

Ein Anker ist eine Sprungmarke in der PDF. Links funktionieren wie:
- **Vorher**: `[Deploy](deploy.md)` → Funktioniert nur in Markdown
- **Nachher**: `[Deploy](#sec-deploy-anleitung)` → Funktioniert im PDF klikbar!

Das Inhaltsverzeichnis (TOC) ist somit **vollständig interaktiv** in der fertiggestellten PDF.

## Enthaltene Dokumente

| Datei | Beschreibung |
|-------|--------------|
| `README.md` | Hauptdokumentation (Einstieg) |
| `CLAUDE.md` | Richtlinien für Claude (diese IDE) |
| `homeassistant-howto.md` | Anleitung zur Ersteinrichtung von Home Assistant auf Raspberry Pi 4 |
| `Bildschirme-Erweiterun-Spiegeln.md` | Display/Monitor Erweiterung und Spiegeln |
