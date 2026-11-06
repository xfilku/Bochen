# Specyfikacja testów

Testy powstają wraz z zadaniami, nie po całym projekcie. Poniższe identyfikatory pozwalają wskazać konkretny scenariusz w zadaniu i rozmowie z mentorem. To plan testów aplikacji; w tym repozytorium nie ma jeszcze działającego API ani jego wykonanych testów.

## Dane i organizacja

Fixtures: `clock` z ustalonym aware UTC, `db_session` w odizolowanej bazie tmp_path, klient TestClient z nadpisaną zależnością sesji, nagłówek testowego klucza. Testy nie korzystają z pliku roboczego piekarni. Żadnych prawdziwych SMS-ów w zwykłym `pytest`.

Domyślna chwila: 2030-11-20 12:00:00Z. Pieczenie piątkowe: bake_date 2030-11-22, accepting_from 2030-11-18T08:00:00Z, deadline 2030-11-21T17:00:00Z (18:00 w Warszawie). Sobota: 2030-11-23 z oddzielną ofertą. Klient Anna może zamawiać dodatki, Jan nie. Produkty: pszenny, żytni, bułki. ID pobieraj z odpowiedzi, zamiast zakładać wartości 1,2,3.

Jednostkowe testy nie wymagają HTTP ani bazy. API testuje kontrakt i reguły użytkowe. Integracyjne sprawdzają transakcje, migracje, adapter i współbieżność. Używaj parametryzacji tam, gdzie wynikają z niej różne przypadki brzegowe. Nie testuj samego faktu, że przypisano atrybut klasy.

## Jednostkowe

| ID | Scenariusz i oczekiwany wynik |
|---|---|
| U01 | `500 600 700`, `+48 (500) 600-700`, `0048500600700` -> ten sam telefon; litery i za długie numery -> błąd |
| U02 | `ŻYTNI`, `zytni`, nadmiar spacji -> ten sam klucz; `ł` -> `l`; oryginał nie jest nadpisany |
| U03 | Produkt: 1 i 2 OK; 0, -1, true, 1.5, tekst "2" błąd. Dodatek: "0.500" kg OK, zero błąd, "1.5" piece błąd, >3 miejsc błąd |
| U04 | Początek okna włącznie, koniec wyłącznie; równoważne offsety; brak tz odrzucony; UTC zapis/odczyt; daty przy zmianie czasu Warszawy |
| U05 | `P12 2 żytnie, bułki x4` -> właściwe ilości; liczba 12 z kodu nie staje się ilością |
| U06 | Najdłuższy alias i granice słów; `żytni z ziarnami` nie jest rozbity na dwa produkty; waga w nazwie `pszenny 500 g` nie staje się zamówieniem 500 sztuk |
| U07 | Negacja, „jeszcze”, „zamiast”, „jak ostatnio”, brak ilości i reszta tekstu -> issue, bez automatycznego przyjęcia fragmentu |
| U08 | Kod ma pierwszeństwo; nieznany/dwa kody nie używają default; bez kodu bierze default; default nie zmienia się sam |
| U09 | Kandydat `10 kg ziemniaków` zachowuje tekst i jednostkę; `10,5 kg` daje Decimal 10.500 i nie rozbija się na dwie pozycje; brak uprawnienia daje issue; podziękowanie nie staje się dodatkiem |

## API M0

| ID | Dane i oczekiwane zachowanie |
|---|---|
| A01 | GET health -> 200 i status ok, bez klucza |
| A02 | POST poprawnego klienta -> 201, normalizacja telefonu, domyślne false/true zgodnie ze schemą |
| A03 | Drugi równoważny telefon, także po archiwizacji pierwszego -> 409 PHONE_ALREADY_EXISTS |
| A04 | PATCH tylko notes zachowuje telefon; notes=null czyści; display_name=null i {} -> 422; is_active=false archiwizuje |
| A05 | Lista klientów: q i is_active, total po filtrze, puste wyniki, granice stron |
| A06 | Nieistniejący klient przy GET/PATCH -> 404 bez ujawniania SQL |
| A07 | Produkt z nazwą normalizującą się do istniejącej -> 409; unit inne niż piece -> 422 |
| A08 | Nazwa produktu zmieniona po dodaniu do oferty nie zmienia snapshotu; wyłączony produkt zachowuje historię |
| A09 | PATCH unit lub nieznane pole produktu -> 422; nieprawidłowa pusta nazwa -> 422 |
| A10 | Złe okno, brak tz, deadline lokalnie po dniu wypieku -> 422; druga identyczna data wypieku -> 409 |
| A11 | Oferta: drugi ten sam produkt -> 409; nieaktywny -> 409; nieistniejący -> 404; cudza pozycja przy DELETE -> 404 |
| A12 | Open pustej oferty -> 409; poprawne open -> 200; edycja otwartej oferty -> 409; powtórzone open/close nie zmienia pierwotnych czasów |
| A13 | POST zamówienia -> draft; nie zwiększa produkcji; customer/bake/source/status nie są samowolnie zmienialne |
| A14 | Puste obie listy i powtórzony bake_product_id -> 422; obca oferta -> 409; brakujący FK -> 404 |
| A15 | Dodatek Anny dozwolony, Jana -> 409; same dodatki dozwolone dla Anny; wyłączenie uprawnienia nie usuwa starych dodatków, ale blokuje ich zwiększenie |
| A16 | Confirm zwiększa produkcję raz; powtórne confirm nie podwaja; summary rozdziela dodatki od pieczywa |
| A17 | PUT zastępuje całą zawartość, zachowuje status; błędna ostatnia pozycja powoduje brak jakichkolwiek zmian |
| A18 | Cancel usuwa wpływ na sumy bez usuwania pozycji; ponowne cancel bez skutku; reopen daje draft, następne confirm działa; confirmed nie daje się reopen |
| A19 | Sekunda przed granicą dopuszcza nowe zamówienie; równa i późniejsza chwila daje 409, także przy statusie open |
| A20 | Draft zgłoszony przed granicą można poprawić/confirm/cancel po granicy; confirmed nie można zwyczajnie PUT/cancel; nowe POST po granicy jest blokowane |
| A21 | Nieistniejące zasoby -> 404; zero ID, limit=0/101, offset<0 -> 422; brak sesji po błędzie nie psuje następnego żądania |
| A22 | Wszystkie biznesowe metody bez/z błędnym kluczem -> 401; z kluczem działają; health pozostaje publiczny |
| A23 | Walidacja i konflikty mają ErrorResponse; dodatkowe pole status na POST orders odrzucone; niepoprawny JSON daje 422 |
| A24 | Listy produktów, pieczeń i zamówień: łączenie filtrów, total, stabilna kolejność; odwrotny zakres dat -> 422 |

## API M1/M2

| ID | Scenariusz i oczekiwany wynik |
|---|---|
| A25 | Członkostwo w grupie dodane dwa razy nadal występuje raz; lista respektuje paginację; grupa nie blokuje przyjęcia zamówienia |
| A26 | Alias kolidujący z aliasem/nazwą innego produktu -> 409; kanoniczny alias nieusuwalny; obcy alias -> 404 |
| A27 | Ustaw/wyczyść default; odrzucenie closed; zamknięcie default nie wybiera kolejnego; powtórzenie ustawienia tego samego ID nie zmienia default_set_at |
| A28 | Symulacja zapisuje oryginał i propozycję, nie zamówienie; apply przyjmuje ręczny wynik; endpoint niewidoczny w produkcji |
| A29 | Ponowne apply tej samej wiadomości nie zmienia danych; zła wersja istniejącego zamówienia -> 409; parse nie nadpisuje zamówienia |
| A30 | Nieznany numer i SMS po granicy są zachowane jako pending; assign/ignore wymagają powodu; nie można zmienić przypisania applied |
| A31 | notify_enabled=false blokuje kampanię, nie odbiór; preview bez skutków; powtórzony Idempotency-Key nie dubluje wysyłki; inny body z tym samym kluczem -> 409 |
| A32 | Korekta wymaga powodu i wersji, zapisuje audyt; finalizacja raportu starego lub z oczekującymi sprawami -> 409 |

## Integracyjne

| ID | Scenariusz i oczekiwany wynik |
|---|---|
| I01 | Alembic upgrade od pustej bazy; upgrade istniejącej M0 do M1 zachowuje zamówienia i tworzy aliasy; downgrade/upgrade ostatniej migracji na bazie testowej |
| I02 | FK są faktycznie aktywne; bezpośredni zapis nieistniejącego powiązania zostaje odrzucony |
| I03 | Ograniczenia UNIQUE zatrzymują duplikaty niezależnie od sprawdzenia w Pythonie; równoległy wariant na PostgreSQL w M2 |
| I04 | Niepowodzenie w połowie wymiany pozycji i podczas apply cofa całą transakcję, także status wiadomości |
| I05 | Dwa confirmed, jeden draft i jeden cancelled dają sumę tylko dwóch; produkty bez zamówień mają zero; kg nie miesza się ze sztukami |
| I06 | Dwa równoległe apply z tą samą expected_version: jedna zmiana wygrywa, druga dostaje konflikt; brak utraty danych |
| I07 | Restart po pobraniu zadania pozwala odzyskać je po wygaśnięciu blokady; dwa workery nie przetwarzają go jednocześnie |
| I08 | Timeout po możliwym przyjęciu SMS przez dostawcę -> unknown lub odtworzenie wyniku po idempotencji; brak ślepej podwójnej wysyłki |
| I09 | Podpis/sekret webhooku sprawdzony; zły nie tworzy wiadomości; ten sam identyfikator dwukrotnie daje jeden zapis i jedno zadanie |
| I10 | Statusy dostawy poza kolejnością nie cofają delivered do submitted; nieznany ID nie zmienia obcej wiadomości |
| I11 | Odbiorcy z dwóch nakładających się grup są deduplikowani; nieaktywny/sms_enabled=false wyłączony; późniejsza zmiana grup nie zmienia kampanii |
| I12 | Raport przechowuje snapshot; zmiana zamówienia lub nowa istotna wiadomość zwiększa data_version; stary PDF identyczny bajtowo |
| I13 | SMS otrzymany przed granicą, lecz przetworzony po niej, zachowuje terminowość; kolejka i pending blokują finalizację; deadline automatycznie zleca pierwszy raport, również bez ogłoszenia; powtórzone zadanie nie tworzy duplikatu |

## Przypadki SMS wynikające z rozmowy

| ID | Scenariusz |
|---|---|
| S01 | Pieczenie bez ogłoszenia, znany klient pisze sam -> poprawne rozpoznanie default bez kampanii |
| S02 | Piątek default i sobota open; bez kodu -> piątek, kod soboty -> sobota |
| S03 | Jednoznaczne pierwsze zamówienie nadal czeka na ręczne apply w domyślnym trybie M1/M2 |
| S04 | Dwa SMS-y o tej samej treści z różnymi ID są dwiema wiadomościami; drugi nie podwaja zamówienia sam |
| S05 | received_at przed granicą, przetwarzanie po niej -> można przyjąć; received_at równe granicy -> do ręcznej decyzji poterminowej |
| S06 | Opóźniony webhook z received_at wcześniejszym od default_set_at -> AMBIGUOUS_ROUTING_TIME, bez nowego automatycznego przypisania |
| S07 | Nieznany kod, dwa kody lub jawnie zamknięte pieczenie -> nie używamy default jako awaryjnego terminu |
| S08 | Literówka, „nie chcę”, produkt znany spoza oferty -> nie staje się automatycznie dodatkiem |
| S09 | „2 pszenne i 10 kg ziemniaków” -> pieczywo plus kandydat dodatku; uprawnienie i ręczne przyjęcie wymagane |
| S10 | „Jak ostatnio, dziękuję” -> problem do wyjaśnienia, bez wymyślonych ilości i produktów |

## PDF

| ID | Scenariusz |
|---|---|
| P01 | PDF zawiera właściwe sumy pieczywa, dodatki z jednostkami i przypisanie do klientów |
| P02 | Polskie znaki są widoczne i możliwe do wydobycia jako tekst; wielostronicowa lista nie gubi pozycji |
| P03 | Draft/pending/znane zadania sprzed granicy -> raport roboczy; finalizacja daje 409 |
| P04 | Korekta albo późny odbiór istotnej wiadomości oznacza poprzedni raport jako stale; nowa rewizja nie podmienia starego pliku |
| P05 | Pobranie wymaga autoryzacji; storage_key nie pozwala czytać arbitralnych ścieżek serwera |

## Śledzenie wymagań i odbiór wydań

| Wymagania | Testy |
|---|---|
| R01-R03 | A02-A06, A15, U01 |
| R04-R05 | A07-A12, U02, U04 |
| R06-R08 | A13-A20, I04-I05 |
| R09-R14 | A25-A30, U05-U09, S01-S10 |
| R15-R18 | A31, I07-I11, I13 |
| R19-R21 | A32, I12-I13, P01-P05 |
| R22 | A22-A23, I09, P05 |

M0 kończysz po przejściu A01-A24, U01-U04 i I01-I05 w odpowiednim zakresie M0. M1 dodaje A25-A30, U05-U09 i S01-S10 z symulatorem. M2 dodaje resztę i powtarza migracje oraz integrację na PostgreSQL.

Komendy docelowe, dopiero po utworzeniu testów:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit -q
.\.venv\Scripts\python.exe -m pytest tests/api -q
.\.venv\Scripts\python.exe -m pytest tests/integration -q
```

Testy wymagające rzeczywistej bramki oznacz osobnym markerem i uruchamiaj wyłącznie jawnie na własnych numerach testowych. Rutynowe testy adaptera korzystają z zapisanych przykładowych odpowiedzi i stubów HTTP. Nie wymagamy arbitralnego procentu coverage; obowiązkowe są wymienione reguły i przypadki brzegowe.
