Świetny pomysł — obecny `find.py` robi tylko jedno: liczy wystąpienia słowa. Do refaktoryzacji potrzeba znacznie więcej kontekstu. Oto co stworzę:

**Nowe tryby analizy:**
- `duplicates` — identyczne pliki po hashu treści
- `similar` — częściowe duplikaty treści (difflib, próg podobieństwa)
- `cluster` — grupowanie plików po wspólnych prefixach nazw (np. `encoder-*`)
- `deps` — graf importów/zależności między plikami
- `report` — JSON gotowy do wklejenia do LLM z pełnym kontekstemGotowe — `refactor.py` jako niezależny skrypt, zero zewnętrznych zależności (tylko stdlib Python 3.10+).

---

## Co nowego względem `find.py`

### Tryby

| Tryb | Co robi | Przykład |
|------|---------|---------|
| `find` | jak poprzednio + rozmiar, linie, JSON | `python refactor.py find encoder` |
| `duplicates` | identyczne pliki po MD5 — bezpieczne do usunięcia | `python refactor.py duplicates encoder` |
| `similar` | pary plików z podobieństwem ≥ N% (difflib) — kandydaci do scalenia | `python refactor.py similar encoder --min-sim 70` |
| `cluster` | grupuje po wspólnym prefixie nazwy (encoder-*, auto-encoder-*) | `python refactor.py cluster encoder --depth 2` |
| `deps` | kto importuje dany moduł / co on sam importuje | `python refactor.py deps encoder-core.service.ts` |
| `report` | JSON z wszystkim powyższym + hint dla LLM | `python refactor.py report encoder --out enc.json` |

### Kluczowe parametry

- `--min-sim 70` — próg podobieństwa treści (60% domyślnie)
- `--depth 2` — ile segmentów nazwy tworzy prefix (`encoder-core`, `auto-encoder`)
- `--min-group 3` — ignoruj klastry z mniej niż N plikami
- `--preview` — dołącz 2000 znaków podglądu treści do raportu (dla LLM)
- `--json` — każdy tryb zwraca JSON, można pipe'ować dalej

### Workflow dla LLM

```bash
# 1. Wygeneruj raport i wklej go do kontekstu LLM
python refactor.py report encoder --out enc.json --preview

for dir in connect-config connect-data connect-deleted connect-devtools connect-encoder connect-id connect-live-protocol connect-manager connect-menu-editor connect-menu-tree connect-protocol connect-reports connect-router connect-scenario connect-template connect-template2 connect-test connect-test-device connect-test-full connect-test-protocol connect-workshop; do
  python refactor.py report "$dir" --out "$dir.toon" --toon --preview
done

# Refactor report commands for all connect-* modules
python refactor.py report "connect-config" --out connect-config.toon --toon --preview
python refactor.py report "connect-data" --out connect-data.toon --toon --preview
python refactor.py report connect-deleted --out connect-deleted.toon --toon --preview
python refactor.py report "connect-devtools" --out connect-devtools.toon --toon --preview
python refactor.py report "connect-encoder" --out connect-encoder.toon --toon --preview
python refactor.py report connect-id --out connect-id.toon --toon --preview
python refactor.py report "connect-live-protocol" --out connect-live-protocol.toon --toon --preview
python refactor.py report "connect-manager" --out connect-manager.toon --toon --preview
python refactor.py report "connect-menu-editor" --out connect-menu-editor.toon --toon --preview
python refactor.py report "connect-menu-tree" --out connect-menu-tree.toon --toon --preview
python refactor.py report "connect-protocol" --out connect-protocol.toon --toon --preview
python refactor.py report "connect-reports" --out connect-reports.toon --toon --preview
python refactor.py report "connect-router" --out connect-router.toon --toon --preview
python refactor.py report "connect-scenario" --out connect-scenario.toon --toon --preview
python refactor.py report "connect-template" --out connect-template.toon --toon --preview
python refactor.py report "connect-template2" --out connect-template2.toon --toon --preview
python refactor.py report "connect-test" --out connect-test.toon --toon --preview
python refactor.py report "connect-test-device" --out connect-test-device.toon --toon --preview
python refactor.py report "connect-test-full" --out connect-test-full.toon --toon --preview
python refactor.py report "connect-test-protocol" --out connect-test-protocol.toon --toon --preview
python refactor.py report "connect-workshop" --out connect-workshop.toon --toon --preview

testql run .testql/generated/*.testql.toon.yaml --dry-run --quiet --output json > .testql/reports/iteration.json

# 2. Sprawdź konkretne duplikaty
python refactor.py duplicates encoder --json

# 3. Znajdź częściowe duplikaty (podobne testy/szablony)
python refactor.py similar encoder --min-sim 80

# 4. Klastry nazw — widać grupy do scalenia
python refactor.py cluster encoder --depth 2 --min-group 3
```

Wynikowy `enc.json` zawiera pole `llm_prompt_hint` z gotowym promptem do wklejenia do LLM razem z danymi.


przenalizuj jeszcze raz poprzez generator testow: testql czy wszystko działa porpzez naalzie raportow 
napraw spotkane błędy  ,
skorzystaj z pliku: /home/tom/github/maskservice/c2004/connect-workshop.toon
tam sa informacje statystyczne o frazie connect-workshop
aby poprawnie przeniść do zmodularyzowanej struktury ./connect-* tylko te istotne pliki
nie zaburzając struktury, aby wszytsko działało poprawnie przy testach testql

