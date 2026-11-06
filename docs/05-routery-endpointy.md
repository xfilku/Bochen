# Routery i endpointy

Adresy w tabelach, poza `/health`, mają prefiks `/api/v1`. Wszystkie operacje pracownika wymagają `X-API-Key`. Parametry ścieżki to dodatnie Integer. Szczegółowe pola wejścia i wyjścia: [schemas](04-schemas.md). Kontrakt M0: [OpenAPI](contracts/openapi-m0.json).

W tabelach `Page[X]` to paginowany wynik. Każda lista biznesowa ma limit/offset; wyjątkiem są małe kompletne listy oferty i aliasów. Odczyt pojedynczego nieistniejącego zasobu daje 404. Błędy formatu, pusty PATCH i nieznane pola dają 422. Brak uprawnień daje 401.

## M0: health.py, customers.py, products.py

| Metoda i ścieżka | operationId / funkcja | Wejście | Sukces | Ważne reguły |
|---|---|---|---|---|
| GET /health | health | brak | 200 HealthRead | Publiczny; nie wykonuje mutacji |
| POST /customers | create_customer | CustomerCreate | 201 CustomerRead | 409 PHONE_ALREADY_EXISTS |
| GET /customers | list_customers | q?, is_active?, limit, offset | 200 Page[CustomerRead] | q wyszukuje fragment nazwy albo kanonicznego telefonu |
| GET /customers/{customer_id} | get_customer | brak | 200 CustomerRead | Także nieaktywny |
| PATCH /customers/{customer_id} | update_customer | CustomerUpdate | 200 CustomerRead | Telefon unikalny również w archiwum |
| POST /products | create_product | ProductCreate | 201 ProductRead | 409 PRODUCT_NAME_EXISTS |
| GET /products | list_products | q?, is_active?, limit, offset | 200 Page[ProductRead] | q po nazwie po normalizacji |
| GET /products/{product_id} | get_product | brak | 200 ProductRead | Także nieaktywny |
| PATCH /products/{product_id} | update_product | ProductUpdate | 200 ProductRead | Nie modyfikuje historycznych ofert |

Nie ma DELETE klienta ani produktu. Archiwizacja to PATCH is_active=false. Brak filtra is_active zwraca obie grupy.

## M0: bakes.py

| Metoda i ścieżka | operationId | Wejście | Sukces | Ważne reguły |
|---|---|---|---|---|
| POST /bakes | create_bake | BakeCreate | 201 BakeRead | Draft; 409 BAKE_DATE_EXISTS |
| GET /bakes | list_bakes | status?, date_from?, date_to?, limit, offset | 200 Page[BakeRead] | Daty włącznie; date_from > date_to daje 422 |
| GET /bakes/{bake_id} | get_bake | brak | 200 BakeRead | |
| PATCH /bakes/{bake_id} | update_bake | BakeUpdate | 200 BakeRead | Tylko draft; walidacja po połączeniu z bieżącymi polami |
| GET /bakes/{bake_id}/products | list_bake_products | brak | 200 list[BakeProductRead] | Cała oferta, po ID rosnąco |
| POST /bakes/{bake_id}/products | add_bake_product | BakeProductCreate | 201 BakeProductRead | Draft; aktywny produkt; 409 OFFER_ITEM_EXISTS |
| DELETE /bakes/{bake_id}/products/{bake_product_id} | remove_bake_product | brak | 204 bez body | Draft; obce ID oferty daje 404 |
| POST /bakes/{bake_id}/open | open_bake | bez body | 200 BakeRead | Niepusta oferta, aktywne produkty, deadline w przyszłości |
| POST /bakes/{bake_id}/close | close_bake | bez body | 200 BakeRead | Zapisuje pierwsze closed_at; nie anuluje szkiców |
| GET /bakes/{bake_id}/summary | get_bake_summary | brak | 200 BakeSummary | Tylko confirmed w ilościach; draft w liczniku oczekujących |

Kody konfliktów: BAKE_NOT_DRAFT, BAKE_NOT_OPEN, BAKE_CLOSED, EMPTY_OFFER, INACTIVE_PRODUCT, ORDER_WINDOW_CLOSED. Open może nastąpić przed accepting_from, ale zamawianie zaczyna się dopiero w oknie. Kolejne identyczne open/close są idempotentne jak w modelach.

## M0: orders.py

| Metoda i ścieżka | operationId | Wejście | Sukces | Ważne reguły |
|---|---|---|---|---|
| POST /orders | create_order | OrderCreate | 201 OrderRead | Tworzy draft, czas i source ustala serwer |
| GET /orders | list_orders | customer_id?, bake_id?, status?, limit, offset | 200 Page[OrderRead] | Łączy filtry przez AND |
| GET /orders/{order_id} | get_order | brak | 200 OrderRead | |
| PUT /orders/{order_id} | replace_order | OrderReplace | 200 OrderRead | Pełna wymiana, jedna transakcja; bez zmiany klienta i pieczenia |
| POST /orders/{order_id}/confirm | confirm_order | bez body | 200 OrderRead | Całość jest zatwierdzona; ponowne confirm niczego nie dolicza |
| POST /orders/{order_id}/cancel | cancel_order | bez body | 200 OrderRead | Zachowuje pozycje; ponowne cancel bez skutku |
| POST /orders/{order_id}/reopen | reopen_order | bez body | 200 OrderRead | Cancelled -> draft; tylko w otwartym oknie |

Nowy draft wymaga aktywnego klienta i otwartego okna. Istniejący draft zgłoszony przed granicą można rozstrzygnąć po jej upływie. Confirm anulowanego zamówienia wymaga najpierw reopen. PUT anulowanego zamówienia daje 409 ORDER_CANCELLED.

Przyjęte zamówienie można przed granicą zmienić przez PUT; pozostaje confirmed, a sumy wynikają z nowych pozycji. Po granicy PUT confirmed i cancel confirmed dają 409 ORDER_LOCKED. Draft otrzymany na czas można po granicy poprawić, przyjąć lub anulować. Ustawienia klienta nie usuwają istniejących przyjętych pozycji; reguły dodatków opisuje B04.

Kody konfliktów: INACTIVE_CUSTOMER, ORDER_ALREADY_EXISTS, ORDER_WINDOW_CLOSED, PRODUCT_NOT_OFFERED, EXTRA_ITEMS_NOT_ALLOWED, ORDER_CANCELLED, ORDER_LOCKED, INVALID_ORDER_STATE. Nieistniejący customer/bake/product oferty to 404; istniejąca pozycja oferty z innego pieczenia to 409 PRODUCT_NOT_OFFERED.

## M1: groups.py i aliases.py

| Operacja | Schema / odpowiedź | Reguły |
|---|---|---|
| POST /groups | GroupCreate -> 201 GroupRead | Unikalna nazwa po normalizacji |
| GET /groups | limit/offset -> 200 Page[GroupRead] | |
| GET /groups/{group_id} | 200 GroupRead | |
| PATCH /groups/{group_id} | GroupUpdate -> 200 GroupRead | |
| GET /groups/{group_id}/customers | limit/offset -> 200 Page[CustomerRead] | Lista członków, także nieaktywnych |
| PUT /groups/{group_id}/customers/{customer_id} | 204 | Idempotentne dodanie członkostwa |
| DELETE /groups/{group_id}/customers/{customer_id} | 204 | Idempotentne usunięcie, jeśli oba zasoby istnieją |
| GET /products/{product_id}/aliases | 200 list[AliasRead] | Łącznie z aliasem kanonicznym |
| POST /products/{product_id}/aliases | AliasCreate -> 201 AliasRead | 409 ALIAS_ALREADY_EXISTS, także dla tego samego produktu |
| DELETE /products/{product_id}/aliases/{alias_id} | 204 | 409 CANONICAL_ALIAS; obcy alias to 404 |

## M1: settings.py i messages.py

| Operacja | Schema / odpowiedź | Reguły |
|---|---|---|
| GET /settings | 200 SettingsRead | Singleton |
| PUT /settings/default-bake | DefaultBakeUpdate -> 200 SettingsRead | Jawne ustawienie lub null; bez wysyłki |
| POST /messages/simulate | SimulatedMessageCreate -> 201 MessageRead | Tylko środowisko dev/test; czas serwera; zapis i interpretacja bez przyjęcia |
| GET /messages | bake_id?, customer_id?, review_status?, limit/offset -> Page[MessageRead] | Pokazuje również nieprzypisane |
| GET /messages/{message_id} | 200 MessageRead | Oryginał i ostatnia interpretacja |
| POST /messages/{message_id}/assign | MessageAssign -> 200 MessageRead | Ręczne przypisanie; zakazane po applied |
| POST /messages/{message_id}/parse | bez body -> 200 MessageRead | Nowa interpretacja, bez zmiany przyjętego zamówienia |
| POST /messages/{message_id}/apply | MessageApply -> 200 OrderRead | Zapis potwierdzonego wyniku i oznaczenie applied w jednej transakcji |
| POST /messages/{message_id}/ignore | MessageIgnore -> 200 MessageRead | Powód obowiązkowy; applied nie da się po prostu zignorować |

Wiadomość od nieznanego telefonu nadal zostaje zapisana jako pending. Parsowanie nie tworzy klienta ani nie zgaduje powiązania. Powtórne apply już zastosowanej wiadomości zwraca powiązane zamówienie bez zmiany; odmienne żądanie wymaga nowej korekty, a nie ponownego zastosowania. Niezgodna expected_order_version daje 409 ORDER_VERSION_CONFLICT.

W tej wersji automatyczne przyjmowanie jest wyłączone. Pracownik może zatwierdzić wynik parsera lub podać poprawioną kompletną listę. Issue nie blokuje ręcznej decyzji samo w sobie, ale wszystkie twarde reguły oferty, uprawnień i czasu nadal obowiązują.

## M2: campaigns.py, webhooks.py, reports.py, amendments w orders.py

| Operacja | Wejście / odpowiedź | Reguły |
|---|---|---|
| PUT /bakes/{bake_id}/notification-settings | BakeNotificationUpdate -> BakeRead rozszerzony | Nie otwiera zapisów i nie wysyła |
| POST /bakes/{bake_id}/campaign-preview | CampaignRequest -> 200 CampaignPreview | Liczy aktywnych, sms_enabled, bez duplikatów; brak skutków zewnętrznych |
| POST /bakes/{bake_id}/campaigns | CampaignRequest -> 202 CampaignRead | Wymaga notify_enabled i otwartego pieczenia z przyszłym deadline; zapis odbiorców i zadań atomowo |
| GET /campaigns/{campaign_id} | 200 CampaignRead | Statystyki rzeczywistej wysyłki |
| POST /webhooks/sms/{provider}/incoming | format dostawcy -> jego poprawne potwierdzenie | Oddzielna autoryzacja; trwały zapis przed ACK; duplikat bez nowego skutku |
| POST /webhooks/sms/{provider}/status | format dostawcy -> jego potwierdzenie | Weryfikacja podpisu/sekretu; odporność na spóźnione statusy |
| POST /orders/{order_id}/amendments | OrderAmendmentCreate -> 201 OrderRead | Powód, wersja, audyt, pełna wymiana, zwiększenie data_version |
| POST /bakes/{bake_id}/reports | bez body -> 201 ReportRead | Po granicy lub ręcznym zamknięciu; nowa niezmienna rewizja PDF |
| GET /bakes/{bake_id}/reports | limit/offset -> Page[ReportRead] | Historyczne wersje |
| GET /reports/{report_id} | 200 ReportRead | Bieżące is_stale |
| POST /reports/{report_id}/finalize | bez body -> 200 ReportRead | 409 dla stale albo nierozstrzygniętych spraw; finalizacja pod blokadą |
| GET /reports/{report_id}/file | 200 application/pdf | Chroniony dostęp do pliku; brak publicznych trwałych URL |

M2 używa nagłówka `Idempotency-Key` dla tworzenia kampanii i korekt. Powtórzenie tego samego klucza i body zwraca pierwotny wynik; inny body z tym samym kluczem daje 409. Klucz, skrót żądania i wynik są zapisywane transakcyjnie w trwałym rejestrze, nie w pamięci procesu. Rejestr stanowi dodatkowy model M2 `IdempotencyRecord` (scope, key, request_hash, result JSON, created_at; UNIQUE(scope,key)).

Nowe spóźnione zamówienie w M2: pracownik zakłada je przez rozszerzone apply z jawnym trybem `accept_late`, powodem i audytem OrderAmendment; zwykły POST orders nie pozwala ominąć terminu. Dla tej operacji M2 rozszerza MessageApply o `accept_late: bool=false`; false zachowuje zachowanie M1. Zmiana istniejącego przyjętego zamówienia po granicy używa amendments.

Podgląd kampanii nie gwarantuje identycznego przyszłego zestawu odbiorców. Dopiero utworzenie kampanii utrwala listę. Wyłączenie ogłoszeń nie blokuje odbioru SMS-ów ani osobnego potwierdzenia zamówienia.

W M2 open planuje zadanie zamknięcia i pierwszego raportu na deadline. Close przed terminem przyspiesza ten proces. Pierwszy PDF powstaje automatycznie, także bez ogłoszenia SMS. POST reports służy do świadomego wygenerowania kolejnej rewizji. Klucz zadania pierwszego raportu jest unikalny dla pieczenia; powtórne wykonanie nie tworzy kolejnej pierwszej rewizji.

## Porządek implementacji routerów

Health -> customers -> products -> bakes -> orders -> groups/aliases -> settings/messages -> webhooks/campaigns/reports. Nie rejestruj pustych routerów przyszłych wydań. Literały, np. `/messages/simulate`, rejestruj przed pasującymi ścieżkami parametrycznymi.
