# REGRES: wsparcie LLM dla refaktoryzacji i regresji

`regres.py` to bezpieczny analizator pojedynczego pliku. Nie wykonuje `checkout` ani mutacji repozytorium. Generuje raport, który możesz od razu podać do LLM.

## Co dostajesz w raporcie

- metryki treści pliku (`lines`, `imports`, `exports`, `class_count`, `sha256`)
- drzewo zależności lokalnych (`dependency_tree`)
- drzewo referencji zwrotnych (`reverse_imports`)
- historię pliku z `git log --follow` (autor, data, status zmian, insertions/deletions)
- **ewolucję pliku** w kolejnych commitach — liczba linii, similarity do aktualnej wersji, zmiany w drzewie importów
- **ostatnie wersje spełniające kryteria** — np. kiedy ostatnio plik był bardziej rozbudowany
- referencje historyczne: jakie pliki współzmieniały się z targetem w ostatnich commitach
- duplikaty treści:
  - dokładne (`exact_duplicates`, ten sam hash)
  - podobne (`near_duplicates`, similarity ważona stosunkiem linii)
- kandydatów po **tej samej nazwie pliku + hash/similarity** (`name_hash_candidates`) z ostatnim commitem dla każdej ścieżki
- gotowy pakiet `llm_context` do promptowania modeli

## Szybkie użycie

```bash
python3 regres.py \
  --file frontend/src/pages/connect-test-reports.page.ts \
  --scan-root frontend/src \
  --max-commits 120 \
  --tree-depth 4 \
  --near-threshold 0.90 \
  --out-json .regres/connect-test-reports.json \
  --out-md .regres/connect-test-reports.md
```
```bash
python3 regres.py \
  --file connect-test-reports.page.ts \
  --scan-root frontend/src \
  --max-commits 120 \
  --tree-depth 4 \
  --near-threshold 0.90 \
  --out-json .regres/connect-test-reports.json \
  --out-md .regres/connect-test-reports.md
```
## Interpretacja wyników

### 1) Metryki
- duży spadek `exports_count` / `function_like_count` po refaktorze często oznacza „zbyt cienki wrapper”
- zmiana `sha256` bez zmian w testach może być tylko kosmetyczna

### 2) Drzewa
- `dependency_tree` pokazuje, gdzie logika faktycznie „uciekła” po przeniesieniach
- `reverse_imports` pokazuje, co popsuje się, jeśli przywrócisz plik 1:1 z historii

### 3) Ewolucja pliku

Dla każdego commita z historii `git log --follow` (do `--max-commits` wstecz):

| Pole | Opis |
|---|---|
| `lines` | Liczba linii pliku w danym commicie |
| `line_delta` | Różnica vs aktualna wersja (`hist - current`) |
| `similarity_to_current` | `SequenceMatcher.ratio()` między treścią w commicie a aktualną |
| `tree_imports_count` | Ile lokalnych importów w drzewie zależności (poziom 1) |
| `tree_changed` | Czy struktura importów zmieniła się vs poprzedni commit |
| `tree_added` / `tree_removed` | Które ścieżki pojawiły się / zniknęły w drzewie |

**Kluczowe wnioski z ewolucji:**
- Wysoka `similarity` + duża `line_delta` = prawdopodobny rename lub kopiowanie z małymi zmianami
- Niska `similarity` + duża `line_delta` = totalna przepisanie / wymiana contentu
- `tree_changed = true` = migracja logiki między plikami (refaktoring)

### 4) Ostatnie wersje spełniające kryteria

Domyślnie znajdywana jest ostatnia wersja z **większą lub równą liczbą linii** niż obecna. Dla plików typu „2-liniowy wrapper" znajdzie wersję historyczną, gdzie była więcej logiki.

Przykład:
```
Ostatnie wersje spełniające kryteria (>= aktualnych linii)
- `92efe1d9` 2026-04-27 — 9 linii (delta +7), similarity=0.0417, 'refactoring'
```
To oznacza: w commicie `92efe1d9` plik miał 9 linii (7 więcej niż obecnie), ale similarity do aktualnej wersji to tylko 4% — czyli content został praktycznie całkowicie wymieniony.

### 5) Historia i referencje
- `lineage` + `recent_commit_related_files` daje kontekst: które pliki migrowały razem
- to jest kluczowe przy duplikatach i rename’ach

### 6) Duplikaty
- `exact_duplicates`: kandydaci do de-duplikacji / pozostawienia jednego źródła prawdy
- `near_duplicates`: similarity ważona stosunkiem linii — `similarity = raw_similarity * (min_lines / max_lines)`. Dzięki temu 2-liniowy wrapper vs 100-liniowy plik nie dostaje fałszywego wysokiego podobieństwa.

## Prompt dla LLM (gotowiec)

Wklej do modelu `llm_context` z JSON i użyj promptu:

```text
Przeanalizuj llm_context dla pliku target.
1. Wskaż najbardziej prawdopodobne źródło regresji.
2. Sprawdź sekcję evolution — czy plik stracił linie, czy drzewo importów się zmieniło?
3. Jeśli last_good_version pokazuje starszą wersję z więcej linii, sprawdź czy to kandydat na przywrócenie.
4. Wskaż, który duplikat (exact/near) jest najlepszym kandydatem na source of truth.
5. Zaproponuj minimalny patch (bez zmian niezwiązanych z problemem).
6. Wypisz ryzyka i testy do uruchomienia po zmianie.
```

## Algorytm Regression Detective (nowy)

Cel: dla pliku z błędem (np. `Failed to resolve import`) znaleźć ostatnią wersję, w której plik miał kompletne, działające drzewo zależności, i wygenerować rekomendację naprawy.

### Krok po kroku (deterministycznie: od najnowszych do najstarszych)

**0. Ustal realny plik wejściowy (`--file`)**
- Jeśli podano ścieżkę absolutną i plik istnieje → użyj jej.
- Jeśli podano ścieżkę względną → sprawdź kolejno: `cwd`, `repo_root`, `scan_root`.
- Jeśli dalej brak pliku, potraktuj wartość jako nazwę/sufiks i przeszukaj repo (`rglob`) — preferuj trafienia pod `scan_root`.
- Gdy kandydatów jest wiele, pokaż listę możliwych ścieżek zamiast kończyć analizę „ślepo”.

**1. Wyciągnij lokalne importy z aktualnej wersji pliku**
- Parsuj wszystkie `import ... from '...'` oraz `export * from '...'`
- Filtrowanie: tylko ścieżki zaczynające się od `./` lub `../`

**2. Ustal oś czasu zmian pliku (`git log --follow`)**
- Zbuduj listę commitów max `N` elementów.
- Kolejność iteracji zawsze: `HEAD -> starsze` (najnowszy do najstarszego).

**3. Dla każdego commita z historii (`HEAD -> starsze`)**
- Odczytaj zawartość pliku: `git show <sha>:<rel_path>`
- Jeśli plik nie istnieje w commicie → pomiń
- Wyciągnij importy z historycznej wersji
- Dla każdego importu: sprawdź czy importowany plik istnieje w tym commicie (`git show <sha>:<resolved_path>`)
- Zapisz: które importy są OK, które BROKEN

**4. Znajdź ostatni działający commit**
- Idąc od `HEAD` wstecz, wybierz pierwszy commit, gdzie **wszystkie** lokalne importy są rozwiązywalne
- Zapisz: `last_working_commit_sha`, `last_working_import_count`, `last_working_lines`

**5. Znajdź pierwszy popsuty commit**
- To commit bezpośrednio nowszy niż `last_working` (jeśli istnieje)
- Zapisz co zniknęło: lista `missing_imports`

**6. Poszukaj zagubionych plików w historii git**
- Dla każdego `missing_import`: `git log --all --full-history -- "<path_glob>"`
- Sprawdź czy plik istnieje pod inną nazwą lub w innym miejscu w repo
- Sprawdź czy plik został przeniesiony (rename w git)

**7. Wygeneruj rekomendację naprawy**
- Jeśli plik zaginiony istnieje pod nową ścieżką → rekomendacja: `sed -i 's|old/import/path|new/import/path|g'`
- Jeśli plik zaginiony nie istnieje wcale → rekomendacja: sprawdź `last_good_version` czy logika była tam wbudowana
- Jeśli import jest martwy i nieużywany → rekomendacja: usuń import
- Jeśli plik był w innym module → rekomendacja: dostosuj ścieżkę relatywną

**8. Śledzenie po nazwie i hashach (`name_hash_candidates`)**
- Dla bazowej nazwy pliku (np. `full-test.page.ts`) wyszukaj wszystkie ścieżki o tej samej nazwie w `scan_root` i repo.
- Porównaj `sha256` i similarity (ważone długością) względem targetu.
- Dla każdej ścieżki zapisz ostatni commit (`git log -n 1 -- <path>`).
- To pozwala znaleźć „ten sam plik pod inną ścieżką” po refaktorze, nawet gdy importy się zmieniły.

### Przykład użycia

Błąd Vite:
```
Failed to resolve import "../../../config/api.config"
from ".../device-testing.page.ts"
```

Uruchom REGRES:
```bash
python3 regres.py \
  --file connect-test-device/frontend/src/modules/connect-test-device/pages/device-testing.page.ts \
  --scan-root frontend/src \
  --max-commits 60 \
  --tree-depth 3 \
  --out-md .regres/device-testing-regression.md
```

W raporcie pojawi się nowa sekcja:
```markdown
## Regression Detective

### Aktualnie popsute importy (3)
- `../../../config/api.config` → NIE ISTNIEJE w obecnej wersji
- `../../connect-test/cqrs/singleton` → ISTNIEJE
- `../../connect-test/models/test-config` → ISTNIEJE

### Ostatni działający commit
- `77959ed6` 2026-04-26 — 450 linii, 8 importów OK

### Co zniknęło między `77959ed6` a HEAD
- `config/api.config.ts` — usunięty w commicie `92efe1d9`
- Znaleziono w historii: `frontend/src/config/api.config.ts` (istniał do 2026-04-27)

### Rekomendacja naprawy
1. Plik `config/api.config.ts` został usunięty w refactoringu.
2. Symbol `MAX_PAGE_SIZE` był tam zdefiniowany.
3. Opcje:
   a) Przywróć `frontend/src/config/api.config.ts` z commita `77959ed6`
   b) Zastąp import inline: `const MAX_PAGE_SIZE = 100;`
   c) Sprawdź czy `MAX_PAGE_SIZE` jest gdzie indziej w repo
```

## Zalecany workflow

1. Uruchom `regres.py` dla pliku z błędem.
2. Przekaż `llm_context` do LLM — zwróć uwagę na `evolution_summary` i `last_good_version`.
3. Jeśli `last_good_version` wskazuje starszą wersję z więcej logiki, porównaj ją z aktualną (np. `git show <sha>:path`).
4. Zastosuj minimalny patch.
5. Uruchom testy lokalne (np. TestQL dry-run).
6. Powtórz dla kolejnych plików z listy `recent_commit_related_files`.

## DEFSCAN / REFACTOR — czy warto integrować?

Tak, ale jako **opcjonalny etap po REGRES**, nie jako zamiennik:

1. `regres.py` identyfikuje precyzyjny punkt regresji dla konkretnego pliku (importy, historia, rename/hash).
2. `defscan.py` i `refactor.py` dają szerszy kontekst strukturalny (duplikacje, atomizacja, większe fale zmian).
3. Najlepszy efekt daje pipeline: **REGRES (lokalna przyczyna) -> DEFSCAN/REFACTOR (kontekst systemowy) -> minimalny patch**.

## Uwagi praktyczne

- najlepiej skanować `--scan-root` możliwie wąsko (np. `frontend/src`), żeby przyspieszyć analizę
- przy dużych repo ustaw `--near-threshold` wyżej (`0.93-0.97`) dla mniejszej liczby false positive
- raport Markdown (`--out-md`) jest czytelny dla człowieka, JSON (`--out-json`) dla LLM/automatyzacji
- analiza ewolucji używa `git show` — nie modyfikuje working tree; dla dużych `--max-commits` może być wolniejsza, bo każdy commit wymaga osobnego `git show`
