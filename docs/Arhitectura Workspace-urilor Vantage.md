Arhitectura Workspace-urilor Vantage
(v7)
Acest document descrie structura finală, decuplată, a proiectelor tale în Project IDX (Firebase
Studio). Vom folosi două workspace-uri separate, bazate pe tehnologii diferite.
Workspace 1: vantage-web (API-ul și Portalul)
Acesta este workspace-ul pe care l-ai creat deja [cite: image_2eece2.png].
● Sursă Git: https://github.com/[NUMELE-TAU]/adk-samples.git
● Scop: Construirea "Creierului" (api.vantage.app) și a "Feței" (proof.vantage.app).
● Filozofie: "Vibe Coding" – Ignorăm tot, cu excepția celor două foldere de care avem
nevoie.
<!-- end list -->
/ (Workspace-ul tău `adk-samples`)
│
├── go/ <-- IGNORĂM
├── java/ <-- IGNORĂM
│
├── python/
│ │
│ ├── agents/
│ │ │
│ │ ├── gemini-fullstack/
│ │ │ ├── app/ <-- IGNORĂM (Folosim backend-ul RAG)
│ │ │ └── frontend/ <-- AICI LUCRĂM (Frontend-ul
`proof.vantage.app`)
│ │ │ ├── src/
│ │ │ └── package.json
│ │ │
│ │ ├── RAG/ <-- AICI LUCRĂM (Backend-ul
`api.vantage.app`)
│ │ │ ├── app/
│ │ │ ├── rag/
│ │ │ └── pyproject.toml
│ │ │
│ │ ├── data-science/ <-- IGNORĂM (Planul v7 nu mai
"canibalizează")
│ │ └── ... (alte foldere) <-- IGNORĂM
│ │
│ └── ... (alte foldere)
│
└── ... (alte fișiere)
Workspace 2: vantage-mobile (Colectorul de Date)
Acesta este un workspace NOU pe care trebuie să îl creezi în Project IDX.
● Sursă Git: https://github.com/[NUMELE-TAU]/cahier.git (Trebuie să faci "Fork" la cahier
întâi!)
● Scop: Implementarea strategiei "Sidecar" MASTER27 [cite: MASTER27: VANTAGE
PROOF - Strategia Modulului "Sidecar" pentru Extracție de Date].
● Filozofie: "Sidecar" – Nu atingem app/, lucrăm doar în uploader/.
<!-- end list -->
/ (Workspace-ul tău `cahier`)
│
├── app/ <-- NU MODIFICĂM (Aplicația originală
`cahier`)
│ │
│ └── build.gradle <-- (Singura modificare este adăugarea
`implementation project(':uploader')`)
│
├── uploader/ <-- AICI LUCRĂM (Modulul nostru "Sidecar"
MASTER27)
│ │
│ ├── src/
│ │ └── main/java/com/vantage/uploader/
│ │ └── UploaderService.kt <-- (Aici scriem logica de
extracție și POST către `api.vantage.app`)
│ │
│ └── build.gradle
│
└── settings.gradle <-- (Aici ne asigurăm că `include ':app',
':uploader'`)
Cum se Conectează
1. Modulul uploader/ (din Workspace 2) rulează pe tabletele clienților.
2. El trimite date (ex: POST https://api.vantage.app/api/v1/ingest) către backend.
3. Acest backend este codul din python/agents/RAG/ (din Workspace 1), care rulează pe
Cloud Run.
4. Managerul deschide https://proof.vantage.app (din Workspace 1).
5. Frontend-ul (gemini-fullstack/frontend/) face apeluri (ex: GET
https://api.vantage.app/api/v1/query) către același backend RAG.