Ghid de Configurare: "Seiful" și
"Memoria" AI (Planul de Bătălie v7)
Obiectiv: Configurarea resurselor de stocare din Google Cloud necesare pentru Faza 2
(Portalul RAG) și Faza 3/4 (Fine-Tuning).
Partea 1: Configurarea "Seifului" (Firestore) - Efort
Minim
Acesta este "Seiful" pe termen lung pentru datele de antrenament (Faza 3/4). Vom folosi
Firestore pentru că se aliniază perfect cu strategia "vibe coding" (efort minim, fără schemă) și
este ideal pentru a stoca documente JSON haotice trimise de uploader (MASTER27) [cite:
MASTER27: VANTAGE PROOF - Strategia Modulului "Sidecar" pentru Extracție de Date].
1. Navighează la Firestore:
○ În Consola Google Cloud, asigură-te că ești în proiectul corect (ex:
vantage-proof-prod).
○ În bara de căutare de sus, scrie "Firestore" și selectează-l.
2. Selectează Modul Nativ:
○ Firestore îți va oferi două opțiuni: "Native Mode" sau "Datastore Mode".
○ Alege "Native Mode". Acesta este cel pe care îl așteaptă clienții mobili și API-urile
moderne.
○ [Imagine a selecției modului Firestore (Native vs. Datastore)]
3. Alege Locația:
○ Selectează o locație pentru baza de date (ex: eur3 (Frankfurt) sau us-central).
○ Important: Odată aleasă, locația nu mai poate fi schimbată.
○ Apasă "CREATE DATABASE".
4. Setează Regulile de Securitate (Inițial):
○ Navighează la tab-ul "Rules" (Reguli) din consola Firestore.
○ Pentru început (în modul de dezvoltare), poți seta regulile să permită scrierea doar
pentru contul tău de serviciu (cahier-uploader-sa) și citirea doar pentru utilizatorii
autentificați (proof.vantages.app).
○ Exemplu de regulă de start:
<!-- end list -->rules_version = '2';
service cloud.firestore {
match /databases/{database}/documents {
// Permite "uploader"-ului (robot) să scrie orice în
colecția clientului
match /{clientId}/{document=**} {
allow write: if request.auth.token.email ==
"cahier-uploader-sa@[...].iam.gserviceaccount.com";
// Permite portalului (utilizator uman logat) să
citească doar din colecția sa
allow read: if request.auth != null &&
request.auth.token.client_id == clientId;
}
}
}
○ Apasă "Publish".
Rezultat: "Seiful" este gata. Este un depozit NoSQL scalabil, gata să primească datele haotice
(nestructurate) de la uploader (MASTER27).
Partea 2: Configurarea "Memoriei" (Vertex AI Vector
Search) - RAG
Acesta este "creierul" (memoria de lucru) pentru agentul RAG din Faza 2 (proof.vantages.app).
Este o componentă mai complexă, dar esențială. Agentul RAG pe care l-ai găsit [cite:
python/agents/RAG] se va baza pe existența acesteia.
1. Navighează la Vertex AI Vector Search:
○ În Consola Google Cloud, scrie în bara de căutare "Vertex AI Search and
Conversation".
○ În meniul din stânga, găsește secțiunea "Vector Search" (s-ar putea să fie sub
"Managementul Datelor" sau un nume similar).
2. Creează un Index Vectorial:
○ Apasă pe "CREATE INDEX".
○ Nume: Dă-i un nume clar (ex: vantage-rag-memory-index).
○ Regiune: Alege aceeași regiune ca și restul resurselor (ex: us-central1).
○ Dimensiuni (CRITIC): Aceasta este cea mai importantă setare. Trebuie să se
potrivească cu modelul de "embedding" pe care îl va folosi agentul RAG. Un
standard foarte comun (folosit de modelul textembedding-gecko de la Google) este
768. Verifică documentația agentului RAG, dar 768 este o presupunere sigură.
○ Tipul Indexului (Algoritm): Lasă algoritmul "Tree-AH" sau "Brute Force" (dacă e
pentru testare). "Tree-AH" este un echilibru bun.
○ Măsurarea Distanței: Alege "Cosine" (de obicei cea mai bună pentru similaritatea
textului) sau "Dot Product".
○ Actualizare: Alege "Streaming Update" (Actualizare în Timp Real). Asta permite
agentului să "se deștepte pe parcurs" imediat ce uploader-ul trimite date noi.
○ Apasă "CREATE".
○ [Imagine a formularului "Create Index" din Vertex AI Vector Search]
3. Creează un Punct Final (Index Endpoint):
○ Un index este doar "fișierul". Ai nevoie de un "server" (endpoint) care să îl
deservească.
○ Navighează la tab-ul "INDEX ENDPOINTS".
○ Apasă "CREATE INDEX ENDPOINT".
○ Nume: Dă-i un nume (ex: vantage-rag-endpoint).
○ Regiune: Aceeași regiune.
○ Acces: Selectează "Standard" (Public Endpoint). Nu-ți face griji, accesul va fi
securizat prin permisiunile IAM, nu va fi cu adevărat "public".
○ Apasă "CREATE".
4. Publică (Deploy) Indexul pe Punctul Final:
○ Așteaptă ca endpoint-ul să fie creat (poate dura câteva minute).
○ Odată creat, dă click pe numele lui (vantage-rag-endpoint).
○ Vei vedea o secțiune "Deployed indexes". Apasă "DEPLOY INDEX".
○ Index: Selectează indexul pe care l-ai creat la Pasul 2
(vantage-rag-memory-index).
○ Nume de Afișare: Dă-i un nume (ex: v7_rag_index_live).
○ Scalare: Setează "Numărul minim de replici" la 1.
○ Apasă "DEPLOY".
○ NOTĂ: Acest pas (publicarea) poate dura 30-60 de minute. Trebuie să ai răbdare.
Rezultat: "Memoria" este gata. Ai acum un API de căutare vectorială complet funcțional. Va
trebui să notezi ID-ul Punctului Final (Endpoint ID) și ID-ul Indexului Publicat (Deployed
Index ID). Acestea vor fi variabilele de mediu pe care le vei introduce în fișierul .env al agentului
tău RAG (din python/agents/RAG/) în Faza 2 a planului de bătălie.