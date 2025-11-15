# MASTER27: VANTAGE PROOF - Strategia Modulului "Sidecar" pentru Extracție de Date
**Status:** **FINAL ȘI APROBAT.** Acest document anulează și înlocuiește toate planurile
anterioare.
**Principiu Director:** Implementarea unui sistem de extracție a datelor complet izolat de codul
sursă al aplicației `cahier`, permițând actualizări facile din repository-ul Git original, cu un efort
de mentenanță minim spre zero.
---
## 1. Viziunea Strategică: Un Parazit Simbiotic
Considerăm funcționalitatea noastră de extracție ca un "simbiot": un modul independent care
trăiește în interiorul aplicației gazdă (`cahier`), se "hrănește" cu datele din baza sa de date, dar
nu modifică și nu afectează în niciun fel funcționarea normală a acesteia.
* **Aplicația Gazdă (`cahier`):** Rămâne neschimbată și poate fi actualizată oricând cu `git
pull` din sursa originală.
* **Modulul Simbiot (`uploader`):** Conține 100% din logica noastră de extracție, transformare
și încărcare. Este singurul loc unde vom scrie cod nou.
---
## 2. Arhitectura Tehnică: Izolare prin Module Gradle
Proiectul va avea următoarea structură de directoare, cu responsabilități clar separate:
vantage-proof/ (Proiectul Rădăcină)
├── app/ (Modulul original din cahier. NU ÎL MODIFICĂM, cu excepția build.gradle)
└── uploader/ (NOUL NOSTRU MODUL. Aici vom lucra exclusiv.)
| Componenta | Rol Operațional | Locație | Mentenanță |
| :--- | :--- | :--- | :--- |
| **Vantage Proof (Core App)** | Aplicația `cahier` originală, cu care interacționează utilizatorul. |
`vantage-proof/app/` | Se poate actualiza cu `git pull`. Riscul de conflict este minim. |
| **Vantage Sidecar** | Modulul nostru care extrage, transformă și încarcă datele în fundal. |
`vantage-proof/uploader/` | 100% codul nostru. Nu este afectat de actualizările modulului `:app`.
|
---
## 3. Plan de Implementare Detaliat
### **Faza 0: Setup-ul Proiectului Modular**
* **Obiectiv:** Pregătirea structurii de proiect care permite izolarea completă a codului nostru.
* **Acțiuni:**
1. **Clonarea Proiectului:** Se clonează repository-ul `cahier` într-un folder nou,
`vantage-proof`.
2. **Crearea Modulului `uploader`:**
* În Android Studio, se accesează `File -> New -> New Module...`.
* Se selectează "Android Library".
* **Module name:** `uploader`
* **Package name:** `com.vantage.uploader`
3. **Conectarea Modulelor:**
* În fișierul `settings.gradle` (la rădăcina proiectului), se asigură că ambele module sunt
incluse: `include ':app', ':uploader'`.
* În fișierul `build.gradle` al modulului `:app` (cel din `cahier`), se adaugă o singură linie în
secțiunea `dependencies` pentru a-l face conștient de existența "simbiotului":
* **Obiectiv:** Pregătirea structurii de proiect care permite izolarea completă a codului nostru.
* **Acțiuni:**
1. **Clonarea Proiectului:** Se clonează repository-ul `cahier` într-un folder nou,
`vantage-proof`.
2. **Crearea Modulului `uploader`:**
* În Android Studio, se accesează `File -> New -> New Module...`.
* Se selectează "Android Library".
* **Module name:** `uploader`
* **Package name:** `com.vantage.uploader`
3. **Conectarea Modulelor:**
* În fișierul `settings.gradle` (la rădăcina proiectului), se asigură că ambele module sunt
incluse: `include ':app', ':uploader'`.
* În fișierul `build.gradle` al modulului `:app` (cel din `cahier`), se adaugă o singură linie în
secțiunea `dependencies` pentru a-l face conștient de existența "simbiotului":