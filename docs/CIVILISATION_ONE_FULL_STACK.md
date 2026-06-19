# Civilisation One — Full-Stack Build Instruction

Version: `v0.1`
Status: implementation specification
Scope: MVP through production architecture

Civilisation One is an open scientific learning and collaboration ecosystem designed to help people learn, verify knowledge, conduct research, develop talent, and contribute ethically to humanity's understanding of life, consciousness, technology, and the universe.

## 1. Foundation principle

Knowledge must be open where possible, evidence must be traceable, participation must be voluntary, and every score or AI recommendation must remain explainable and contestable.

## 2. Product objectives

The platform must support:

- open scientific education;
- AI-assisted learning;
- collaborative research;
- ethical innovation;
- talent sponsorship;
- scientific simulations;
- collective knowledge verification;
- future-oriented space and consciousness research.

The system must clearly separate:

1. established knowledge;
2. active research;
3. competing interpretation;
4. speculative hypothesis;
5. independently submitted theory.

This separation protects scientific credibility while allowing unconventional ideas to be examined without falsely presenting them as verified science.

## 3. Recommended stack

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts
- React Flow or Cytoscape for knowledge graphs
- React Three Fiber for simulation and scientific visualisation

### Backend

- FastAPI
- Python 3.12+
- Pydantic
- SQLAlchemy
- Alembic migrations

### Data layer

- PostgreSQL
- pgvector for semantic search
- Redis for caching, queues, and realtime events
- S3-compatible object storage, with MinIO for local development

### AI layer

- Provider-neutral AI adapter
- Optional local Ollama adapter
- Retrieval-augmented generation pipeline
- Source and uncertainty enforcement
- AI output correction logging

### Realtime and jobs

- WebSockets or server-sent events for streaming
- Celery or RQ for jobs
- Redis pub/sub for event delivery
- Worker processes for simulations, indexing, reports, certificates, and moderation queues

### Deployment

- Docker Compose for local development
- Managed container hosting or Kubernetes for production
- CDN for static assets
- Default private services bound to internal networks only

## 4. User roles

| Role | Main capabilities |
|---|---|
| Visitor | Browse public content and public research summaries. |
| Learner | Enrol in courses, complete quizzes, use the AI tutor, track progress. |
| Researcher | Create projects, upload datasets/code, publish logs, request review. |
| Educator | Create courses, manage pathways, review student work. |
| Reviewer | Evaluate claims, methodology, evidence, and replication status. |
| Sponsor | Fund users/projects and monitor milestones/outcomes. |
| Admin | Manage users, moderation, review state, and platform operations. |
| Ethics/Data Officer | Review consent, sensitive data, safeguarding, and governance issues. |

## 5. Core modules

### 5.1 Learning Hub

Must include:

- course catalogue;
- lessons;
- quizzes;
- exercises;
- certificates;
- learning pathways;
- progress tracking;
- evidence-level labels;
- AI tutor integration.

Course object:

```json
{
  "id": "uuid",
  "title": "string",
  "discipline": "physics | biology | AI | mathematics | engineering | other",
  "level": "beginner | intermediate | advanced | research",
  "evidence_level": "established | active_research | competing_interpretation | speculative | independent_theory",
  "sources": [],
  "author_id": "uuid",
  "review_status": "draft | pending_review | reviewed | rejected | archived"
}
```

### 5.2 Research Collaboration Space

Must include:

- research project pages;
- team membership;
- hypotheses;
- methodology;
- assumptions;
- data/code links;
- evidence records;
- research logs;
- revision history;
- peer-review requests;
- replication status;
- preprint/report publishing.

Research project pages must show:

- hypothesis;
- methodology;
- assumptions;
- data sources;
- funding source;
- conflicts of interest;
- evidence level;
- review status;
- reproducibility status.

Project status values:

```text
draft
active
under_review
replication_requested
replicated
contested
rejected
archived
```

### 5.3 AI-Assisted Tutor

The AI tutor must:

- label AI-generated material;
- cite sources where available;
- state uncertainty;
- distinguish established science from hypothesis;
- support correction and reporting;
- avoid fabricating citations;
- avoid presenting speculation as fact.

AI answer schema:

```json
{
  "answer": "string",
  "classification": "established | active_research | speculative | unknown",
  "sources": [],
  "assumptions": [],
  "uncertainty": "low | medium | high",
  "needs_human_review": false
}
```

### 5.4 Virtual Laboratory

Simulation domains may include:

- quantum circuits;
- orbital mechanics;
- particle interactions;
- black-hole dynamics;
- neural networks;
- climate systems;
- biological populations;
- engineering models;
- statistical experiments.

Every simulation must distinguish between:

- physical measurement;
- mathematical approximation;
- synthetic output;
- speculative modelling.

Simulation result schema:

```json
{
  "simulation_id": "uuid",
  "model_name": "string",
  "input_parameters": {},
  "output_data_uri": "string",
  "classification": "toy_model | approximation | validated_model | speculative_model",
  "assumptions": [],
  "limitations": [],
  "created_at": "datetime"
}
```

### 5.5 Searchable Knowledge Database

Index:

- papers;
- courses;
- datasets;
- videos;
- articles;
- simulations;
- research organisations;
- funding opportunities;
- experiments.

Filters:

- discipline;
- date;
- evidence level;
- peer-review status;
- accessibility;
- replication status;
- language;
- difficulty level.

### 5.6 Talent Sponsorship

Must include:

- student sponsorship profiles;
- research funding pages;
- sponsor dashboard;
- milestone tracking;
- funding records;
- outcome reports;
- conflict-of-interest disclosure.

Rules:

- funding decisions must be auditable;
- milestones must be visible;
- sponsors must not be able to buy scientific authority;
- all conflicts of interest must be disclosed.

### 5.7 Civilisation 2 Profile

Dimensions:

- Knowledge;
- Verification;
- Learning;
- Collaboration;
- Creativity;
- Ethics;
- Wellbeing;
- Contribution.

Composite formula:

```text
C2 = wK*K + wV*V + wL*L + wC*C + wR*R + wE*E + wW*W + wI*I
```

Hard constraints:

- the score must be explainable;
- users must be able to view, challenge, correct, export, or delete profile data;
- the profile must not become a social-credit system;
- the profile must not measure human worth;
- the profile must not control access to fundamental services.

## 6. API structure

### Auth

```text
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
```

### Learning

```text
GET    /courses
POST   /courses
GET    /courses/{id}
PATCH  /courses/{id}
DELETE /courses/{id}
GET    /courses/{id}/lessons
POST   /courses/{id}/lessons
POST   /lessons/{id}/complete
```

### Research

```text
GET   /research/projects
POST  /research/projects
GET   /research/projects/{id}
PATCH /research/projects/{id}
POST  /research/projects/{id}/evidence
POST  /research/projects/{id}/review-request
```

### AI Tutor

```text
POST /ai/tutor
POST /ai/summarize
POST /ai/explain
POST /ai/quiz
POST /ai/source-check
```

### Simulations

```text
POST /simulations
GET  /simulations/{id}
POST /simulations/{id}/run
GET  /simulation-runs/{id}
WS   /simulation-runs/{id}/stream
```

### Sponsorship

```text
GET  /sponsorships
POST /sponsorships
GET  /sponsorships/{id}
POST /sponsorships/{id}/milestones
POST /sponsorships/{id}/report
```

### Civilisation Profile

```text
GET  /profile/me
GET  /profile/{user_id}
POST /profile/events
POST /profile/challenge
POST /profile/export
POST /profile/delete-request
```

### Audit

```text
GET  /audit/logs
GET  /audit/object/{type}/{id}
POST /audit/report
```

## 7. Database baseline

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  display_name TEXT,
  role TEXT NOT NULL DEFAULT 'learner',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE courses (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  discipline TEXT,
  level TEXT,
  evidence_level TEXT,
  author_id UUID REFERENCES users(id),
  review_status TEXT DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE lessons (
  id UUID PRIMARY KEY,
  course_id UUID REFERENCES courses(id),
  title TEXT NOT NULL,
  content_md TEXT,
  order_index INT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE research_projects (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  hypothesis TEXT,
  methodology TEXT,
  evidence_level TEXT,
  verification_status TEXT DEFAULT 'draft',
  owner_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE evidence_records (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES research_projects(id),
  claim TEXT NOT NULL,
  source_uri TEXT,
  evidence_type TEXT,
  evidence_strength TEXT,
  review_status TEXT DEFAULT 'unreviewed',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE simulations (
  id UUID PRIMARY KEY,
  owner_id UUID REFERENCES users(id),
  name TEXT NOT NULL,
  model_type TEXT,
  classification TEXT,
  assumptions JSONB,
  limitations JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sponsorships (
  id UUID PRIMARY KEY,
  sponsor_id UUID REFERENCES users(id),
  recipient_id UUID REFERENCES users(id),
  project_id UUID REFERENCES research_projects(id),
  amount NUMERIC,
  currency TEXT,
  status TEXT DEFAULT 'pending',
  disclosure TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  actor_id UUID REFERENCES users(id),
  action TEXT NOT NULL,
  target_type TEXT,
  target_id UUID,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## 8. Frontend routes

```text
/                         Landing page
/dashboard                Personal dashboard
/learn                    Course catalogue
/learn/[courseId]         Course detail
/learn/[courseId]/lesson/[lessonId]
/research                 Research catalogue
/research/[projectId]     Research workspace
/lab                      Virtual laboratory
/lab/[simulationId]       Simulation view
/ai-tutor                 AI tutor chat
/sponsorship              Sponsorship marketplace
/profile                  Civilisation 2 profile
/governance               Policies, review boards, appeals
/news                     Global science news
/admin                    Admin dashboard
```

## 9. Governance and safety requirements

Civilisation One must include governance for:

- scientific review;
- AI ethics;
- data protection;
- financial oversight;
- child safety;
- research integrity;
- appeals;
- dispute resolution;
- moderation.

Hard privacy requirements:

- participation in research must require informed consent;
- users must be able to withdraw;
- sensitive data must be minimised;
- wellbeing data must be voluntary;
- aggregate statistics should be preferred;
- children require special safeguards;
- medical and psychological claims require professional review;
- data retention must be documented;
- users must be able to export and delete their data where legally possible.

## 10. Token/economy constraints

At MVP stage, any token system must be internal and non-speculative.

Allowed early uses:

- daily participation unit;
- service access;
- research support;
- verified contribution reward;
- limited community voting;
- administration fee.

Forbidden without legal review:

- public trading;
- investment promises;
- financial return claims;
- speculative asset promotion;
- vote buying;
- purchased scientific authority;
- rewards for misinformation.

## 11. MVP scope

### Include

- user accounts;
- role-based access control;
- course catalogue;
- basic lesson pages;
- AI tutor chat with source/certainty labels;
- research project pages;
- evidence classification badges;
- user profile;
- basic Civilisation 2 dimensions;
- audit logs;
- admin moderation dashboard;
- privacy and consent flows.

### Exclude

- tradeable token;
- formal accreditation claims;
- sensitive wellbeing tracking;
- children's research studies;
- medical/psychological analysis;
- Quantum ID branding unless real quantum-secure technology is used;
- complex financial marketplace.

## 12. Development phases

1. Foundation: auth, roles, PostgreSQL schema, core UI, courses, projects, audit log, admin.
2. AI Tutor: AI adapter, RAG, citations, uncertainty labels, correction logs.
3. Research Tools: evidence records, logs, uploads, review requests, replication status.
4. Virtual Lab: simulation runner, realtime updates, result classification, export reports.
5. Sponsorship: sponsor dashboard, milestones, funding records, outcome reports.
6. Governance: review boards, appeals, policy versioning, data protection controls, transparency reports.

## 13. Non-negotiable implementation rules

- Essential knowledge should remain freely accessible.
- AI-generated material must be labelled and source-linked where possible.
- Scientific claims must be classified by evidence status.
- Scores must be explainable and contestable.
- The Civilisation 2 profile must not become a social-credit system.
- Do not implement tradeable financial assets at MVP stage.
- Do not claim accreditation unless legally approved.
- Do not collect sensitive wellbeing, health, biometric, location, or psychological data without explicit consent and governance review.
- Every important object must have audit history.
