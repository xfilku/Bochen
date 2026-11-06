# Piekarnia: specyfikacja API i ścieżka nauki

Dokumentacja opisuje aplikację, którą napiszesz samodzielnie z pomocą AI jako nauczyciela. W repozytorium nie ma gotowej implementacji API. Są wymagania, kontrakty, projekt danych, zadania i scenariusze testów.

Zacznij od zadania **T01** w [planie implementacji](docs/06-plan-implementacji.md). Realizuj jedno zadanie naraz. Nie buduj jeszcze SMS-ów ani całej docelowej struktury katalogów.

| Dokument | Do czego służy |
|---|---|
| [Wymagania i zakres wydań](docs/01-wymagania.md) | Co aplikacja ma robić i co powstaje najpierw |
| [Architektura](docs/02-architektura.md) | Podział odpowiedzialności, pliki, baza, konfiguracja |
| [Modele danych](docs/03-modele.md) | Tabele, pola, relacje, ograniczenia i statusy |
| [Schematy API](docs/04-schemas.md) | Plan modeli Pydantic oraz przykłady danych |
| [Routery i endpointy](docs/05-routery-endpointy.md) | Metody, adresy, odpowiedzi i reguły operacji |
| [Plan implementacji](docs/06-plan-implementacji.md) | Konkretne zadania z zależnościami i testami |
| [Specyfikacja testów](docs/07-testy.md) | Scenariusze, dane, oczekiwane wyniki i strategia |
| [Praca z mentorem AI](docs/08-mentor.md) | Jak prosić o podpowiedzi i przegląd kodu |
| [Decyzje i założenia](docs/09-decyzje.md) | Co uzgodniono, co zaproponowano, co można zmienić |
| [OpenAPI wydania M0](docs/contracts/openapi-m0.json) | Maszynowy kontrakt pierwszego działającego API |

Wydania:

- **M0: ręczna obsługa piekarni.** Klienci, produkty, pieczenia, zamówienia, artykuły dodatkowe, sumy produkcji. Bez SMS, parsera i PDF.
- **M1: słowniki i symulowane SMS-y.** Grupy, aliasy, domyślne pieczenie, interpretacja treści, ręczne zatwierdzanie.
- **M2: użytkowe MVP SMS.** Prawdziwa bramka dwukierunkowa, wysyłka lub brak ogłoszeń, kolejka zadań, raport PDF, kontrolowane korekty.
- **Później:** Django, konfigurowalne szablony, formuły, LLM, płatności.

Artykuły dodatkowe należą już do M0. Podział na wydania porządkuje naukę; nie usuwa ich z uzgodnionego MVP.

Plik OpenAPI opisuje docelowy stan **M0**, a dokumenty opisowe także M1 i M2. Nie generuj z niego całej aplikacji. Korzystaj z niego do sprawdzania kolejno napisanych endpointów.

Weryfikacja samej dokumentacji i kontraktu, bez instalowania bibliotek aplikacji:

```powershell
python tools/validate_spec.py
```

Nie jest to uruchomienie testów przyszłego API. Właściwe testy napiszesz w zadaniach z planu.
