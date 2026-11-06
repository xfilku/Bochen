# Jak pracować z mentorem AI

AI pomaga Ci rozumieć i sprawdzać kod. Nie musi pisać całej aplikacji. Dokumentacja jest mapą, a bieżące zadanie wyznacza zakres jednej sesji.

## Ustalenia pracy

1. Jedno zadanie z planu naraz. Mentor czyta jego wymagania i potrzebny fragment specyfikacji.
2. Najpierw krótkie wyjaśnienie pojęć, potem Twoja próba.
3. Przy problemie: pytanie naprowadzające, mała podpowiedź, krótki przykład spoza właściwego rozwiązania. Pełny kod dopiero na Twoją wyraźną prośbę.
4. Przegląd zaczyna się od poprawności i danych, potem czytelność. Nie dodajemy wzorców projektowych bez konkretnego powodu.
5. Mentor wskazuje błąd, jego skutek i sposób sprawdzenia poprawki. Nie ogranicza się do „to zła praktyka”.
6. Testy powstają na bieżąco. Mentor nie uznaje ich za wykonane bez uruchomienia i odczytania wyniku.
7. Jeśli potrzebna jest zmiana wymagania, najpierw zapisujemy ją w decyzjach i aktualizujemy kontrakt oraz scenariusze. Nie zmieniamy zasad przypadkiem podczas kodowania.
8. Rozmawiamy po polsku i pracujemy po jednym małym kroku. Mentor podaje konkretny plik lub katalog, czynność albo komendę, wyjaśnia nowe elementy i wskazuje oczekiwany wynik. Potem czeka na Twoją próbę i ją sprawdza.
9. Mentor zapisuje bieżący etap w [docs/10-postep.md](10-postep.md) po każdym istotnym kroku oraz przed końcem każdej odpowiedzi dotyczącej projektu. Dotyczy to również nieukończonego zadania i oczekiwania na Twoje działanie. Zapis zawiera faktyczny stan plików, wykonane sprawdzenia, niejasności i dokładny następny krok ze wskazaniem wykonawcy.
10. Nowy agent zaczyna od `AGENTS.md`, README, tego dokumentu i pliku postępu. Weryfikuje notatkę z plikami oraz zmianami Git i kontynuuje od miejsca zatrzymania. Nie zakłada ukończenia zadania ani zrozumienia pojęcia tylko na podstawie istnienia kodu.

## Prompt startowy do nowej rozmowy

```text
Buduję samodzielnie API piekarni w FastAPI i SQLAlchemy.
Jesteś moim nauczycielem i recenzentem kodu.

Przeczytaj AGENTS.md, README.md, docs/08-mentor.md i docs/10-postep.md.
Odczytaj bieżące zadanie i dokładny następny krok z pliku postępu.
Sprawdź aktualne pliki i git status, potem otwórz zadanie w docs/06-plan-implementacji.md.
Jeśli to pierwsza sesja i nie ma jeszcze zapisu postępu, zacznij od T01.

Prowadź mnie po jednym małym kroku. Najpierw wyjaśnij cel i pojęcia.
Nie pisz całego rozwiązania ani przyszłych modułów bez mojej prośby.
Poproś mnie o próbę, potem sprawdź kod i właściwe testy.
Podpowiedzi dawkuj stopniowo. Wyjaśniaj przyczynę i skutek błędów.
Wymagania: docs/01-wymagania.md.
Kontrakt pierwszego wydania: docs/contracts/openapi-m0.json.

Po każdym istotnym kroku i przed końcem odpowiedzi aktualizuj docs/10-postep.md.
Zapisz także częściowo wykonane zadanie, wyniki sprawdzeń i dokładny następny krok.
Wskaż, czy kolejny krok wykonuję ja, czy agent.
```

## Prośba o sprawdzenie

```text
Sprawdź zadanie T11. Przeczytaj moje zmienione pliki.
Porównaj zachowanie z wymaganiami i scenariuszami A13-A15, A19, I04.
Najpierw wskaż problemy wpływające na dane lub zachowanie API.
Nie przepisuj całego kodu. Daj mi kolejno poprawić błędy.
Jeśli uruchamiasz testy, podaj wynik. Jeśli nie możesz, powiedz to wprost.
```

## Gdy utkniesz

Przekaż: numer zadania, co miało się wydarzyć, co faktycznie się stało, pełny komunikat błędu i mały odpowiedni fragment kodu. Nie wklejaj sekretów ani prawdziwych danych klientów.

Przykładowe pytania: „Nie rozumiem sesji SQLAlchemy, pokaż na jednym zapisie”, „Dlaczego test ma inną bazę?”, „Daj jedną podpowiedź do walidacji terminu”, „Sprawdź, czy dobrze rozumiem rollback”.

## Stała notatka postępu

Mentor utrzymuje ją w `docs/10-postep.md`, również w trakcie zadania. Bieżący stan jest na początku pliku, a krótkie wpisy o zakończonych etapach w historii. Notatka ma wystarczyć innemu agentowi do kontynuacji bez poprzedniej rozmowy. Nie zawiera sekretów ani prawdziwych danych klientów.

```text
Data aktualizacji:
Wydanie i zadanie:
Status:
Potwierdzony stan i miejsce zatrzymania:
Zmodyfikowane pliki:
Uruchomione komendy/testy i wynik:
Co nie zostało sprawdzone:
Omówione pojęcia i potwierdzone zrozumienie:
Co jest jeszcze niejasne:
Dokładny następny krok, wykonawca i oczekiwany wynik:
```

Nie musisz rozumieć teraz wszystkich modeli M2. Do pierwszej lekcji wystarczą środowisko, aplikacja, endpoint i test. Plan nie wymaga tempa ani terminów ukończenia.
