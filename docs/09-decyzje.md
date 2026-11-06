# Decyzje i otwarte założenia

## Uzgodnione z użytkownikiem

| ID | Decyzja |
|---|---|
| D01 | Backend FastAPI i SQLAlchemy; frontend Django później |
| D02 | Komunikacja SMS, nie e-mail |
| D03 | Może być osobny numer w bramce dwukierunkowej |
| D04 | Kilka terminów może mieć otwarte zapisy jednocześnie; inne dni wypieku są osobnymi pieczeniami |
| D05 | Jedno domyślne pieczenie dla całej piekarni, bez podziału według grup |
| D06 | Domyślny termin obsługuje SMS-y bez kodu; inny termin wymaga kodu albo ręcznej decyzji |
| D07 | Brak ogłoszenia SMS jest pełnoprawnym trybem pieczenia |
| D08 | Znacznik klienta zezwalający na artykuły dodatkowe; dodatki muszą być w MVP |
| D09 | Rozpoznawanie po słownikach w MVP; LLM oraz konfigurowalne szablony/formuły później |
| D10 | Użytkownik pisze aplikację sam, AI prowadzi i sprawdza; teraz powstaje specyfikacja, nie gotowy backend |
| D11 | Najpierw małe API klientów, produktów i zamówień, potem kolejne funkcje |

## Propozycje przyjęte do pierwszego kontraktu

To rozstrzygnięcia projektowe, których nie podano wprost. Można je zmienić przed rozpoczęciem właściwego zadania; nie blokują T01-T02.

| ID | Propozycja i powód |
|---|---|
| P01 | Jedna piekarnia, bez wielodostępności; jeden rekord wypieku na datę |
| P02 | Jeden klient/gospodarstwo na numer telefonu i jedno zamówienie na klienta w danym pieczeniu |
| P03 | Pieczywo w całych sztukach; dodatki piece/kg/g, Decimal do 3 miejsc |
| P04 | Brak cen i płatności w M0; użytkownik nie potwierdził jeszcze potrzeby kwot |
| P05 | Każdy aktywny klient może zamawiać na otwarte pieczenie, grupy wybierają odbiorców ogłoszeń |
| P06 | W M1 i M2 domyślnie wszystkie propozycje SMS wymagają ręcznego apply; automat pierwszych jednoznacznych wiadomości jest późniejszym przełącznikiem, nie częścią obecnego kontraktu |
| P07 | Kolejne wiadomości, negacje i dodatki zawsze wymagają ręcznej decyzji; nie sumujemy dopisków automatycznie |
| P08 | Po granicy dopuszczamy rozstrzygnięcie terminowego zgłoszenia, a nowe spóźnione przyjęcie wymaga jawnego wyjątku M2 |
| P09 | Kontrola dostępu w M0 przez klucz pracownika; konta i sesje Django później |
| P10 | Brak automatycznej zmiany default; datę w potwierdzeniu pokazujemy jawnie, jeśli potwierdzenia zostaną włączone |
| P11 | SMS-y potwierdzające domyślnie wyłączone, ogłoszenia również wymagają jawnego włączenia; ustawienia te są niezależne |
| P12 | W M2 raport końcowy wymaga rozwiązania wszystkich znanych spraw, stare rewizje zostają niezmienne |

## Do ustalenia przy właściwym etapie

- Przed T10: czy produkty piekarni także bywają na wagę? Jeśli tak, zmieniamy jednostki produktów i kontrakt ilości przed implementacją zamówień.
- Przed T10: czy M0 ma już liczyć ceny i kwoty? Obecna specyfikacja obejmuje wyłącznie ilości.
- Przed T27: dostawca, dostępność stałego numeru odbiorczego, sposób uwierzytelniania webhooku, czas odbioru i limity wiadomości. Nie obiecujemy przeniesienia obecnego numeru.
- Przed T28: czy włączyć płatne potwierdzenia i czy automatyczne przyjmowanie prostych pierwszych SMS-ów jest potrzebne? Bazowy proces ręczny pozostaje działający.
- Przed T30: środowisko serwera, generator PDF, miejsce przechowywania i kopii plików oraz czas przechowywania historii klientów/wiadomości.

## Ograniczenia interpretacji

SMS nie ma wiarygodnego wskazania „odpowiedź dotyczy piątku” tylko dlatego, że telefon pokazuje konwersację. Kod albo jawna reguła default rozwiązuje wybór techniczny. Wiadomość bez kodu odebrana po ręcznym przełączeniu na nowy tydzień może w intencji klienta dotyczyć starego terminu; system nie ma danych, aby to pewnie wykryć.

Opóźniony webhook z czasem odbioru wcześniejszym od aktualnego default_set_at wymaga ręcznej decyzji. Ponowne parsowanie już przypisanej wiadomości nie przepisuje jej do nowego default. Pracownik może wyczyścić default między zapisami, jeśli chce kierować takie odpowiedzi do sprawdzenia.

Nieznany produkt nie jest automatycznie zatwierdzonym zakupem. Flaga klienta otwiera możliwość dodatków, a człowiek potwierdza interpretację i możliwość realizacji. Parser bez LLM ma świadomie ograniczony zakres: cyfrowe ilości, znane aliasy i wykrywanie reszty tekstu.

## Jak zmieniać specyfikację

Zapisz datę i decyzję, zmień wymaganie B/R, model i schemę, endpoint oraz właściwy test. W M0 aktualizuj również OpenAPI i przykłady. Dopiero potem kod i migrację. Nie każda zmiana wymaga nowej wersji `/api/v2`; w trakcie nauki wystarczy uzgodniona zmiana kontraktu przed odbiorem wydania.
