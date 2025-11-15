Plan de Arhitectură și Strategie:
Platforma "Physical AI" (v7 - Hibrid)
Referințe: Strategia "Hibrid RAG/Fullstack", MASTER27 [cite: MASTER27: VANTAGE PROOF
- Strategia Modulului "Sidecar" pentru Extracție de Date], gemini-fullstack [cite:
adk_gemini_fullstack.gif], Agentul RAG
Acest document definește arhitectura tehnică decuplată și strategia de dezvoltare "efort minim",
optimizată pentru colectarea datelor de fine-tuning printr-un sistem RAG gata făcut.
1. Arhitectura Ecosistemului (Separarea Domeniilor
v7)
Componentă Domeniu (Exemplu) Tehnologie Sursă (din
adk-samples)
Rol în Ecosistem
Colectorul Mobil Cahier (Aplicație
Android)
cahier (Sursă Externă) Colectare: Interfața
gratuită (nemodificată)
de pe teren.
Extractorul de Date uploader (Modul
Gradle)
Cod Propriu
(MASTER27)
Extracție: Modulul
"Sidecar" [cite:
MASTER27: VANTAGE
PROOF - Strategia
Modulului "Sidecar"
pentru Extracție de
Date]. Trimite datele
haotice către
api.vantage.app.
Baza de Date (Seif) Google Cloud (N/A) Stocare Lung Termen:
Firestore/BigQuery
pentru datele de
antrenament (Faza
3/4).
Baza de Date
(Memorie)
Google Cloud (N/A) - Definită de
Agentul RAG
Memoria AI (RAG):
Baza de date vectorială
(ex: Vertex AI Vector
Search) pe care o
folosește agentul RAG.
Portalul Public vantage.app WordPress Marketing & Demo:
Site-ul public. Apelează
API-ul demo.
Portalul "Evoluție" proof.vantage.app gemini-fullstack/front
end/
Produsul Faza 2:
Portalul de chat [cite:
adk_gemini_fullstack.gi
f] (cu Auth) care Componentă Domeniu (Exemplu) Tehnologie Sursă (din
adk-samples)
Rol în Ecosistem
interoghează
backend-ul RAG.
Motorul AI (API) api.vantage.app RAG/ (Agentul RAG pe
care l-ai găsit)
Inteligența (RAG):
Backend-ul "Physical
AI". Găzduiește API-ul
de ingestie și
interogare.
Portalul Premium app.vantage.app (Rezervat) Produsul Faza 3: Va
găzdui "Agentul Client"
(fine-tuned).
2. Strategia de Dezvoltare (Cum Construim - "Hibrid")
A. Pentru Cahier (Colectorul): Strategia "Sidecar" (MASTER27)
● Obiectiv: Izolare totală [cite: MASTER27: VANTAGE PROOF - Strategia Modulului
"Sidecar" pentru Extracție de Date]. Nu se modifică codul cahier/app/.
● Acțiune: Creăm doar modulul uploader/ care citește baza de date locală cahier și trimite
datele nestructurate (notițe, desene) așa cum sunt, către noul API de ingestie.
B. Pentru Ecosistemul Web: Strategia "Hibrid Fork and Merge"
● Obiectiv: A folosi cele mai bune piese din adk-samples cu modificări minime.
● Acțiune:
1. Fork & Clone: Facem "Fork" la adk-samples și îl clonăm în Project IDX.
2. Backend (api.vantage.app): Vom folosi folderul python/agents/RAG/ ca fundație.
Ne vom concentra pe configurarea .env-ului său și pe securizarea endpoint-urilor
sale de ingest (pentru uploader) și query (pentru proof.vantage.app). Efortul de
codare logică AI este zero.
3. Frontend (proof.vantage.app): Vom folosi folderul
python/agents/gemini-fullstack/frontend/ ca fundație. Vom adăuga Firebase
Authentication și vom face o singură modificare majoră: vom schimba URL-ul
API-ului pe care îl apelează, pentru a-l direcționa către API-ul RAG (ex:
https://api.vantage.app/api/v1/query).
C. Pentru Motorul AI (Uneltele): Strategia "Folosește, nu Construi"
● Obiectiv: Efort minim real.
● Acțiune: Nu mai "canibalizăm" data-science-agent. Nu mai construim noi unelte RAG.
Folosim agentul RAG gata făcut, care are deja uneltele de căutare vectorială încorporate.