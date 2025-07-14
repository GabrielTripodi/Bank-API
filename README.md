# API RESTful bancaria

**Lingue disponibili / Available languages**: [IT](README.md) | [EN](README-en.md)

Questo repository contiene il codice sorgente dell'**API RESTful bancaria**, sviluppata in Flask. Questa API funge da backend per l'estensione per Thunderbird [**IBAN Guard**](https://github.com/GabrielTripodi/IBAN-Guard).

Il progetto è stato realizzato come parte di una tesi per il corso di laurea magistrale in Artificial Intelligence and Computer Science presso l'Università della Calabria. L'API simula un servizio bancario reale in grado di verificare la titolarità di un codice IBAN, un componente fondamentale per la prevenzione di truffe legate agli attacchi di tipo Business Email Compromise (BEC).

---

## 🛡️ Obiettivo

Simulare un servizio, messo a disposizione da un istituto bancario nazionale, capace di verificare se un codice IBAN, trovato in un’email o in un suo allegato, appartiene realmente al mittente del messaggio. Lo scopo è prevenire frodi in cui l’IBAN viene manipolato da un attaccante.

---

## 🏗️ Architettura

L'API è stata progettata per essere leggera, sicura e scalabile, seguendo i principi dell'architettura REST.

* **Backend:** [Flask](https://flask.palletsprojects.com/) (Python)
* **Database:** [SQLite](https://www.sqlite.org/index.html) (un database relazionale serverless basato su file)
* **Interfaccia amministrativa:** Web app Flask + HTML/CSS/JS (Bootstrap, SweetAlert2)
* **Librerie principali**:
    * `Flask-Cors`: Per la gestione delle policy Cross-Origin Resource Sharing (CORS).
    * `rapidfuzz`: Per implementare il confronto "fuzzy matching" tra stringhe, utilizzato per la verifica degli IBAN intestati a un'azienda.
    * `bcrypt`: Per l'hashing sicuro delle password degli amministratori.
    * `Rich`: Per migliorare l'interfaccia a riga di comando dello script di inizializzazione.

---

## 📦 Funzionalità

* **Verifica IBAN Intelligente**: L'API è in grado di gestire la verifica sia per **persone fisiche** che per **aziende**. Per le aziende, utilizza un algoritmo di *fuzzy matching* per tollerare piccole variazioni nei nomi (es. "CyberSonic" vs "CyberSonic S.r.l.").
* **Interfaccia Amministrativa Web**: È inclusa una semplice ma funzionale interfaccia web ("IBAN Admin Manager") riservata agli amministratori per gestire le operazioni CRUD (Create, Read, Update, Delete) sulla tabella degli effettivi intestatari degli IBAN.
* **Sicurezza Robusta**: Sono state implementate molteplici misure di sicurezza per proteggere l'API e i dati che gestisce.
* **Struttura Modulare**: Il codice è organizzato in moduli con responsabilità specifiche (`app.py`, `utils.py`, `db_utils.py`, etc.) per favorire la manutenibilità e la leggibilità.
* **Versioning degli Endpoint**: Tutti gli endpoint sono prefissati con `/api/v1/` per garantire la retrocompatibilità in caso di futuri aggiornamenti.

---

## 🗃️ Struttura del Database

### `iban_holders`
| Campo         | Tipo        | Descrizione                          |
|--------------|-------------|--------------------------------------|
| `id`         | CHAR(36)      | Identificatore univoco di tipo UUID v4 |
| `iban`       | CHAR(27)        | Codice IBAN (27 caratteri) |
| `first_name` | VARCHAR(40) (optional) | Nome intestatario (persona fisica)   |
| `last_name`  | VARCHAR(50) (optional) | Cognome intestatario (persona fisica) |
| `company_name` | VARCHAR(80) (optional) | Ragione sociale azienda |
| `created_at` | TIMESTAMP    | Data e ora creazione record |
| `updated_at` | TIMESTAMP    | Data e ora ultima modifica |

### `administrators`
| Campo         | Tipo        | Descrizione                          |
|--------------|-------------|--------------------------------------|
| `id`         | CHAR(36)    | Identificatore univoco di tipo UUID v4 |
| `username`   | VARCHAR(50) | Nome utente di un amministratore     |
| `password`   | CHAR(60)    | Hash della password generato con Bcrypt       |

---

## 📡 Endpoint dell'API

L'API espone i seguenti endpoint principali.

### Endpoint Pubblici (per l'estensione IBAN Guard)

Questi endpoint sono protetti da una policy CORS restrittiva che consente richieste solo dall'origine dell'estensione Thunderbird.

* `POST /api/v1/sender-iban-verification`
    * **Scopo**: Verifica automatica dell'IBAN rispetto al nome del mittente di un'email.
    * **Corpo richiesta**: `{"sender": "Nome Mittente", "iban": "IT..."}`
    * **Risposte**:
        * `200 OK`: Se la verifica ha successo (positiva o negativa).
        * `400 Bad Request`: Dati di input non validi.
        * `404 Not Found`: L'IBAN non è presente nel database.
        * `500 Internal Server Error`: Errore del server.

* `POST /api/v1/iban-verification`
    * **Scopo**: Verifica manuale di un IBAN inserito dall'utente.
    * **Corpo richiesta (Persona Fisica)**: `{"name": "Nome", "surname": "cognome", "iban": "IT..."}`
    * **Corpo richiesta (Azienda)**: `{"name": "Nome Azienda Srl", "iban": "IT..."}`
    * **Risposte**: Uguali all'endpoint precedente.

### Endpoint Amministrativi (protetti da autenticazione)

Questi endpoint sono utilizzati dall'interfaccia amministrativa per le operazioni CRUD e richiedono una sessione autenticata.

* `GET /api/v1/ibans`: Recupera l'elenco di tutti gli IBAN e i relativi intestatari.
* `POST /api/v1/ibans`: Aggiunge un nuovo IBAN e il suo intestatario.
* `PUT /api/v1/ibans/<uuid:iban_id>`: Modifica un IBAN e/o un intestatario esistente.
* `DELETE /api/v1/ibans/<uuid:iban_id>`: Elimina un IBAN dal database.

---

## 🛠️ Interfaccia Amministrativa

Per gestire i dati nel database, è possibile accedere all'interfaccia web di amministrazione.

1.  Apri il browser e naviga verso l'URL di login. Per motivi di sicurezza, l'URL non è standard ma è stato reso volutamente difficile da indovinare:
    `http://127.0.0.1:5000/admin-HaZiNgTLamSe`
2.  Effettua il login con le credenziali dell'amministratore create durante la fase di inizializzazione.
3.  Dalla dashboard, potrai aggiungere, modificare o rimuovere record di IBAN e dei loro intestatari.

---

## 🔐 Misure di Sicurezza

Le principali misure implementate includono:

* **Validazione Rigorosa degli Input**: Tutti i dati ricevuti dagli endpoint vengono validati tramite espressioni regolari per prevenire dati malformati.
* **Protezione da SQL Injection**: L'interazione con il database avviene esclusivamente tramite query parametrizzate .
* **Cross-Origin Resource Sharing (CORS)**: Meccanismo di sicurezza che accetta richieste solo da origini esplicitamente autorizzate (come l’estensione per Thunderbird), prevenendo accessi indesiderati da domini esterni.
* **Content Security Policy (CSP)**: Configurazione restrittiva che limita le fonti di contenuti attivi (script, stili, immagini, ecc.) per prevenire attacchi XSS e altri tipi di minacce.
* **Autenticazione Sicura**: La sessione amministrativa è protetta da cookie firmati crittograficamente con flag `HttpOnly`, `Secure` e `SameSite="Lax"` per prevenire manomissioni e attacchi CSRF.
* **Password Hashing**: Le password degli amministratori sono salvate nel database utilizzando l'algoritmo Bcrypt.
* **Header di sicurezza HTTP**: L'API e l'interfaccia ammninistrativa includono header come `Strict-Transport-Security`, `X-Frame-Options` e `X-Content-Type-Options` per rafforzare la sicurezza lato client.

---

## 🚀 Guida all'installazione

Segui questi passaggi per configurare ed eseguire l'API in un ambiente di sviluppo locale.

### Prerequisiti

* Python 3.x
* `pip` (il package manager di Python)

### Installazione e Configurazione

1.  **Clona il repository**:
    ```bash
    git clone [https://github.com/GabrielTripodi/Bank-API.git](https://github.com/GabrielTripodi/Banking-API.git)
    cd Banking-API
    ```

2.  **Crea e attiva un ambiente virtuale** (consigliato):
    ```bash
    # Per macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Per Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Installa le dipendenze**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inizializza il database simulato**:
    Esegui lo script di inizializzazione. Questo comando creerà il file del database `BankDatabase.db`, popolerà la tabella `iban_holders` con dati di esempio e ti chiederà di **creare le credenziali per il primo utente amministratore**.
    ```bash
    python initialize_database.py
    ```
    Conserva le credenziali che hai creato, ti serviranno per accedere all'interfaccia amministrativa.

5.  **Avvia il server Flask**:
    ```bash
    python app.py
    ```
    L'API sarà ora in esecuzione e accessibile all'indirizzo `http://localhost:5000`.

---

> ⚠️ Nota: questo progetto è stato realizzato a scopo accademico. L’API bancaria simulata non ha valore legale né accesso a dati reali.
