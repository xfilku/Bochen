# Plan implementacji

Pracuj w kolejności. Każde zadanie kończy się działającym fragmentem, testami i krótkim omówieniem z mentorem. Lista nie oznacza, że masz utworzyć wszystkie pliki naraz. Pierwszy cel to M0, a nie kompletne M2.

Przy zadaniu zapisz status: do zrobienia / w trakcie / do sprawdzenia / ukończone. Ukończenie wymaga spełnienia kryteriów, a nie samego istnienia pliku. Testy odwołują się do [specyfikacji testów](07-testy.md).

## M0: ręczne zamówienia

### T01. Środowisko i zależności

- Zależności: brak.
- Cel: rozumieć interpreter, środowisko wirtualne i zależności projektu.
- Zrób: utwórz `.venv`, `.gitignore`, plik zależności i `.env.example`. Zainstaluj FastAPI z dodatkami standard, SQLAlchemy 2.x, Alembic, pydantic-settings, pytest i HTTPX. Zapisz konkretne użyte wersje; nie twórz jeszcze modeli.
- Kryterium: potrafisz wskazać interpreter projektu i sprawdzić importy. Sekrety, `.venv`, lokalna baza i cache testów nie trafiają do kontroli wersji.
- Sprawdzenie: odczyt wersji i importy tym samym Pythonem; bez testu kopiującego wynik `pip`.
- Wyjaśnij mentorowi: dlaczego globalne zainstalowanie biblioteki nie wystarcza dla `.venv`?

### T02. Pierwszy endpoint i pierwszy test

- Zależności: T01.
- Cel: żądanie, odpowiedź, status HTTP i uruchomienie testu.
- Zrób: utwórz `app/main.py`, obiekt FastAPI i GET `/health`. Dodaj test przez TestClient, potem uruchom serwer lokalnie i sprawdź `/docs`.
- Kryterium: endpoint zwraca dokładnie `{"status":"ok"}` z 200, test działa bez uruchamiania osobnego serwera.
- Testy: A01.
- Wyjaśnij: dlaczego test klienta nie potrzebuje ręcznie uruchomionego Uvicorn?

### T03. Konfiguracja, sesja i migracje

- Zależności: T02.
- Cel: rozdzielić engine, Session i model ORM.
- Zrób: konfigurację DATABASE_URL, bazę deklaratywną, zależność sesji, Alembic i odizolowaną bazę testową. Włącz FK na każdym połączeniu SQLite.
- Kryterium: test ma osobną bazę; sesja zamyka się także po błędzie; Alembic poprawnie ładuje metadane. Pierwsza migracja tabel powstanie w T05.
- Testy: przygotowanie fixtures do I01-I02; test realnego FK dokończ po T05.
- Wyjaśnij: czym różni się `flush()` od `commit()`?

### T04. Telefon, normalizacja i zegar

- Zależności: T03.
- Cel: wydzielić reguły niezależne od HTTP.
- Zrób: normalizację telefonu i nazw, pobieranie aware UTC przez podmienialny zegar, walidację granic okna.
- Kryterium: zachowujesz oryginalne nazwy, a klucze normalizacji są powtarzalne; SQLite nie gubi semantyki UTC.
- Testy: U01-U04, na razie U03 jako samodzielne reguły ilości.
- Wyjaśnij: dlaczego koniec okna jest wyłączny i dlaczego nie testujemy tego przez sleep?

### T05. Model i schemas klienta

- Zależności: T04.
- Cel: odróżnić tabelę od kontraktu JSON.
- Zrób: Customer, migrację, CustomerCreate/Update/Read. Sprawdź UNIQUE telefonu i odczyt ORM przez schemę.
- Kryterium: baza odrzuca duplikat nawet bez wcześniejszego SELECT; PATCH rozróżnia brak pola od null.
- Testy: I01-I03 w zakresie klienta, walidacja A02-A04 bez pełnych routerów.
- Wyjaśnij: dlaczego samo zapytanie „czy numer już istnieje” nie gwarantuje unikalności?

### T06. Router klientów

- Zależności: T05.
- Cel: pierwsza pełna funkcja API oparta na bazie.
- Zrób: POST/GET lista/GET szczegół/PATCH klientów. Obsłuż duplikat i brak klienta. Na tym etapie możesz zwracać błędy domenowe; format ujednolicisz w T15.
- Kryterium: utworzony klient pozostaje po restarcie, archiwizacja zachowuje rekord. Telefon jest normalizowany przed zapisem.
- Testy: A02-A06; końcową paginację dopracujesz w T15.
- Wyjaśnij: kiedy zwracasz 404, a kiedy 409?

### T07. Produkty

- Zależności: T06.
- Cel: powtórzyć CRUD bez mechanicznego kopiowania całego klienta.
- Zrób: Product, migrację, schemas i cztery endpointy. Wprowadź unikalną nazwę po normalizacji i jednostkę piece.
- Kryterium: można wyłączyć produkt, nie można zmienić jednostki; nie ma jeszcze aliasów.
- Testy: A07, A09, I03 w zakresie produktu. A08 dokończ z ofertą w T09.
- Wyjaśnij: dlaczego aktywność jest polem, a nie usunięciem rekordu?

### T08. Pieczenia i daty

- Zależności: T07.
- Cel: walidacja zależności między polami.
- Zrób: Bake, migrację, create/list/get/update. Kod generuj po flush w jednej transakcji. PATCH waliduje wynik po nałożeniu zmian.
- Kryterium: jeden dzień nie ma dwóch rekordów, niepoprawny zakres i czas bez strefy są odrzucone.
- Testy: A10, U04, I03.
- Wyjaśnij: dlaczego walidacja samych pól PATCH może przeoczyć błędny zakres?

### T09. Oferta i otwieranie zapisów

- Zależności: T08.
- Cel: relacja produktu z pieczeniem i przejścia stanu.
- Zrób: BakeProduct, list/add/remove oferty oraz open/close. Zapisuj snapshot nazwy i jednostki.
- Kryterium: nie otworzysz pustej oferty; po otwarciu nie zmienisz asortymentu; powtórzenie open/close nie zmienia czasu.
- Testy: A08, A11-A12, I02.
- Wyjaśnij: dlaczego pozycja zamówienia będzie wskazywać BakeProduct, a nie sam Product?

### T10. Modele i schemas zamówień

- Zależności: T09.
- Cel: relacja rodzic-dzieci i dwa rodzaje pozycji.
- Zrób: Order, OrderItem, OrderExtraItem, migracje, schemas wejścia i wyjścia. Uwzględnij Decimal i unikalną parę klient-pieczenie.
- Kryterium: dodatki są częścią modelu od początku, a nie polem tekstowym udającym ilości.
- Testy: U03, I02-I03, walidacyjne części A14-A15.
- Wyjaśnij: dlaczego `10.000` kg trzymamy jako Decimal, a nie float?

### T11. Tworzenie szkicu zamówienia

- Zależności: T10.
- Cel: pierwsza transakcja obejmująca kilka tabel.
- Zrób: serwis create_order oraz POST/list/get. Sprawdź klienta, okno, własność oferty, uprawnienia do dodatków i co najmniej jedną pozycję.
- Kryterium: powstaje cały draft albo nic. Czas i source ustala serwer. Drugie zamówienie tej samej pary daje 409.
- Testy: A13-A15, A19, I04.
- Wyjaśnij: dlaczego draft nie zwiększa jeszcze liczby chlebów do wypieku?

### T12. Przyjęcie zamówienia i sumy

- Zależności: T11.
- Cel: oddzielić operację biznesową od prostego ustawienia pola.
- Zrób: confirm i summary. Zliczaj confirmed, pokazuj wszystkie produkty oferty także z zerem, dodatki według klientów i licznik draft.
- Kryterium: wielokrotne confirm nie zmienia wyniku; nie sumujesz kg z piece.
- Testy: A16, I05.
- Wyjaśnij: dlaczego przechowywanie osobnego, ręcznie aktualizowanego licznika chleba byłoby ryzykowne?

### T13. Pełna wymiana zamówienia

- Zależności: T12.
- Cel: transakcja i rollback chroniący istniejące dane.
- Zrób: PUT zamówienia, walidację całej nowej zawartości przed zapisaniem i atomową wymianę pozycji. Przed terminem confirmed pozostaje confirmed.
- Kryterium: zła ostatnia pozycja nie usuwa starych. Wyłączenie uprawnienia nie kasuje dodatków, ale nie pozwala ich zwiększyć; porównuj sumę według znormalizowanego opisu i jednostki.
- Testy: A15, A17, I04.
- Wyjaśnij: czym różni się pełny PUT od PATCH?

### T14. Anulowanie, reopen i granica zapisów

- Zależności: T13.
- Cel: spójność stanów i czasu.
- Zrób: cancel/reopen, poterminowe dokończenie terminowego draft oraz blokadę zwykłej zmiany confirmed po granicy. Nie dodawaj jeszcze wyjątków z korektą.
- Kryterium: anulowanie nie usuwa historii, reopen nie tworzy drugiego rekordu; granica działa bez harmonogramu.
- Testy: A18-A20, U04.
- Wyjaśnij: czym różni się późne zatwierdzenie istniejącego zgłoszenia od nowego spóźnionego zgłoszenia?

### T15. Spójny kontrakt HTTP

- Zależności: T14.
- Cel: API przewidywalne dla przyszłego frontendu.
- Zrób: ErrorResponse i obsługę walidacji, filtry/paginację wszystkich list, ograniczenia parametrów, finalne response_model. Porównaj wygenerowane OpenAPI aplikacji z kontraktem dokumentacji.
- Kryterium: brak dowolnych pól ORM w odpowiedziach, total zgadza się z filtrem, błędy mają wspólny format.
- Testy: A05-A06, A21, A23-A24.
- Wyjaśnij: dlaczego `total` nie jest liczbą elementów bieżącej strony?

### T16. Dostęp i odbiór M0

- Zależności: T15.
- Cel: zamknąć małe działające wydanie.
- Zrób: X-API-Key, test ochrony wszystkich biznesowych operacji, krótki scenariusz od klienta do sum. Uporządkuj instrukcję uruchomienia i migracji.
- Kryterium: przechodzą wymagane testy M0; po restarcie można odczytać wcześniejsze zamówienie. Nie ma jeszcze parsera, SMS-ów ani PDF.
- Testy: A01-A24, U01-U04, I01-I05 w zakresie M0.
- Wyjaśnij: pokaż mentorowi pełną drogę danych jednego zamówienia.

## M1: słowniki i symulowane wiadomości

### T17. Grupy klientów

- Zależności: T16.
- Cel: relacja wiele do wielu.
- Zrób: modele grup i członkostw, migrację, schemas i router. Członkostwo dodawaj idempotentnie.
- Kryterium: jedna osoba może należeć do kilku grup; grupy nie blokują jej zamawiania.
- Testy: A25, I02-I03.
- Wyjaśnij: dlaczego lista ID w kolumnie tekstowej nie zastępuje tabeli powiązań?

### T18. Aliasy produktów

- Zależności: T17.
- Cel: jednoznaczny słownik.
- Zrób: ProductAlias, migrację kanonicznych nazw, endpointy oraz transakcyjną aktualizację nazwy głównej.
- Kryterium: alias nie może oznaczać dwóch produktów, a nazwa główna ma chroniony alias.
- Testy: A26, U02, I01 przy przejściu M0 -> M1.
- Wyjaśnij: czym różni się odmiana wyrazu od usunięcia polskich znaków?

### T19. Domyślne pieczenie

- Zależności: T18.
- Cel: jawna reguła biznesowa zamiast zgadywania.
- Zrób: singleton AppSettings i GET/PUT ustawienia. Ustawiaj default_set_at wyłącznie przy zmianie wskazania.
- Kryterium: najwyżej jeden default dla całej piekarni; koniec zapisów nie wybiera nowego terminu.
- Testy: A27, U08.
- Wyjaśnij: czego nie da się ustalić z samego numeru telefonu i treści „dwa chleby”?

### T20. Oryginalne wiadomości i symulator

- Zależności: T19.
- Cel: oddzielić wiadomość od zamówienia.
- Zrób: SmsMessage i MessageInterpretation, schemas, simulate/list/get/assign/ignore. Symulator używa czasu serwera i nie działa w produkcji.
- Kryterium: nieznany numer i spóźniony SMS nie giną; samo nadejście nie zmienia produkcji.
- Testy: A28 w zakresie zapisu, A30, S01-S02, S07.
- Wyjaśnij: dlaczego treść oryginalna musi pozostać mimo późniejszej korekty interpretacji?

### T21. Parser słownikowy

- Zależności: T20.
- Cel: testować interpretację bez sieci i bazy.
- Zrób: obsługę kodu, aliasów, liczbowych ilości przed/po nazwie, kandydatów dodatków i issue. Najpierw najprostszy przypadek, potem parametryzowane przykłady. Nie implementuj rozumienia dowolnego języka.
- Kryterium: parser nie zapisuje zamówienia; negacja, reszta tekstu i brak ilości nie dają wymyślonych pozycji.
- Testy: U05-U09, S08-S10; dane pomocnicze w examples/parser-cases.json.
- Wyjaśnij: dlaczego „nierozpoznane” nie oznacza automatycznie „ziemniaki do kupienia”?

### T22. Ręczne zastosowanie interpretacji

- Zależności: T21.
- Cel: kontrolować powtórzenia i konflikty edycji.
- Zrób: parse/apply, version zamówienia i sprawdzanie expected_order_version. Apply przyjmuje pełny ręcznie zatwierdzony wynik oraz zapisuje applied atomowo.
- Kryterium: drugie apply nie dolicza niczego, kolejny SMS nie nadpisuje sam poprzedniego zamówienia. Terminowe otrzymanie pozwala rozstrzygnąć wiadomość później.
- Testy: A28-A29, I04, S03-S05. Pełny konkurencyjny wariant I06 wykonasz na PostgreSQL w T25.
- Wyjaśnij: czym różni się duplikat webhooku od kolejnego SMS-a o tej samej treści?

### T23. Odbiór M1 na przykładach piekarni

- Zależności: T22.
- Cel: sprawdzić proces, nie tylko pojedyncze funkcje.
- Zrób: scenariusze piątek bez ogłoszenia, sobota z kodem, klient z ziemniakami, klient bez uprawnienia, dopisek, nieznany klient, wiadomość na granicy.
- Kryterium: każda sprawa ma widoczny status i można ją przyjąć albo odrzucić z powodem. Brak automatycznej wysyłki i przyjmowania.
- Testy: A25-A30, U05-U09, S01-S10 w symulacji. S06 przygotuj z zaufanym czasem adaptera w T27.
- Wyjaśnij: wskaż świadome ograniczenia parsera i reguły default.

## M2: użytkowe MVP SMS

### T24. PostgreSQL i migracje istniejących danych

- Zależności: T23.
- Cel: przygotować bazę do równoległego przetwarzania.
- Zrób: konfigurację PostgreSQL, ten sam zestaw migracji od pustej bazy, przeniesienie przykładowych danych i round-trip UTC/Decimal. Nie przepisuj warstwy biznesowej.
- Kryterium: dane i ID powiązań zachowane; testy nie łączą się z bazą roboczą.
- Testy: I01-I05, U04 na PostgreSQL.
- Wyjaśnij: dlaczego testy SQLite nie wystarczą do potwierdzenia zachowania blokad?

### T25. Współbieżne zatwierdzanie

- Zależności: T24.
- Cel: brak utraty danych przy dwóch żądaniach.
- Zrób: test równoległych apply i atomowe podnoszenie version. Zablokuj powtórne zastosowanie tej samej wiadomości w transakcji.
- Kryterium: jedna zmiana wygrywa, druga daje czytelny konflikt; żadnych częściowych pozycji.
- Testy: I03, I04, I06, A29.
- Wyjaśnij: dlaczego sprawdzenie wersji przed transakcją może nie wystarczyć?

### T26. Trwałe zadania

- Zależności: T25.
- Cel: zadania odporne na restart.
- Zrób: Job, pobieranie z blokadą, retry z ograniczeniem, odzyskanie osieroconego zadania i stan błędu. Zapis wiadomości i zadania musi być atomowy.
- Kryterium: dwa workery nie wykonują tego samego zadania równocześnie; po restarcie nie gubisz pracy.
- Testy: I07, I04.
- Wyjaśnij: co robić, gdy wysyłka mogła się udać, ale nie masz odpowiedzi?

### T27. Bramka: wybór i odbiór SMS

- Zależności: T26.
- Cel: podłączyć transport bez zmiany reguł biznesowych.
- Zrób: wybierz dostawcę obsługującego polski numer dwukierunkowy; sprawdź odbiór, podpisy/sekrety, identyfikatory, czas odbioru i ponowienia. Zapisz kontrakt adaptera, stuby i webhook. Rozróżnij received_at i czas przetwarzania.
- Kryterium: nie ma odpowiedzi ACK przed trwałym zapisem; duplikat nie tworzy drugiego zadania; opóźniony webhook sprzed zmiany default trafia do sprawdzenia.
- Testy: I09, I13, S01-S07, A30. Prawdziwy SMS wyłącznie w jawnym teście na własnym numerze.
- Wyjaśnij: jak zachowa się aplikacja, jeśli dostawca nie daje zaufanego czasu odbioru? Przyjmij zapisany czas odbioru webhooku i opisz ograniczenie.

### T28. Ogłoszenia i potwierdzenia

- Zależności: T27.
- Cel: kontrolowana wysyłka bez duplikowania odbiorców.
- Zrób: notify_enabled, sms_enabled, preview, kampanie, snapshot odbiorców, IdempotencyRecord, zadania wysyłki i callbacki statusów. Osobne potwierdzenie po przyjęciu zamówienia jest domyślnie wyłączone, dopóki pracownik nie włączy go w konfiguracji.
- Kryterium: odznaczona wysyłka nie blokuje zapisów; preview niczego nie wysyła; błąd/unknown jest widoczny i nie powoduje ślepej powtórki.
- Testy: A31, I08-I11, S01.
- Wyjaśnij: dlaczego delivered nie oznacza confirmed?

### T29. Kontrolowane korekty po terminie

- Zależności: T28.
- Cel: poprawiać błędy z zachowaniem historii.
- Zrób: amendments, pełny before/after, reason, expected_version, idempotencję oraz jawne przyjęcie spóźnionego SMS-a. Dodaj Bake.data_version i zwiększaj w każdej istotnej mutacji.
- Kryterium: zwykły endpoint nie omija terminu; każda poterminowa zmiana ma uzasadnienie i zmienia wersję danych raportowych.
- Testy: A32, I04, I06, I12, S05.
- Wyjaśnij: dlaczego usunięcie starego zamówienia i utworzenie nowego niszczy historię?

### T30. Raport PDF

- Zależności: T29.
- Cel: utrwalić to, co faktycznie ma zostać przygotowane.
- Zrób: wybierz generator PDF i font z polskimi znakami; przygotuj snapshot, trzy części raportu, rewizje, chronione pobieranie oraz finalizację porównującą data_version pod blokadą. Open planuje trwałe zamknięcie i pierwszy raport na deadline; ręczne close przyspiesza proces. Deduplikuj pierwszy raport po bake_id. Plik może powstać poza transakcją, ale publikacja musi sprawdzić zgodność wersji.
- Kryterium: pending oznacza raport roboczy; nowa wiadomość albo korekta nie zmienia starego pliku i blokuje finalizację starej wersji. Błąd zapisu pliku nie publikuje zepsutego raportu.
- Testy: P01-P05, I12-I13, A32.
- Wyjaśnij: dlaczego odczyt aktualnych danych przy każdym pobraniu nie jest historycznym raportem?

### T31. Odbiór użytkowego MVP

- Zależności: T30.
- Cel: pełny proces bez frontendu.
- Zrób: przejdź scenariusze wymaganiowe przez API, sprawdź restart workera, błędny webhook, brak ogłoszenia, dwa dni wypieku, dodatki, termin, korektę i dwie rewizje PDF. Uzupełnij instrukcję uruchomienia, kopii bazy oraz przechowywania plików.
- Kryterium: wszystkie testy właściwe M2 przechodzą na PostgreSQL; zwykły zestaw nigdy nie wysyła prawdziwych SMS-ów. Rzeczywistą integrację sprawdź osobno na własnych danych.
- Testy: A01-A32, U01-U09, I01-I13, S01-S10, P01-P05.
- Wyjaśnij: które ograniczenia pozostają świadomie, zanim zaczniesz Django lub LLM?

## Pierwsza sesja z mentorem

Otwórz T01 i T02. Zrób środowisko, health i jeden test. Poproś o sprawdzenie tych plików. Następnej lekcji nie zaczynaj od modeli wszystkich przyszłych tabel. Po ukończeniu każdego zadania zapisz krótko: co działa, jaki przypadek testujesz i czego jeszcze nie rozumiesz.
