# Wymagania

Wersja specyfikacji: 1.0. Data: 2026-11-06. Zakres bieżącej pracy: API. Jedna piekarnia, jeden katalog klientów, obsługa przez pracownika. Klienci składają zamówienia telefonicznie lub SMS-em i nie mają kont w aplikacji.

Dokument rozróżnia ustalenia rozmowy od proponowanych decyzji technicznych. Rejestr znajduje się w [decyzjach](09-decyzje.md). Zmiana propozycji nie wymaga przebudowy całego planu.

## Słownik

| Pojęcie | Znaczenie |
|---|---|
| Klient / kontrahent | Osoba lub gospodarstwo składające zamówienie; w API `Customer` |
| Produkt | Pozycja katalogu piekarni, np. chleb pszenny |
| Pieczenie | Oddzielny wypiek na konkretny dzień; w API `Bake` |
| Oferta pieczenia | Wskazane produkty katalogowe dostępne w tym pieczeniu |
| Zamówienie | Bieżące zamówienie jednego klienta na jedno pieczenie |
| Artykuł dodatkowy | Zakup spoza oferty, np. ziemniaki; nie jest produktem piekarni |
| Wiadomość | Oryginalny SMS i jego metadane; nie jest sama w sobie zamówieniem |
| Domyślne pieczenie | Wskazany przez pracownika termin dla SMS-ów bez kodu |
| Przyjęte zamówienie | Zamówienie `confirmed`, uwzględniane w produkcji |

## Wydania i wymagania

| ID | Wymaganie | Wydanie |
|---|---|---|
| R01 | Dodawanie, odczyt i aktualizacja klientów; archiwizacja zamiast usuwania historii | M0 |
| R02 | Wymagane nazwa i unikalny telefon, opcjonalne adres i notatki | M0 |
| R03 | Znacznik klienta pozwalający zamawiać artykuły dodatkowe | M0 |
| R04 | Katalog produktów z możliwością wyłączenia produktu | M0 |
| R05 | Oddzielne pieczenia z datą, oknem zapisów i własną ofertą | M0 |
| R06 | Ręczne tworzenie, zmiana, przyjęcie i anulowanie zamówienia | M0 |
| R07 | Osobne pozycje oferty i artykuły dodatkowe z ilością i jednostką | M0 |
| R08 | Bieżące sumy przyjętych pozycji oraz liczba zamówień oczekujących | M0 |
| R09 | Grupy klientów, także przynależność do kilku grup | M1 |
| R10 | Synonimy produktów, odmiany nazw i normalizacja polskich znaków | M1 |
| R11 | Jedno domyślne pieczenie dla całej piekarni; kilka innych terminów może mieć otwarte zapisy | M1 |
| R12 | SMS bez kodu dotyczy wskazanego domyślnego pieczenia; z kodem dotyczy wskazanego terminu | M1 |
| R13 | Parser słownikowy przygotowuje propozycję, zapisuje problemy i zachowuje oryginał | M1 |
| R14 | Wiadomości niejasne, kolejne, spóźnione i z dodatkami mają obsługę ręczną | M1 |
| R15 | Osobny numer bramki z wysyłką i odbiorem SMS | M2 |
| R16 | Ogłoszenie do wszystkich uprawnionych klientów lub wskazanych grup, bez duplikatów | M2 |
| R17 | Pieczenie może przyjmować zamówienia bez jakiegokolwiek ogłoszenia SMS | M2 |
| R18 | Historia wysyłki, odbioru, błędów i ponowień; brak podwojenia zamówienia po powtórzonym webhooku | M2 |
| R19 | Po terminie automatycznie powstaje PDF: produkcja, dodatki, zamówienia według klientów | M2 |
| R20 | Raport roboczy przy nierozstrzygniętych sprawach; wersjonowanie i finalizacja | M2 |
| R21 | Zmiana przyjętego zamówienia po terminie wymaga powodu i zostawia ślad | M2 |
| R22 | Kontrola dostępu do operacji pracownika; brak sekretów w repozytorium | M0 |

## Reguły biznesowe

**B01.** Aktywny klient ma jeden unikalny telefon w formacie kanonicznym. W M0 numer identyfikuje jednego klienta lub gospodarstwo. Dezaktywacja nie zwalnia numeru.

**B02.** Produkt piekarni w M0 zamawia się w całych sztukach. Ilość musi być dodatnia. Zmiana nazwy katalogowej nie zmienia nazw zapisanych w już utworzonych ofertach.

**B03.** Artykuł dodatkowy ma opis, dodatnią ilość dziesiętną i jednostkę `piece`, `kg` albo `g`. Dla `piece` wymagana jest ilość całkowita. Kwoty i ceny nie są częścią pierwszego kontraktu; to założenie do potwierdzenia.

**B04.** Dodanie dodatku wymaga `allow_extra_items=true`. Wyłączenie tego znacznika nie usuwa wcześniej przyjętych dodatków. Przy zmianie zamówienia bez nowych lub zwiększonych dodatków można zachować lub zmniejszyć dotychczasowe zatwierdzone pozycje; ponowne zwiększenie wymaga uprawnienia. Edycja opisu lub jednostki oznacza nowy dodatek.

**B05.** Jeden dzień wypieku ma jeden rekord pieczenia. Dwa dni oznaczają dwa rekordy. Ograniczenie `UNIQUE(bake_date)` przyjmujemy jako decyzję projektową dla jednej piekarni.

**B06.** Okno zapisów jest półotwarte: `accepting_from <= submitted_at < effective_cutoff`. `effective_cutoff` to wcześniejsza z wartości `order_deadline` i `closed_at`, jeśli zamknięto ręcznie. Czas równy granicy jest po terminie.

**B07.** Pieczenie musi zostać otwarte przez pracownika. Status `open` nie wystarcza, jeśli okno zapisów już minęło. Zakończenie okna nie zależy od pracy harmonogramu.

**B08.** Oferta jest edytowalna tylko w `draft`. Otwarcie wymaga co najmniej jednego aktywnego produktu i nieprzekroczonego terminu. Zamówienie może zawierać wyłącznie pozycje tej oferty.

**B09.** Istnieje jeden rekord zamówienia na parę klient-pieczenie, także po anulowaniu. Zmiany dotyczą tego rekordu. `confirmed` i tylko ten status zasila produkcję. Zamówienie musi mieć co najmniej jedną pozycję łącznie, a więc może składać się wyłącznie z uprawnionych dodatków.

**B10.** Pełna wymiana pozycji jest jedną transakcją. Błąd ostatniej pozycji nie może usunąć wcześniejszych danych. Nie przyjmujemy automatycznie poprawnego fragmentu niejasnego SMS-a.

**B11.** Po terminie można rozstrzygnąć szkic zgłoszony prawidłowo przed granicą: zmienić jego pozycje, zatwierdzić albo anulować. Przyjętych zamówień nie zmienia się po terminie zwykłym `PUT`; w M2 służy do tego jawna korekta z powodem. W M0 korekt poterminowych przyjętego zamówienia nie ma.

**B12.** Brak ogłoszenia SMS nie blokuje zamawiania. Lista klientów dopuszczonych do pieczenia i lista odbiorców kampanii to różne rzeczy. W M0 i M1 każdy aktywny klient może zamówić; grupy służą do wybierania odbiorców ogłoszeń, nie do blokowania zamówień.

**B13.** Domyślne pieczenie ustawia wyłącznie pracownik. Nie przełącza się po zamknięciu na kolejny tydzień. Nie ma domyślnego pieczenia osobno dla grup.

**B14.** Jawny kod ma pierwszeństwo przed ustawieniem domyślnym. Nieznany kod, dwa różne kody lub zamknięty wskazany termin kierują wiadomość do sprawdzenia, bez awaryjnego wyboru innego terminu.

**B15.** Oryginalna wiadomość jest zachowana. Brak kodu przy kilku otwartych pieczeniach oznacza świadomie przyjętą regułę wyboru domyślnego terminu, nie rozpoznanie intencji. Późnej odpowiedzi dotyczącej poprzedniego tygodnia nie da się zawsze odróżnić bez udziału człowieka.

**B16.** Nierozpoznany fragment nie staje się automatycznie dodatkiem. „Nie chcę”, „jak ostatnio”, literówki i produkt katalogowy spoza oferty wymagają wyjaśnienia. Dodatek od klienta bez uprawnienia także pozostaje widoczny jako problem.

**B17.** Kolejny SMS tego samego klienta na to samo pieczenie nie jest automatycznym dodaniem ani zastąpieniem zamówienia. W proponowanym MVP wymaga zatwierdzenia pełnego wyniku przez pracownika.

**B18.** Transportowe powtórzenie tej samej wiadomości nie tworzy nowego SMS-a ani nowej zmiany zamówienia. Różne wiadomości o identycznej treści pozostają różnymi wiadomościami.

**B19.** Ilości nie sumują różnych jednostek. Dodatki w raporcie są listą według klientów. „Ziemniaki” i „młode ziemniaki” nie łączą się automatycznie.

**B20.** W M2 raport końcowy wymaga rozwiązania niejasnych wiadomości, przetworzenia znanej kolejki wiadomości otrzymanych przed granicą oraz braku szkiców. Wiadomości po terminie można jawnie odrzucić albo zaakceptować korektą. Nowe dane nie zmieniają starego PDF: powstaje nowa wersja.

**B21.** W M2 otwarcie pieczenia planuje trwałe zadanie zamknięcia na order_deadline, niezależnie od notify_enabled. Zadanie zamyka zapisy i zleca pierwszy raport. Wcześniejsze ręczne close uruchamia ten proces wcześniej. Powtórzenie zadania nie tworzy drugiego pierwszego raportu. Przy nierozstrzygniętych sprawach automatyczny raport jest roboczy; kolejne rewizje można wygenerować ręcznie.

## Scenariusze odbioru

1. Pracownik dodaje Annę z uprawnieniem do dodatków, produkt pszenny i piątkowe pieczenie. Przyjmuje 2 chleby i 10 kg ziemniaków. Produkcja pokazuje 2 chleby, a dodatki pokazują oddzielnie 10 kg ziemniaków dla Anny.
2. Piątkowe pieczenie nie ma ogłoszenia. Anna wysyła SMS bez kodu. W M1/M2 wiadomość wskazuje domyślny piątek bez potrzeby wcześniejszej wysyłki.
3. Sobota jest drugim otwartym pieczeniem. Kod soboty kieruje do soboty. Brak kodu nadal kieruje do jawnie wybranego piątku.
4. Klient pisze „jeszcze jeden”. Piekarnia widzi poprzednie zamówienie i wiadomość, a ilość produkcyjna nie zmienia się bez decyzji.
5. Bramka wysyła ten sam webhook dwukrotnie. W bazie jest jedna wiadomość i najwyżej jedno zastosowanie jej treści.
6. Po granicy zapisów nie przyjmujemy nowego zwykłego zamówienia. Prawidłowo otrzymany wcześniej szkic można dokończyć. Raport pokazuje oczekujące sprawy.

## Poza zakresem

LLM, dowolny Python w szablonach, konta klientów, sklep internetowy, magazyn, faktury, płatności, wiele piekarni, powtarzalne automatyczne generowanie terminów i frontend Django. Ręczne utworzenie kolejnego tygodniowego pieczenia wystarcza w MVP.

## Źródła techniczne

To odnośniki do mechanizmów bibliotek, nie źródło wymagań biznesowych. Sprawdzone 2026-11-06; wersje zależności należy utrwalić podczas T01.

- [FastAPI: routery i większe aplikacje](https://fastapi.tiangolo.com/tutorial/bigger-applications/).
- [SQLAlchemy 2.x: ORM](https://docs.sqlalchemy.org/en/21/orm/quickstart.html).
- [Pydantic: modele danych](https://docs.pydantic.dev/latest/concepts/models/).
- [Alembic: migracje](https://alembic.sqlalchemy.org/en/latest/tutorial.html).
- [FastAPI: testowanie](https://fastapi.tiangolo.com/tutorial/testing/) oraz [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html).
- [SMSAPI: odbieranie SMS-ów i numery dwukierunkowe](https://www.smsapi.pl/odbior-sms).
