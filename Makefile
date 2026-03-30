# Makefile for Markdown to PDF Conversion
# ==========================================
# Ein Makefile ist ein Automatisierungstool, das wiederholte Terminal-Befehle vereinfacht.
# Statt lange Shell-Befehle zu tippen, schreibst du einfach 'make befehl' und Makefile erledigt den Rest.

RECURSIVE_SCRIPT := make.py
OPENER ?= xdg-open

# Finde alle .md-Dateien im aktuellen Verzeichnis (nicht in Unterordnern)
MD_FILES := $(wildcard *.md)
PDF_TARGETS := $(patsubst %.md,pdf/%.pdf,$(MD_FILES))

# Finde alle .md-Dateien rekursiv (auch in Unterordnern, aber nicht in pdf/)
MD_FILES_RECURSIVE := $(shell find . -name "*.md" -type f -not -path "./pdf/*" 2>/dev/null | sort)
PDF_TARGETS_RECURSIVE := $(patsubst %.md,pdf/%.pdf,$(MD_FILES_RECURSIVE))

# DEFAULT TARGET: Baue README.md → PDF
.PHONY: all all-recursive
all: readme

# RECURSIVE TARGET: Baue alle .md-Dateien zu PDFs (inkl. Unterordner)
all-recursive: $(PDF_TARGETS_RECURSIVE)
	@echo "✅ Alle PDFs (rekursiv) erstellt:"
	@ls -lh pdf/**/*.pdf pdf/*.pdf 2>/dev/null | awk '{print "  - " $$NF}'

# Pattern Rule: Baue PDF aus .md-Datei
pdf/%.pdf: %.md
	@mkdir -p $(dir $@)
	python3 $(RECURSIVE_SCRIPT) $<
	@echo "✅ $@ erstellt"

# README TARGET: Findet README.md (case-insensitive) und baut PDF
README_FILE := $(shell ls -1 *.md 2>/dev/null | grep -i "^readme\.md$$")
readme:
	@if [ -z "$(README_FILE)" ]; then echo "❌ Keine README.md gefunden"; exit 1; fi
	$(MAKE) pdf/$(README_FILE:.md=.pdf)

# PHONY TARGETS
.PHONY: all all-recursive clean list recurse help readme

# RECURSE TARGET: Zeige welche Dateien das Skript findet
recurse:
	@echo "🔍 Scanning for linked files in README.md..."
	@python3 $(RECURSIVE_SCRIPT)

# LIST TARGET: Zeige alle .md-Dateien
list:
	@echo "📄 Markdown-Dateien (aktuelles Verzeichnis):"
	@ls -1 *.md 2>/dev/null | sed 's/^/  - /' || echo "   (keine .md-Dateien gefunden)"
	@echo ""
	@echo "📄 Markdown-Dateien (rekursiv, ohne pdf/):"
	@find . -name "*.md" -type f -not -path "./pdf/*" 2>/dev/null | sort | sed 's/^/  - /' || echo "   (keine .md-Dateien gefunden)"

# CLEAN TARGET: Aufräumen — lösche alle generierten PDFs
clean:
	rm -rf pdf
	@echo "🗑️  Bereinigt: pdf/"

# INSTALL TARGET: Prüfe und installiere alle Abhängigkeiten
install:
	@echo "🔍 Checking dependencies..."
	@MISSING=""; \
	command -v pandoc >/dev/null 2>&1 && echo "  [OK] pandoc" || { echo "  [MISSING] pandoc"; MISSING="$$MISSING pandoc"; }; \
	command -v python3 >/dev/null 2>&1 && echo "  [OK] python3" || { echo "  [MISSING] python3"; MISSING="$$MISSING python3"; }; \
	command -v xelatex >/dev/null 2>&1 && echo "  [OK] xelatex" || { echo "  [MISSING] xelatex (texlive)"; MISSING="$$MISSING texlive-latex-base texlive-fonts-recommended texlive-latex-recommended texlive-xetex texlive-lang-german"; }; \
	command -v rsvg-convert >/dev/null 2>&1 && echo "  [OK] rsvg-convert" || { echo "  [MISSING] rsvg-convert (für SVG in PDFs)"; MISSING="$$MISSING librsvg2-bin"; }; \
	echo ""; \
	if [ -n "$$MISSING" ]; then \
		echo "📦 Installiere:$$MISSING"; \
		echo ""; \
		sudo apt install -y $$MISSING; \
		echo ""; \
		echo "✅ Installation abgeschlossen."; \
	else \
		echo "✅ Alle Abhängigkeiten sind installiert."; \
	fi

# HELP TARGET: Zeige Hilfe
help:
	@echo "📚 Markdown to PDF Converter"
	@echo ""
	@echo "Verwendung:"
	@echo "  make            - Baue README.md → pdf/"
	@echo "  make readme     - Baue README.md → pdf/"
	@echo "  make all-recursive - Baue alle .md-Dateien (inkl. Unterordner)"
	@echo "  make recurse    - Zeige gefundene Dateien (README.md)"
	@echo "  make list       - Zeige alle .md-Dateien"
	@echo "  make clean      - Lösche pdf/"
	@echo "  make install    - Installiere alle Abhängigkeiten"
	@echo "  make help       - Zeige diese Hilfe"
	@echo ""
