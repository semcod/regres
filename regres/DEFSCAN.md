# defscan.py — skaner duplikatów definicji

**Kluczowa zasada:** wyciąga **pełne ciało** każdej definicji (klasa / metoda / funkcja / interface / enum / type / struct / trait) i porównuje **implementacje**, nie tylko nazwy. Dzięki temu wykrywa zarówno klasyczne duplikaty po nazwie, jak i ukryte kopie pod różnymi nazwami.

## Tryby pracy

Skrypt obsługuje **trzy tryby** — wybierane przez flagi CLI:

| Tryb | Flagi | Co robi |
|------|-------|---------|
| **DUPLIKATY** (domyślny) | brak | Grupuje wszystkie definicje po nazwie i pokazuje grupy z `>= --min-count` wystąpieniami w całym `--path`. |
| **FOCUS** | `--focus <folder>` (+ opcjonalnie `--scope`) | Zbiera definicje **tylko z `--focus`** i porównuje je z resztą `--scope`. Pokazuje grupy tylko gdy istnieje co najmniej jedna definicja **poza** focusem. Idealne do pytania *„czy `./backend` duplikuje coś z reszty projektu?”*. |
| **SEED similarity globalna** | `--seed <folder>` | Bierze każdą definicję z `--seed` i porównuje **ciało** z **każdą** definicją w projekcie, niezależnie od nazwy. Wykrywa **ukryte duplikaty pod innymi nazwami**. Domyślny próg: 60% (można nadpisać `--min-sim`). |

## Szybkie przykłady

```bash
# Tryb DUPLIKATY — wszystkie klasy zduplikowane ≥2 razy, pary podobne ≥50%
python defscan.py --kind class --min-count 2 --min-sim 50

# Konkretny symbol z pełnym podglądem ciała
python defscan.py --name ProtocolStatus --min-sim 0

# Tryb FOCUS — czy ./backend duplikuje coś z reszty projektu?
python defscan.py --focus ./backend --min-sim 50

# FOCUS w węższym zakresie (np. tylko backend vs reszta backendu)
python defscan.py --focus ./backend/api --scope ./backend --kind class

# Tryb SEED — ukryte duplikaty modeli (różne nazwy, podobny kod)
python defscan.py --seed ./backend --kind class --min-sim 70

# SEED ignorujący te same nazwy (zostawia tylko ukryte kopie)
python defscan.py --seed ./backend --kind class --min-sim 70 --seed-skip-same-name

# Filtrowanie po rozszerzeniu — tylko klasy Pythona zduplikowane ≥2 razy, 95% podobne
python defscan.py --ext .py --kind class --min-count 2 --min-sim 95 --md > defscan-classes-py.md

# Filtrowanie po rozszerzeniu — tylko klasy TypeScript zduplikowane ≥2 razy, 95% podobne
python defscan.py --ext .ts --kind class --min-count 2 --min-sim 95 --md > defscan-classes-ts.md

# Eksport raportu dla LLM / PR review
python defscan.py --min-count 2 --top 20 --json > dup-report.json
python defscan.py --min-count 2 --md  > dup-report.md
```

## Wszystkie flagi

### Wspólne

| Flaga | Domyślnie | Opis |
|-------|-----------|------|
| `--path`, `-p` | `.` | Katalog główny projektu. |
| `--name`, `-n` | `—` | Filtruj po nazwie symbolu (case-insensitive, dokładne dopasowanie). |
| `--kind`, `-k` | `—` | `class \| function \| method \| interface \| enum \| type \| struct \| trait`. |
| `--ext`, `-e` | `—` | Filtruj po rozszerzeniu pliku (można podać wiele: `--ext .py --ext .ts`). Bez tej flagi skanowane są wszystkie obsługiwane języki. |
| `--min-sim`, `-s` | `0` (seed: `60`) | Minimalny próg podobieństwa par (%). |
| `--preview` | `6` | Ile linii ciała pokazywać w podglądzie (`0` = wyłącz). |
| `--top` | `0` | Tylko TOP N grup / seedów (`0` = wszystkie). |
| `--json` / `--md` | `—` | Eksport do JSON / Markdown na stdout. |
| `--no-color` | `—` | Wyłącz kolory ANSI (domyślnie wyłączane przy `--json/--md` lub redirekcie). |

### Tryb DUPLIKATY (domyślny)

| Flaga | Domyślnie | Opis |
|-------|-----------|------|
| `--min-count`, `-c` | `2` | Minimalna liczba definicji o tej samej nazwie. |

### Tryb FOCUS

| Flaga | Domyślnie | Opis |
|-------|-----------|------|
| `--focus` | `—` | Folder źródłowy (np. `./backend`). Włącza tryb. |
| `--scope` | wartość `--path` | Zakres porównania (musi obejmować `--focus`). |

### Tryb SEED similarity globalna

| Flaga | Domyślnie | Opis |
|-------|-----------|------|
| `--seed` | `—` | Folder z definicjami bazowymi. Włącza tryb. |
| `--similar-global` | flaga | Akceptowane dla zgodności CLI — tryb seed jest globalny domyślnie. |
| `--seed-top` | `10` | Liczba najlepszych dopasowań pokazywanych per seed. |
| `--seed-skip-same-name` | `false` | Pomijaj dopasowania o tej samej nazwie (zostają tylko ukryte duplikaty). |
| `--scope` | wartość `--path` | Zakres porównania zarówno dla seed jak i pełnego skanu. |

## Progi podobieństwa

| % | Etykieta | Co to znaczy |
|---|----------|--------------|
| ≥95% | **IDENTYCZNE** | Bezpieczne do usunięcia jednej kopii. |
| ≥75% | **PRAWIE KOPIE** | Ten sam model, drobne różnice (np. `DONE` vs `COMPLETED`). |
| ≥50% | **PODOBNE** | Ta sama logika, inne nazewnictwo / język. |
| ≥25% | **CZĘŚCIOWE** | Wspólna struktura, różna implementacja. |
| <25% | **RÓŻNE** | Najpewniej kolizja nazw, nie duplikat. |

## Języki i co wyciąga

- **Python** (`.py`) — przez `ast`: klasy, metody (`Class.method`), funkcje, klasy bazowe, dekoratory.
- **TypeScript / JavaScript** (`.ts .tsx .js .jsx`) — klasy, interfejsy, enumy, type aliases (object), funkcje deklarowane i strzałkowe.
- **Go** (`.go`) — `struct`, `interface`, funkcje z receiverem (`Receiver.Method`).
- **Rust** (`.rs`) — `struct`, `enum`, `trait`, `fn`.

Ignorowane katalogi: `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `target`, `out`, `__pycache__`, `_archive`, `.cache`, `.next`, `.nuxt`, `coverage`, `.pytest_cache`, `.mypy_cache` oraz wszystkie ukryte foldery (zaczynające się od `.`).

### Respektowanie `.gitignore`

Skrypt automatycznie czyta `.gitignore` z korzenia projektu (`--path`) i pomija pasujące pliki/katalogi we **wszystkich trybach** (DUPLIKATY, FOCUS, SEED). Obsługiwane są:

- wzorce zanchorowane (`/build/`, `/dist`),
- wzorce niezanchorowane dopasowywane do dowolnego komponentu ścieżki (`*.log`, `secret.env`),
- wzorce katalogowe zakończone `/` (np. `tmp/`),
- negacje `!pattern` przywracające wcześniej zignorowane ścieżki,
- glob-y w stylu `fnmatch` (`*`, `?`, `[abc]`).

Filtr działa **dodatkowo** do listy `IGNORED_DIRS` powyżej — `.gitignore` może tylko rozszerzać zbiór pomijanych ścieżek, nie zmniejsza go. Pliki spoza `--path` (np. gdy `--scope` wskazuje katalog nadrzędny) są filtrowane wzorcami z `--path/.gitignore`.

### Debugowanie pominiętych plików

Jeśli symbol nie pojawia się w wynikach, najpierw upewnij się, że nie jest on pomijany przez `.gitignore` lub twardą listę `IGNORED_DIRS`:

```bash
# 1. Sprawdź, czy symbol w ogóle jest w indeksie
python defscan.py --name DokladnaNazwaKlasy --min-sim 0

# 2. Jeśli brak wyniku — sprawdź, czy katalog nie jest w IGNORED_DIRS
#    lub nie zaczyna się od kropki (np. .idea/, .task/)
# 3. Jeśli nie — sprawdź .gitignore w korzeniu --path

# 4. Szybki test pojedynczego pliku względem .gitignore
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '.')
from defscan import load_gitignore, _path_ignored_by_gitignore
root = Path('.')
path = Path('backend/api/schemas/secret.py')
ignored = _path_ignored_by_gitignore(path, root, load_gitignore(root))
print('IGNORED' if ignored else 'NOT IGNORED')
"
```

## Wybrane scenariusze refaktoryzacyjne

```bash
# 1. Znajdź 100% identyczne klasy w monorepo (gotowe do scalenia)
python defscan.py --ext py --kind class --min-count 2 --min-sim 95 --md > defscan-classes-py.md
python defscan.py --ext ts --kind class --min-count 2 --min-sim 95 --md > defscan-classes-ts.md

# 2. Sprawdź, czy backend nie powiela schematów connect-* backendów
python defscan.py --focus ./backend --scope . --kind class --min-sim 50

# 3. Wykryj ukryte modele DTO/command pod różnymi nazwami
python defscan.py --seed ./backend/api/schemas --kind class \
    --seed-skip-same-name --min-sim 75 --md > hidden-dtos.md

# 4. Drift między Python a TypeScript dla konkretnego symbolu
python defscan.py --name ProtocolStatus --min-sim 0 --preview 20
```

## Wyjścia

- **Tekst** (domyślnie) — czytelny w terminalu, kolorowany wg progu podobieństwa.
- **JSON** (`--json`) — strukturalny dump (grupy/duplikaty albo seed→matches).
- **Markdown** (`--md`) — tabele + foldowane podglądy `<details>`, gotowe do PR review.