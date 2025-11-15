Planul de Bătălie (v7): Implementarea
Hibridă RAG-Fullstack
Referințe: Strategia "Hibrid RAG/Fullstack", MASTER27 [cite: MASTER27: VANTAGE PROOF
- Strategia Modulului "Sidecar" pentru Extracție de Date], gemini-fullstack [cite:
adk_gemini_fullstack.gif], Agentul RAG
Obiectiv: Lansarea rapidă a portalului proof.vantage.app (Faza 2) prin combinarea
backend-ului RAG (pentru API) cu frontend-ul gemini-fullstack (pentru UI), cu efort minim de
programare.
Faza 0: Fundația (Google Cloud & Firebase)
1. Creează Proiectul Google Cloud: (ex: vantage-proof-prod).
2. Conectează Firebase: Adaugă proiectul în Consola Firebase.
3. Activează API-urile Esențiale:
○ Vertex AI API
○ Cloud Storage API
○ Cloud Run API
○ IAM API
○ Cloud Build API
○ Firestore API (pentru "Seiful" de Faza 3)
○ Vertex AI Vector Search API (sau orice alt API de Vector DB pe care îl necesită
agentul RAG).
4. Setează Permisiunile (IAM):
○ Adaugă rolurile necesare contului tău (Vertex AI User, Storage Admin, Cloud Run
Admin, Firebase Admin).
○ (Securitate uploader): Creează un Service Account (ex: cahier-uploader-sa)
pentru scriptul uploader MASTER27 [cite: MASTER27: VANTAGE PROOF -
Strategia Modulului "Sidecar" pentru Extracție de Date]. Acordă-i rolurile necesare
(ex: Cloud Run Invoker pentru API-ul de ingestie).
5. Creează Resursele de Stocare și Memorie:
○ Firestore/BigQuery: Configurează "Seiful" pe termen lung (Faza 3).
○ Vector Search: Configurează un Index Vectorial în Vertex AI, conform specificațiilor
agentului RAG.
○ Alerte de Buget: Setează alerte de buget pentru a monitoriza costurile Vertex AI
(Search + Gemini) și Cloud Run.
6. Setează Firebase Authentication: Activează metoda de login (ex: Email/Parolă) pentru
proof.vantage.app.
Faza 1: Mediul de Lucru (Project IDX)
1. Fork Repository-ul: Mergi pe https://github.com/google/adk-samples și apasă "Fork" în
contul tău de GitHub.
2. Creează Mediul IDX: În idx.google.com, creează un mediu nou din "From GitHub" folosind URL-ul fork-ului tău.
Faza 2: Construcția Backend-ului (api.vantage.app) -
Bazat pe RAG
Folosind folderul python/agents/RAG/ din fork-ul tău.
1. Navighează și Autentifică:
○ Într-un Terminal (Backend): cd python/agents/RAG
○ Autentifică mediul: gcloud auth application-default login și gcloud auth
application-default set-quota-project [Project ID].
2. Instalează și Configurează:
○ Rulează make install (sau echivalentul din README.md-ul agentului RAG).
○ Configurează fișierul .env al agentului RAG cu ID-ul Proiectului, ID-ul Indexului
Vectorial, etc.
3. Definește API-ul (Configurare, nu Cod):
○ Endpoint Ingestie Date: Găsește endpoint-ul de ingest sau upload al agentului
RAG.
■ Securizează-l pentru a valida Cheia API de Serviciu (din Faza 0) trimisă de
uploader.
■ Logica (Dublă Salvare): Modifică minim acest endpoint pentru ca, pe lângă
adăugarea în Vector DB, să salveze datele brute și în Firestore/BigQuery
(pentru "Seiful" de Faza 3).
○ Endpoint Interogare (Query): Găsește endpoint-ul de query sau chat al agentului
RAG.
■ Securizează-l pentru a valida Token-ul JWT Firebase (acesta va fi apelat de
proof.vantage.app).
4. Testează: Pornește serverul backend RAG (ex: make run-backend).
Faza 3: Construcția Portalului "Evoluție"
(proof.vantage.app)
Folosind folderul python/agents/gemini-fullstack/frontend/.
1. Navighează și Instalează Firebase:
○ Într-un al doilea Terminal (Frontend): cd python/agents/gemini-fullstack/frontend
○ Rulează: npm install firebase firebaseui.
2. Configurează Firebase:
○ Creează frontend/src/firebaseConfig.ts cu cheile de configurare.
3. Implementează Autentificarea:
○ Modifică frontend/src/App.tsx pentru a implementa Firebase Authentication.
Utilizatorii trebuie să se logheze pentru a vedea interfața de chat [cite:
adk_gemini_fullstack.gif].
4. Sarcina Cheie (Efortul Minim de Programare):
○ Găsește fișierul în care gemini-fullstack/frontend/ își definește endpoint-ul API (ex:
frontend/src/api/chatApi.ts sau similar).
○ Schimbă URL-ul de bază. În loc să apeleze '/api/chat' (backend-ul local), trebuie să
apeleze URL-ul complet al backend-ului RAG: <!-- end list -->// Exemplu de modificare în
frontend/src/api/chatApi.ts
// LINIA VECHE:
// const API_BASE_URL = '/api';
// LINIA NOUĂ:
const API_BASE_URL =
'[https://api.vantage.app](https://api.vantage.app)'; //
URL-ul backend-ului RAG
// ... restul codului care construiește cererea (ex:
/v1/query)
○ Asigură-te că trimiți și Token-ul JWT de la Firebase în header-ul Authorization la
fiecare cerere.
5. Testează Local: Pornește frontend-ul cu npm run dev. Acum ar trebui să vorbească cu
backend-ul RAG care rulează în celălalt terminal.
Faza 4 & 5: Site-ul Public și Deployment
Rămân identice cu planul v6.
1. Site-ul Public (vantage.app): Construit pe WordPress.
2. Deployment Backend (api.vantage.app):
○ Publică backend-ul RAG/ pe Cloud Run.
○ Aplică Cloud Armor cu Rate Limiting pe endpoint-ul demo (dacă este cazul).
3. Deployment Frontend (proof.vantage.app):
○ Publică frontend-ul gemini-fullstack/frontend/ pe Firebase Hosting.,