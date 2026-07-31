# Gesneu API - Project Context & Rules

## Framework & Architecture
- Framework: Next.js 15 (App Router) + Prisma ORM + PostgreSQL (Supabase)
- Architecture: Screaming Architecture + Clean/Hexagonal principles (Services, Repositories, Handlers, EventBus Observers)
- Testing: Jest Integration Suites (156 tests passing) + Playwright E2E

## gstack Skills

Use the `/browse` skill from `gstack` for all web browsing (never use `mcp__claude-in-chrome__*` tools).

Available gstack skills:
- `/office-hours`: Product interrogation and reframing
- `/plan-ceo-review`: Strategic scope challenge (Expansion, Hold, Reduction)
- `/plan-eng-review`: Technical architecture, data flow, edge cases, test matrix
- `/plan-design-review`: Senior design audit & UI slop detection
- `/plan-devex-review`: DX friction audit & TTHW benchmark
- `/design-consultation`: Design system builder
- `/design-shotgun`: AI mockup variants comparison
- `/design-html`: Production HTML/CSS generator
- `/review`: Staff engineer bug & race condition detector
- `/cso`: Chief Security Officer audit (OWASP Top 10 + STRIDE threat model)
- `/qa`: Automated QA with real browser & regression test generation
- `/qa-only`: Pure bug reporter without code edits
- `/ship`: Run tests, audit coverage, sync main, open PR
- `/land-and-deploy`: Merge PR, wait for CI/deploy, verify production health
- `/canary`: Post-deploy monitoring loop
- `/benchmark`: Performance engineering & Core Web Vitals
- `/browse`: Headless/Headed Chromium browser automation
- `/connect-chrome`: Remote Chrome attachment
- `/setup-browser-cookies`: Import browser cookies for authenticated QA
- `/setup-deploy`: Deploy pipeline configurator
- `/setup-gbrain`: Persistent knowledge base onboarding
- `/retro`: Weekly team retro & shipping analytics
- `/investigate`: Root cause debugging workflow
- `/document-release`: Release doc updater (Diataxis framework)
- `/document-generate`: Documentation authoring
- `/codex`: Second opinion review via OpenAI Codex CLI
- `/autoplan`: Automatic multi-review planning pipeline
- `/careful`: Destructive command safety guardrails
- `/freeze`: Directory edit lock
- `/guard`: Full safety (/careful + /freeze)
- `/unfreeze`: Unlock directory edit lock
- `/gstack-upgrade`: Self-updater
- `/learn`: Cross-session memory & learnings manager
