# Schematy Pydantic i dane JSON

Maszynowy kontrakt M0 jest w [OpenAPI](contracts/openapi-m0.json). Poniższe nazwy odpowiadają planowanym klasom w `app/schemas/`. Nie dziedziczymy wejścia bezpośrednio po modelu ORM. Klient nie może ustawiać ID, statusów ani czasów serwerowych przez dodatkowe pola.

## Zasady wspólne

- Pydantic 2; odczyty ORM przez `from_attributes=True`, wejścia przez `extra='forbid'`.
- Wymagane teksty: trim, co najmniej 1 znak. Nazwy/opisy pozycji maks. 160, notatki maks. 2000, adres maks. 500.
- ID i ilości pieczywa to ścisłe liczby całkowite: `true`, `1.2` i `"2"` nie są ilością Integer. ID > 0, ilość produktu 1-1000000.
- Decimal dodatku jest w JSON tekstem dziesiętnym bez wykładnika i przecinka, np. `"10"`, `"0.500"`; > 0, do 9 cyfr całkowitych i 3 po przecinku. Dla piece część ułamkowa musi wynosić zero. Odpowiedź serializuje do 3 miejsc.
- Daty i czasy jak w [architekturze](02-architektura.md); datetime bez offsetu daje 422.
- Listy wejściowe: najwyżej 100 pozycji katalogowych i 100 dodatkowych. `bake_product_id` nie może powtarzać się na liście. Co najmniej jedna pozycja łącznie.
- Odpowiedzi list: `Page[CustomerRead]` itd., zawsze items/total/limit/offset. Nie paginujemy pozycji wewnątrz jednego zamówienia.
- PATCH: wszystkie pola można pominąć, ale null dozwolone jest tylko tam, gdzie wskazano nullable. `{}` i nieznane pola dają 422.

## M0: klienci i produkty

| Schema | Pola |
|---|---|
| CustomerCreate | display_name: str; phone: str; address: str nullable = null; notes: str nullable = null; allow_extra_items: bool = false |
| CustomerUpdate | opcjonalne display_name, phone, address nullable, notes nullable, allow_extra_items, is_active |
| CustomerRead | id, display_name, phone, address nullable, notes nullable, allow_extra_items, is_active, created_at, updated_at |
| ProductCreate | name: str; description: str nullable = null; unit: Literal['piece'] = 'piece' |
| ProductUpdate | opcjonalne name, description nullable, is_active; jednostka nie jest edytowalna |
| ProductRead | id, name, description nullable, unit='piece', is_active, created_at, updated_at |

Normalizacja numeru i nazwy następuje przed sprawdzeniem unikalności. Duplikat to 409, nie 422. Normalizacja telefonu może zmienić wejściowe `500 600 700` na `+48500600700`.

## M0: pieczenia

| Schema | Pola |
|---|---|
| BakeCreate | name: str; bake_date: date; accepting_from: aware datetime; order_deadline: aware datetime |
| BakeUpdate | opcjonalne pola BakeCreate, wyłącznie dla draft; walidacja obejmuje wynik po nałożeniu PATCH |
| BakeRead | id, code, name, bake_date, accepting_from, order_deadline, status, opened_at nullable, closed_at nullable, created_at, updated_at |
| BakeProductCreate | product_id: positive int |
| BakeProductRead | id, bake_id, product_id, product_name: str, unit='piece' |

`BakeProductRead.product_name` jest nazwą ze snapshotu, a nie bieżącą nazwą w katalogu.

## M0: zamówienia

| Schema | Pola |
|---|---|
| OrderItemInput | bake_product_id: positive int; quantity: strict int 1-1000000 |
| OrderExtraItemInput | description: str; quantity: DecimalString; unit: piece/kg/g |
| OrderCreate | customer_id: positive int; bake_id: positive int; items: list[OrderItemInput] = []; extra_items: list[OrderExtraItemInput] = []; notes: nullable str = null |
| OrderReplace | items i extra_items są wymaganymi listami; notes: nullable str = null; nie przyjmuje customer_id ani bake_id |
| OrderItemRead | id, bake_product_id, product_id, product_name, quantity, unit='piece' |
| OrderExtraItemRead | id, description, quantity: DecimalString, unit |
| OrderRead | id, customer_id, customer_name, customer_phone, bake_id, status, source, submitted_at, notes nullable, items, extra_items, confirmed_at nullable, cancelled_at nullable, created_at, updated_at |

`OrderRead.customer_name` i customer_phone pochodzą ze snapshotu. Samo POST tworzy draft. Przyjęcie jest osobną operacją confirm. Ręczne zatwierdzenie dodatków jest świadomym działaniem pracownika.

Przykładowe utworzenie zamówienia; wszystkie wskazane ID muszą już istnieć:

```json
{
  "customer_id": 1,
  "bake_id": 1,
  "items": [{"bake_product_id": 1, "quantity": 2}],
  "extra_items": [{"description": "Ziemniaki", "quantity": "10.000", "unit": "kg"}],
  "notes": "Odbiór po 16:00"
}
```

Przy wymianie klient musi przesłać również listę, którą chce wyczyścić. Pominięcie wymaganej listy to 422:

```json
{"items":[{"bake_product_id":1,"quantity":3}],"extra_items":[],"notes":null}
```

## M0: sumy i błędy

| Schema | Pola |
|---|---|
| ProductionItem | bake_product_id, product_id, product_name, unit='piece', quantity: int >= 0 |
| AdditionalItemSummary | order_id, customer_id, customer_name, description, quantity: DecimalString, unit |
| BakeSummary | bake_id, confirmed_order_count, pending_order_count, products: list[ProductionItem], additional_items: list[AdditionalItemSummary], generated_at |
| ErrorDetail | field: str nullable, message: str |
| ErrorBody | code: str, message: str, details: list[ErrorDetail] |
| ErrorResponse | error: ErrorBody |
| HealthRead | status: Literal['ok'] |

Summary zawiera wszystkie pozycje oferty, również z ilością 0, uporządkowane po ID oferty. Dodatki są uporządkowane po order_id i ID pozycji. `pending_order_count` liczy draft. Cancelled nie zasila żadnej sumy.

## M1: grupy i aliasy

| Schema | Pola |
|---|---|
| GroupCreate / GroupUpdate | name: str 1-100; w Update wymagamy niepustego PATCH |
| GroupRead | id, name, created_at, updated_at |
| AliasCreate | text: str 1-160 |
| AliasRead | id, product_id, text, normalized_text, is_canonical |
| DefaultBakeUpdate | bake_id: positive int nullable; null usuwa wskazanie |
| SettingsRead | default_bake_id nullable, default_set_at nullable |

## M1: wiadomości i interpretacja

| Schema | Pola |
|---|---|
| SimulatedMessageCreate | from_phone: str; body: str 1-2000; brak received_at i provider_message_id w wejściu |
| MessageRead | id, direction, from_phone, to_phone, body, customer_id nullable, bake_id nullable, received_at nullable, routing_status, review_status, delivery_status nullable, applied_order_id nullable, latest_interpretation nullable, created_at |
| MessageAssign | customer_id: positive int; bake_id: positive int; reason: str 1-500 |
| ParsedCatalogItem | bake_product_id, quantity: positive int, matched_text: str |
| ParsedExtraCandidate | description: str, quantity: DecimalString nullable, unit: piece/kg/g nullable, original_text: str |
| ParseIssue | code: str; fragment: str nullable; message: str |
| InterpretationRead | id, parser_version, mode: new/review_existing, items: list[ParsedCatalogItem], extra_candidates: list[ParsedExtraCandidate], issues: list[ParseIssue], created_at |
| MessageApply | items: list[OrderItemInput]; extra_items: list[OrderExtraItemInput]; notes nullable = null; expected_order_version: positive int nullable = null; reason: str 1-500 |
| MessageIgnore | reason: str 1-500 |

`MessageApply` zawsze zawiera kompletny zamierzony wynik zamówienia. Przy istniejącym zamówieniu expected_order_version jest obowiązkowe; przy nowym ma być null. W M1 każde apply jest ręcznym przyjęciem, czyli tworzy lub zmienia confirmed w jednej transakcji. Opóźnione apply wiadomości otrzymanej przed granicą jest dozwolone. Spóźnione zgłoszenie nie jest dozwolone bez korekty M2. Ponowne apply tego samego message_id nie wykonuje zmiany.

Nieznany klient wymaga wcześniejszego dodania klienta i assign. Inny numer klienta niż nadawcy wymaga jawnego powodu; taka operacja jest wyłącznie ręczna. `OrderRead` od M1 ma dodatkowo version, a source dopuszcza manual i sms. Nie nadpisuj istniejącego zamówienia podczas samego parse.

## M2: kampanie, korekty, raporty

| Schema | Pola i warunki |
|---|---|
| BakeNotificationUpdate | notify_enabled: bool; osobny endpoint, nie obchodzi blokady edycji oferty |
| CustomerUpdate, rozszerzenie | sms_enabled: bool; wpływa na ogłoszenia, nie na możliwość zamawiania |
| CampaignRequest | audience: all/groups; group_ids: list[positive int] = []; dla groups co najmniej jeden, dla all pusta lista |
| CampaignPreview | text, recipient_count, excluded_count, estimated_segments nullable; podgląd niczego nie wysyła |
| CampaignRead | id, bake_id, status, text_snapshot, recipient_count, submitted_count, delivered_count, failed_count, unknown_count, created_at |
| OrderAmendmentCreate | items i extra_items jako pełne listy; notes nullable; expected_order_version: positive int; reason: str 1-1000; source_message_id nullable |
| ReportCreate | brak body; serwer buduje snapshot aktualnych danych |
| ReportRead | id, bake_id, revision, data_version, state, is_stale, unresolved_message_count, pending_order_count, created_at, finalized_at nullable, download_url |

Webhook dostawcy nie przyjmuje powyższego MessageRead. Ma format dostawcy oraz jego metodę autoryzacji. Adapter dopiero tworzy wewnętrzne dane wejściowe: provider, provider_message_id, from_phone, to_phone, body, received_at. Nie traktuj czasu podanego przez dowolnego wywołującego jako zaufanego czasu operatora.

## Kody interpretacji

`UNKNOWN_CUSTOMER`, `MISSING_DEFAULT_BAKE`, `UNKNOWN_BAKE_CODE`, `MULTIPLE_BAKE_CODES`, `OUTSIDE_WINDOW`, `AMBIGUOUS_ROUTING_TIME`, `MISSING_QUANTITY`, `UNKNOWN_FRAGMENT`, `PRODUCT_NOT_OFFERED`, `POSSIBLE_CHANGE_OR_NEGATION`, `EXTRA_ITEMS_NOT_ALLOWED`, `EXTRA_ITEM_REQUIRES_REVIEW`, `EXISTING_ORDER_REQUIRES_REVIEW`. To wynik interpretacji, nie zawsze błąd HTTP.

## Algorytm interpretacji M1

1. Zachowaj oryginalną treść. Wersję do porównań normalizuj osobno; dopasowania muszą nadal wskazywać oryginalne fragmenty. Nie zmieniaj przychodzącego SMS-a w bazie.
2. Odczytaj kod pieczenia bez rozróżniania wielkości liter, zanim szukasz ilości. Dwa różne kody dają issue. Liczba z P12 nie jest ilością produktu.
3. Rozpoznaj klienta po kanonicznym telefonie. Nieznanego nie zakładaj automatycznie.
4. Zachowaj istniejące ręczne przypisanie; w przeciwnym razie wybierz jawny kod, a przy jego braku default. Brak lub błąd jawnego kodu nie pozwala wybrać innego terminu. Wiadomości z received_at wcześniejszym od aktualnego default_set_at nie przypisuj automatycznie do nowego default.
5. Oceń okno względem received_at. Poza oknem zapisz issue, ale nie kasuj wiadomości. Ponowne parse nie zmienia zapisanego powiązania.
6. Pobierz aliasy i ofertę wskazanego pieczenia. Dopasuj pełne słowa i najdłuższe frazy. Znany produkt spoza oferty daje PRODUCT_NOT_OFFERED; nie staje się dodatkiem.
7. Dla dopasowanej frazy odczytaj jednoznaczną cyfrową ilość przed lub po niej, opcjonalnie z x lub szt. Brak, sprzeczne ilości albo powtórzone wzmianki o tym samym produkcie wymagają sprawdzenia. Nie sumuj powtórzeń samodzielnie. Liczby należące do aliasu, np. 500 g, są częścią nazwy.
8. Poza rozpoznanymi pozycjami ignoruj tylko zamknięty zestaw form grzecznościowych i łączników: proszę, poproszę, chcę, i oraz separatory. Nie ignoruj dowolnej reszty tekstu. Negacje, „jeszcze”, „zamiast” i „jak ostatnio” zawsze zgłaszają problem.
9. Fragment typu „10 kg ziemniaków” może dać kandydata dodatku. Obsłuż cyfry, kg/g/szt oraz dziesiętną kropkę lub przecinek w kontekście ilości. Przed podziałem po przecinkach rozpoznaj liczby dziesiętne. Nie zgaduj brakującej ilości, jednostki ani znaczenia „worek”. W JSON wynikowy Decimal używa kropki.
10. Dla klienta uprawnionego zgłoś EXTRA_ITEM_REQUIRES_REVIEW; dla nieuprawnionego EXTRA_ITEMS_NOT_ALLOWED. Pozostały tekst zgłoś jako UNKNOWN_FRAGMENT. W obu przypadkach zachowaj fragment.
11. Jeśli zamówienie klienta na ten termin już istnieje, ustaw mode=review_existing i issue. Nie dodawaj ani nie zastępuj ilości bez kompletnego ręcznego apply.
12. Zwróć propozycję. W M1/M2 bazowym nawet brak issue nie powoduje automatycznego przyjęcia. Tylko apply przechodzi przez te same reguły serwisu zamówień co ręczne API.

Przykładowy payload interpretacji, bez metadanych zapisanej wersji:

```json
{
  "parser_version": "dictionary-v1",
  "mode": "new",
  "items": [{"bake_product_id": 1, "quantity": 2, "matched_text": "2 pszenne"}],
  "extra_candidates": [{"description": "ziemniaków", "quantity": "10.000", "unit": "kg", "original_text": "10 kg ziemniaków"}],
  "issues": [{"code": "EXTRA_ITEM_REQUIRES_REVIEW", "fragment": "10 kg ziemniaków", "message": "Potwierdź dodatkowy zakup."}]
}
```

W tym przykładzie słownik zawiera alias pszenne, klient ma uprawnienie do dodatków, a ID oferty wynosi 1. Odmianę „ziemniaków” pracownik może poprawić na „Ziemniaki” przy apply; parser nie musi mieć słownika wszystkich możliwych zakupów.
