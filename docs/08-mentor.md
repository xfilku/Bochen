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

## Prompt startowy do nowej rozmowy

```text
Buduję samodzielnie API piekarni w FastAPI i SQLAlchemy.
Jesteś moim nauczycielem i recenzentem kodu.

Przeczytaj README.md oraz docs/08-mentor.md.
Moje bieżące zadanie: T01 z docs/06-plan-implementacji.md.

Prowadź mnie po jednym małym kroku. Najpierw wyjaśnij cel i pojęcia.
Nie pisz całego rozwiązania ani przyszłych modułów bez mojej prośby.
Poproś mnie o próbę, potem sprawdź kod i właściwe testy.
Podpowiedzi dawkuj stopniowo. Wyjaśniaj przyczynę i skutek błędów.
Wymagania: docs/01-wymagania.md.
Kontrakt pierwszego wydania: docs/contracts/openapi-m0.json.

Na końcu zapisz, co ukończyłem i jaki jest dokładnie następny krok.
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

## Notatka po zadaniu

```text
Zadanie:
Status:
Zmodyfikowane pliki:
Uruchomione testy i wynik:
Czego się nauczyłem:
Co jest jeszcze niejasne:
Następne zadanie:
```

Nie musisz rozumieć teraz wszystkich modeli M2. Do pierwszej lekcji wystarczą środowisko, aplikacja, endpoint i test. Plan nie wymaga tempa ani terminów ukończenia.
