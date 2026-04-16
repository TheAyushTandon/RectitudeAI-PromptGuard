# 🔐 Rectitude.AI — Frontend Implementation Master Plan
> Version 1.0 | Full-Stack UI/UX Blueprint for Faculty Showcase
> Author: Senior UI Architect Review | Status: APPROVED FOR BUILD

---

## 📐 Design System Foundation

### Visual Identity (Inspired by eragon.ai)
- **Primary Palette:**
  - Background: `#060010` (near-black deep purple-black)
  - Surface: `#0D0019`
  - Accent Purple: `#7B3FE4`
  - Accent Glow: `#A855F7`
  - Text Primary: `#F0EBF8`
  - Text Secondary: `#8B7AA0`
  - Border/Subtle: `rgba(123, 63, 228, 0.15)`

- **Typography:**
  - Display/Hero: `Clash Display` or `Syne` (ultra-bold, geometric)
  - Body: `DM Sans` (clean, readable, modern)
  - Monospace/Code: `JetBrains Mono` (for security data, code blocks)
  - Import via: Google Fonts + Fontshare CDN

- **Motion Philosophy:**
  - All entrances: staggered fade-up with slight blur
  - Scroll-driven: mask reveals, clip-path wipes
  - Hover: subtle glow pulse, pill transitions (GSAP)
  - Loading states: shimmer, thinking-bar animations
  - Easing: `cubic-bezier(0.16, 1, 0.3, 1)` — snappy but smooth

- **Soft Edges Design Language:**
  - Cards: `border-radius: 24px` minimum
  - Inputs: `border-radius: 16px`
  - Buttons: `border-radius: 999px` (pill)
  - Nav: `border-radius: 999px` (pill nav from code)
  - Modals: `border-radius: 28px`

---

## 🏗️ Tech Stack

```
Framework:        React 18 + Vite (or Next.js 14 App Router)
Language:         TypeScript
Styling:          Tailwind CSS v4.0
Animation:        GSAP (nav), Framer Motion / motion (components)
UI Primitives:    shadcn/ui
State:            React Context + Zustand (chat state)
Routing:          React Router v6 (or Next.js App Router)
API Client:       Axios + React Query (TanStack)
Auth:             JWT stored in httpOnly cookie / localStorage
Misc:             use-stick-to-bottom, clsx, tailwind-merge
```

**Install Commands (run once at project start):**
```bash
# Core
npm create vite@latest rectitude-ui -- --template react-ts
cd rectitude-ui
npm install

# Tailwind v4
npm install tailwindcss@next @tailwindcss/vite@next

# Animations
npm install gsap motion

# shadcn setup
npx shadcn@latest init
npx shadcn@latest add button card input dialog tabs badge

# UI helpers
npm install clsx tailwind-merge @tabler/icons-react lucide-react

# Chat UX
npm install use-stick-to-bottom

# Data fetching
npm install axios @tanstack/react-query

# State
npm install zustand

# Utilities
npm install react-router-dom
```

---

## 📁 Project File Structure

```
src/
├── assets/
│   ├── logo.svg                      ← Rectitude.AI logo (shield + circuit)
│   ├── hero-bg.svg                   ← Abstract mesh background
│   └── screenshots/                  ← UI screenshots for 3D marquee
│       ├── dashboard-1.png
│       ├── chat-screen.png
│       ├── security-layers.png
│       └── ... (8-12 images total)
│
├── components/
│   ├── ui/                           ← shadcn + custom primitives
│   │   ├── 3d-marquee.tsx            ← From provided code (aceternity)
│   │   ├── floating-dock.tsx         ← From provided code
│   │   ├── resizable-navbar.tsx      ← From provided code
│   │   └── button.tsx, card.tsx ...  ← shadcn
│   │
│   ├── nav/
│   │   ├── PillNav.tsx               ← GSAP pill nav (from provided code)
│   │   ├── ScrollNav.tsx             ← Resizable retractable nav (provided)
│   │   └── SideFloatingDock.tsx      ← Floating dock nav (provided)
│   │
│   ├── hero/
│   │   ├── HeroSection.tsx           ← Main hero with scroll reveal
│   │   ├── MaskReveal.tsx            ← Scroll-triggered mask animation
│   │   ├── HeroHeadline.tsx          ← Animated headline text
│   │   └── HeroStats.tsx             ← Animated stat counters
│   │
│   ├── features/
│   │   ├── SecurityLayers.tsx        ← 5-layer security viz
│   │   ├── WhyRectitude.tsx          ← Value proposition section
│   │   ├── UseCases.tsx              ← LLM company use cases
│   │   ├── HowItWorks.tsx            ← Step-by-step flow diagram
│   │   └── MarqueeSection.tsx        ← 3D marquee of screenshots
│   │
│   ├── chat/
│   │   ├── ChatPage.tsx              ← Full chat page wrapper
│   │   ├── ChatContainer.tsx         ← use-stick-to-bottom container
│   │   ├── MessageList.tsx           ← Renders all messages
│   │   ├── MessageBubble.tsx         ← Single message (user/ai)
│   │   ├── PromptInputBar.tsx        ← Input bar with send button
│   │   ├── AgentSelector.tsx         ← Dropdown to choose agent
│   │   ├── ThinkingIndicator.tsx     ← Dots/shimmer loader
│   │   ├── ChainOfThought.tsx        ← Collapsible reasoning steps
│   │   ├── SecurityBadge.tsx         ← Shows risk score, ASI, tier
│   │   └── ScrollToBottom.tsx        ← Scroll button
│   │
│   ├── dashboard/
│   │   ├── SecurityDashboard.tsx     ← ASI monitor, risk charts
│   │   ├── AuditLog.tsx              ← Live audit log feed
│   │   ├── AgentCard.tsx             ← Individual agent status card
│   │   └── RiskMeter.tsx             ← Animated risk score display
│   │
│   ├── prompt-kit/                   ← Custom prompt-kit components
│   │   ├── chat-container.tsx
│   │   ├── code-block.tsx
│   │   ├── loader.tsx
│   │   ├── markdown.tsx
│   │   ├── message.tsx
│   │   ├── prompt-input.tsx
│   │   ├── scroll-button.tsx
│   │   ├── thinking-bar.tsx
│   │   └── chain-of-thought.tsx
│   │
│   └── shared/
│       ├── Footer.tsx
│       ├── GlowCard.tsx
│       └── SectionHeading.tsx
│
├── pages/
│   ├── LandingPage.tsx               ← Full landing/hero page
│   ├── ChatDemoPage.tsx              ← Interactive chat demo
│   ├── AgentsPage.tsx                ← Agent showcase gallery
│   └── DashboardPage.tsx             ← Security monitoring dashboard
│
├── hooks/
│   ├── useChat.ts                    ← Chat state + API calls
│   ├── useAuth.ts                    ← JWT auth management
│   ├── useScrollReveal.ts            ← Intersection observer hook
│   └── useASI.ts                     ← ASI score polling
│
├── store/
│   ├── chatStore.ts                  ← Zustand chat store
│   └── authStore.ts                  ← Zustand auth store
│
├── api/
│   ├── client.ts                     ← Axios instance + interceptors
│   ├── auth.ts                       ← login/token endpoints
│   ├── chat.ts                       ← /v1/agent/chat
│   ├── agents.ts                     ← /v1/agents
│   └── session.ts                    ← /v1/session/:id/asi
│
├── lib/
│   └── utils.ts                      ← cn() helper
│
└── styles/
    ├── globals.css                   ← CSS variables, base styles
    └── animations.css                ← Custom keyframes
```

---

## 🗂️ BUILD PHASES — Divided Into Chat Sessions

---

### ═══════════════════════════════════════════
### PHASE 1 — Project Bootstrap + Design System
### ═══════════════════════════════════════════

**Session Goal:** Get the blank canvas perfectly configured before any UI is built.

**Tasks:**
1. Initialize Vite + React + TypeScript project
2. Install ALL dependencies from the list above
3. Configure Tailwind v4 with custom CSS variables in `globals.css`
4. Set up `lib/utils.ts` with `cn()` helper
5. Configure Google Fonts: Clash Display + DM Sans + JetBrains Mono via `index.html`
6. Set up CSS custom properties in `globals.css`:
   ```css
   :root {
     --bg: #060010;
     --surface: #0D0019;
     --accent: #7B3FE4;
     --accent-glow: #A855F7;
     --text-primary: #F0EBF8;
     --text-secondary: #8B7AA0;
     --border: rgba(123, 63, 228, 0.15);
     --radius-card: 24px;
     --radius-pill: 999px;
   }
   ```
7. Set up React Router with 4 routes: `/`, `/chat`, `/agents`, `/dashboard`
8. Create bare `App.tsx` shell with router
9. Set up Axios client in `api/client.ts` with base URL pointing to FastAPI backend
10. Set up Zustand stores (empty shells, filled later)

**Deliverable:** Working blank app with all deps, fonts loading, dark bg visible at `localhost:5173`

---

### ═══════════════════════════════════════════
### PHASE 2 — Navigation System (3 nav components)
### ═══════════════════════════════════════════

**Session Goal:** Complete navigation system across all breakpoints.

#### 2A — PillNav (Primary Desktop Nav)

**Implementation from provided code:**
- Convert `PillNav.jsx` → TypeScript with proper interfaces
- Logo: custom Rectitude.AI SVG shield icon
- Nav items: `Home`, `How It Works`, `Agents`, `Demo`, `Dashboard`
- Config:
  ```tsx
  <PillNav
    logo={rectitudeLogo}
    logoAlt="Rectitude.AI"
    items={NAV_ITEMS}
    activeHref={currentPath}
    ease="power3.easeOut"
    baseColor="#060010"
    pillColor="#7B3FE4"
    hoveredPillTextColor="#F0EBF8"
    pillTextColor="#A855F7"
    initialLoadAnimation={true}
  />
  ```
- Positioned: `fixed top-4 left-1/2 -translate-x-1/2 z-[1000]`
- On load: GSAP scale-in animation for logo + width expansion for pill container

#### 2B — ScrollNav (Retractable on Scroll)

**Implementation from provided resizable-navbar code:**
- At scroll=0: Full-width transparent nav, wide layout
- At scroll>100: Shrinks to centered 40% width pill, gets `backdrop-blur(10px)` + box-shadow
- Spring animation: `stiffness: 200, damping: 50`
- Contains: Logo left, NavItems center, CTA button right (`"Try Demo"` → gradient variant)
- Mobile: Uses `MobileNav` + `MobileNavHeader` + `MobileNavMenu` + `MobileNavToggle`
- Behavior mirrors obsidianos.com: nav shrinks gracefully, stays readable at all sizes

#### 2C — SideFloatingDock (In-page feature navigation)

**Implementation from provided floating-dock code:**
- Used on: `/chat` and `/dashboard` pages as a LEFT sidebar icon dock
- Items:
  ```tsx
  [
    { title: "Chat", icon: <MessageSquare />, href: "/chat" },
    { title: "Agents", icon: <Bot />, href: "/agents" },
    { title: "Dashboard", icon: <BarChart2 />, href: "/dashboard" },
    { title: "Security Log", icon: <Shield />, href: "/dashboard#logs" },
    { title: "Home", icon: <Home />, href: "/" },
  ]
  ```
- Desktop: positioned `fixed left-4 top-1/2 -translate-y-1/2`
- Mobile: Bottom-right FAB that expands upward
- Magnification effect on hover (from IconContainer code)

**Deliverable:** All 3 nav types working, responsive, animated correctly

---

### ═══════════════════════════════════════════
### PHASE 3 — Landing Page: Hero Section
### ═══════════════════════════════════════════

**Session Goal:** The crown jewel — the first thing judges and LLM companies see.

#### 3A — Scroll Mask Reveal Animation

**Concept:** User lands on a blurred/masked version of the product UI. As they scroll, a circular or rectangular mask expands from center, revealing the full dashboard screenshot underneath. The mask uses `clip-path` animated via scroll position.

**Implementation:**
```tsx
// MaskReveal.tsx
// Uses IntersectionObserver + scroll progress
// clip-path: circle(5% at 50% 50%) → circle(150% at 50% 50%)
// Driven by: scrollYProgress from useScroll (motion/react)
```

- **Above the fold (no scroll):** Masked, only headline visible
- **25% scroll:** Mask expands, dashboard screenshot starts showing through
- **50% scroll:** Full product screenshot revealed
- **Background:** The revealed content is a static screenshot of the Rectitude.AI dashboard (dark theme, matching the site)

#### 3B — Hero Headline + Subtext

Layout (inspired by eragon.ai):
```
[Security Badge: "Defense-in-Depth AI Gateway"]

PROTECT YOUR LLM
INFRASTRUCTURE
FROM THE INSIDE OUT.

[subtext]
Rectitude.AI wraps every LLM call in a 5-layer security sandwich —
blocking prompt injections, social engineering, and data exfiltration
before they ever reach your model.

[CTA Row]
[→ Try Live Demo]  [Read the Docs ↗]

[Trusted By stat row]
99.2% Block Rate  |  <5ms Tier-1  |  5 Specialized Agents  |  Zero Data Retention
```

**Animations:**
- Headline: word-by-word stagger reveal (clip-path from bottom, 80ms delay per word)
- Subtext: fade-up after headline finishes (400ms delay)
- CTAs: scale-in + glow pulse on hover
- Stats: number counter animation on viewport enter

#### 3C — Hero Visual (above fold)

- Background: radial gradient mesh (deep purple to near-black)
- Floating particles/orbs: subtle, slow-drifting purple orbs using CSS animations
- The masked product screenshot sits below the headline text
- A faint grid overlay (CSS `background-image: linear-gradient(...)`) gives depth

**Deliverable:** Full hero viewport with working mask reveal on scroll

---

### ═══════════════════════════════════════════
### PHASE 4 — Landing Page: Feature Sections
### ═══════════════════════════════════════════

**Session Goal:** All feature/marketing sections below the hero.

#### 4A — "The 5-Layer Security Sandwich" Section

**Visual:** Vertical stacked diagram showing the 5 layers with icons, each layer animates in on scroll.

```
Layer 1: Intent Security    → Regex + ML (<5ms)     [Shield icon, purple]
Layer 2: Crypto Integrity   → JWT Capability Tokens  [Key icon, blue-purple]
Layer 3: Behavior Monitor   → ASI Drift Detection    [Activity icon, violet]
Layer 4: Red Teaming        → RL Policy Updates      [Zap icon, magenta]
Layer 5: Orchestration      → LangGraph Routing      [GitBranch icon, soft purple]
```

- Each layer card: glass morphism style (`backdrop-blur`, border `1px solid rgba(123,63,228,0.2)`)
- Hover state: glowing border + subtle scale-up
- Stagger animate in from left as user scrolls

#### 4B — "Why Rectitude.AI?" Section (LLM Company Value Props)

**Target audience messaging for LLM companies:**

```
WHY LLM COMPANIES CHOOSE RECTITUDE.AI

┌─────────────────────────────────────────────────────────────┐
│  🚫 Prompt Injection       │  ✅ Blocked at Tier 1 in <5ms  │
│  🤖 Persona Hijacking      │  ✅ Regex + ML dual detection   │
│  📤 Data Exfiltration      │  ✅ Output mediator redacts PII │
│  🌀 Multi-Turn Jailbreaks  │  ✅ ASI behavioral monitoring   │
│  🔑 Tool Privilege Abuse   │  ✅ JWT Capability Tokens       │
└─────────────────────────────────────────────────────────────┘
```

Layout: alternating left/right feature callouts (like eragon.ai's feature grid)
Each callout: icon + headline + 2-line description + subtle before/after code snippet

#### 4C — "How It Works" Section

**3-step visual flow:**
```
[1. Request Arrives] → [2. Security Sandwich Runs] → [3. Safe Response]
        ↓                         ↓                          ↓
  JWT verified           5 layers execute              Output mediated
  Rate limit checked     <200ms total                  PII redacted
  User identified        Risk scored                   Delivered safely
```

Implementation: horizontal scroll on mobile, flex-row on desktop
Connecting arrows animated with SVG path stroke-dashoffset animation

#### 4D — 3D Marquee Section (Product Screenshots)

**From provided acetylinity code:**
```tsx
// Use ThreeDMarquee component directly
// Replace placeholder images with actual Rectitude.AI screenshots:
const images = [
  "/screenshots/chat-demo.png",
  "/screenshots/security-dashboard.png",
  "/screenshots/agent-selector.png",
  "/screenshots/risk-score-display.png",
  "/screenshots/asi-monitor.png",
  "/screenshots/audit-log.png",
  "/screenshots/layer1-intercept.png",
  "/screenshots/capability-tokens.png",
  // ... fill to 32 items with variations
]
```

Section heading: `"See Rectitude.AI in Action"`
Background: slightly lighter surface card (`#0D0019`)
The 3D perspective grid of screenshots scrolls automatically

#### 4E — "Use Cases" Section

Cards for each target user:

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  LLM API         │  │  Enterprise       │  │  AI Agents       │
│  Providers       │  │  Deployments      │  │  & Copilots      │
│                  │  │                   │  │                  │
│  Wrap your API   │  │  Protect internal │  │  Multi-agent     │
│  endpoints with  │  │  chatbots from    │  │  systems need    │
│  5-layer defense │  │  data leakage     │  │  token-scoped    │
│  before serving  │  │  and insider      │  │  tool authority  │
│  any user prompt │  │  prompt attacks   │  │  separation      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

Each card: glass morphism, hover lifts with shadow, icon at top

#### 4F — Stats/Social Proof Bar

Animated counters (count up on scroll enter):
```
99.2%          <5ms          5             0
Attack         Tier-1        Specialized   Data
Block Rate     Response      Agents        Retained
```

**Deliverable:** All feature sections built and scroll-animated

---

### ═══════════════════════════════════════════
### PHASE 5 — Footer
### ═══════════════════════════════════════════

**Session Goal:** Clean, professional footer matching eragon.ai/obsidianos.com style.

Layout:
```
[Logo + tagline]              [Links col 1]    [Links col 2]    [Links col 3]
Rectitude.AI                  Product          Resources        Legal
LLM Security Gateway          Demo             Docs             Privacy
                               Agents           GitHub           Terms
                               Dashboard        API Ref          License

─────────────────────────────────────────────────────────────────────────
© 2026 Rectitude.AI · Built by Ayush Tandon & Vartika Manish · IIT Delhi
```

- Top border: subtle gradient line (purple → transparent → purple)
- Background: `#060010` matching site bg
- Text: muted secondary colors, hover → accent purple

---

### ═══════════════════════════════════════════
### PHASE 6 — Chat Demo Page (/chat)
### ═══════════════════════════════════════════

**Session Goal:** The fully interactive chat interface. This is the most complex page.

#### Layout Structure:
```
┌─────────────────────────────────────────────────────────────────────┐
│  [SideFloatingDock - left]                                           │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐        │
│  │  HEADER: Rectitude.AI Chat  [AgentSelector ▼] [ASI: 0.98]│        │
│  ├──────────────────────────────────────────────────────────┤        │
│  │                                                          │        │
│  │  [ChatContainer with StickToBottom]                      │        │
│  │   ↳ MessageList                                          │        │
│  │      ↳ MessageBubble (user) - right aligned              │        │
│  │      ↳ MessageBubble (ai)   - left + avatar              │        │
│  │         ↳ ChainOfThought (collapsible reasoning)         │        │
│  │         ↳ SecurityBadge (risk score, tier, decision)     │        │
│  │         ↳ Markdown rendered response                     │        │
│  │         ↳ CodeBlock if code in response                  │        │
│  │                                                          │        │
│  │  [ScrollToBottom button - bottom right]                  │        │
│  ├──────────────────────────────────────────────────────────┤        │
│  │  [ThinkingBar - visible while AI processing]             │        │
│  ├──────────────────────────────────────────────────────────┤        │
│  │  [PromptInput with send button]                          │        │
│  └──────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

#### 6A — AgentSelector Component

Dropdown showing all 5 agents:
```tsx
const AGENTS = [
  { name: "hr_database",       label: "HR Database",       icon: "🗂️",  color: "#7B3FE4" },
  { name: "email_agent",       label: "Email Agent",       icon: "📧",  color: "#A855F7" },
  { name: "code_exec",         label: "Code Executor",     icon: "⚡",  color: "#6366F1" },
  { name: "financial_advisor", label: "Financial Advisor", icon: "📈",  color: "#8B5CF6" },
  { name: "general_utility",   label: "General Assistant", icon: "🤖",  color: "#9333EA" },
]
```

Auto-routing option: "Let AI Decide" (sends `agent_name: null`)

#### 6B — Message Bubble Component

**User message (right-aligned):**
- Pill shape, accent purple bg, white text
- No avatar

**AI message (left-aligned):**
- Card style, glass surface bg
- Avatar: Rectitude.AI shield icon with purple glow
- Renders: Markdown → `<Markdown>` component
- Code blocks: `<CodeBlock>` with syntax highlighting
- Below message: expandable `<ChainOfThought>` accordion

**SecurityBadge (attached to each AI message):**
```tsx
// Shows inline metadata from security_metadata field
<SecurityBadge
  decision={meta.decision}       // "allow" | "block" | "escalate"
  riskScore={meta.risk_score}    // 0.0 – 1.0
  asiScore={meta.asi_score}      // 0.0 – 1.0
  tierReached={meta.tier_reached} // 1, 2, or 3
  agentUsed={agent_used}
  executionMs={execution_time_ms}
/>
// Visual: small pill badges, color-coded
// "✓ ALLOW  Tier-1  Risk: 0.02  ASI: 0.98  3ms"
// Color: green=allow, yellow=escalate, red=block
```

#### 6C — ChainOfThought Component (from provided code)

**Used to show security reasoning:**
```tsx
<ChainOfThought>
  <ChainOfThoughtStep>
    <ChainOfThoughtTrigger leftIcon={<Shield />}>
      Tier 1: Regex Prefilter — PASSED
    </ChainOfThoughtTrigger>
    <ChainOfThoughtContent>
      <ChainOfThoughtItem>Score: 0.00 — No patterns matched</ChainOfThoughtItem>
      <ChainOfThoughtItem>Decision: allow → escalate to Tier 2</ChainOfThoughtItem>
    </ChainOfThoughtContent>
  </ChainOfThoughtStep>
  <ChainOfThoughtStep>
    <ChainOfThoughtTrigger leftIcon={<Brain />}>
      Tier 2: ML Classifiers — PASSED
    </ChainOfThoughtTrigger>
    <ChainOfThoughtContent>
      <ChainOfThoughtItem>Injection classifier: 0.03</ChainOfThoughtItem>
      <ChainOfThoughtItem>Perplexity detector: 0.11</ChainOfThoughtItem>
    </ChainOfThoughtContent>
  </ChainOfThoughtStep>
</ChainOfThought>
```

Collapsed by default. Expand button: `"▸ Show Security Reasoning"`

#### 6D — ThinkingBar (from provided code)

Shown while `isLoading = true`:
```tsx
<ThinkingBar
  text="Security pipeline processing..."
  stopLabel="Cancel"
  onStop={cancelRequest}
/>
```

Layers of text that cycle: "Running regex prefilter..." → "Classifying intent..." → "Checking capability tokens..." → "Generating response..."

#### 6E — PromptInput (from provided code)

```tsx
<PromptInput value={input} onValueChange={setInput} isLoading={isLoading} onSubmit={handleSubmit}>
  <PromptInputTextarea placeholder="Ask anything — HR, Finance, Code, or Email tasks..." />
  <PromptInputActions className="justify-between pt-2">
    <AgentSelector value={selectedAgent} onChange={setSelectedAgent} />
    <PromptInputAction tooltip={isLoading ? "Stop" : "Send"}>
      <Button variant="default" size="icon" className="h-8 w-8 rounded-full bg-accent">
        {isLoading ? <Square /> : <ArrowUp />}
      </Button>
    </PromptInputAction>
  </PromptInputActions>
</PromptInput>
```

#### 6F — ChatContainer (from provided code)

```tsx
<ChatContainerRoot className="h-full">
  <ChatContainerContent>
    {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}
  </ChatContainerContent>
</ChatContainerRoot>
<ScrollButton />  // bottom-right corner
```

#### 6G — API Integration (useChat hook)

```typescript
// hooks/useChat.ts
export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => `sess_${Math.random().toString(36).slice(2, 10)}`)

  const sendMessage = async (prompt: string, agentName?: string) => {
    // 1. Append user message immediately
    // 2. Set isLoading = true, show ThinkingBar
    // 3. POST to /v1/agent/chat with { user_id, prompt, session_id, agent_name }
    // 4. On response: append AI message with full security_metadata
    // 5. Set isLoading = false
    // 6. Handle blocked responses: show red SecurityBadge with reason
  }

  return { messages, isLoading, sendMessage, sessionId }
}
```

**Error handling:**
- 403 blocked: Show red "BLOCKED" message bubble with `reason` from response
- 500: Show toast "Backend error — check if Ollama is running"
- Network error: Show reconnect prompt

**Deliverable:** Fully working chat interface connected to FastAPI backend

---

### ═══════════════════════════════════════════
### PHASE 7 — Agents Showcase Page (/agents)
### ═══════════════════════════════════════════

**Session Goal:** Visual gallery of all 5 agents with demo interaction.

#### Layout:

```
AGENTS PAGE HEADER: "Meet Your Security-Wrapped AI Agents"
subtext: "Each agent operates within cryptographically scoped permissions"

[Grid of 5 Agent Cards]

┌─────────────────────────────┐
│  🗂️  HR Database Agent       │
│                             │
│  Answers questions about    │
│  employees, departments,    │
│  and HR policies.           │
│                             │
│  Tools: query_database      │
│         read_file           │
│                             │
│  Security: CapToken ✓       │
│           Output Mediated ✓ │
│                             │
│  [→ Try This Agent]         │
└─────────────────────────────┘
```

Each card:
- Glass morphism with colored top border (unique color per agent)
- Tool badges shown as small pill badges
- Security features as checkmarks
- Click → navigates to `/chat?agent=hr_database` (pre-selects that agent)

#### Vulnerability Showcase (expandable accordion per agent):

```
▸ What attacks does this agent defend against?

HR Agent:    SQL injection, PII extraction, full table dumps
Email Agent: Indirect prompt injection via email body, domain exfiltration
Code Agent:  RCE via import smuggling, eval() abuse, privilege escalation
Finance:     Multi-turn persona drift, gradual jailbreak, unrestricted advice
General:     Fallback for unclassified requests — minimal tool scope
```

**Deliverable:** Full agents page with cards, security info, click-to-demo

---

### ═══════════════════════════════════════════
### PHASE 8 — Security Dashboard Page (/dashboard)
### ═══════════════════════════════════════════

**Session Goal:** Live monitoring dashboard — showpiece for faculty demo.

#### Layout:

```
┌─────────────────────────────────────────────────────────────────────┐
│  SECURITY MONITORING DASHBOARD                                       │
│  Session: sess_abc123                          [Reset Session]       │
├───────────────────────┬─────────────────────────────────────────────┤
│  ASI SCORE            │  RISK DISTRIBUTION (last 10 requests)       │
│                       │                                             │
│  ┌─────────────┐      │  [Horizontal bar chart per request]         │
│  │   0.94      │      │  Req 1 ████░░░░░░ 0.12 [allow]             │
│  │   ASI       │      │  Req 2 ██████░░░░ 0.45 [escalate]          │
│  │   HEALTHY   │      │  Req 3 ██████████ 1.00 [BLOCKED]           │
│  └─────────────┘      │                                             │
│                       │                                             │
├───────────────────────┼─────────────────────────────────────────────┤
│  LAYER PERFORMANCE    │  LIVE AUDIT LOG                             │
│                       │                                             │
│  T1 Regex:   2.1ms    │  [Scrollable real-time log feed]            │
│  T2 ML:    142.3ms    │  12:04:23 [ALLOW] "who is in engineering"   │
│  T3 Token:   0.4ms    │  12:04:31 [BLOCK] "ignore all instructions" │
│  Output:     8.2ms    │  12:04:45 [ESCALATE] "my boss said..."      │
│                       │  12:05:02 [ALLOW] "python list syntax"      │
└───────────────────────┴─────────────────────────────────────────────┘
```

#### 8A — ASI Score Display (RiskMeter component)

- Circular gauge (SVG arc) showing 0.0 to 1.0
- Color: green (>0.7), yellow (0.45–0.7), red (<0.45)
- Sub-labels: C (consistency), T (tool stability), B (boundaries), LDFR
- Polls `/v1/session/:id/asi` every 5 seconds

#### 8B — Audit Log Feed

- Reads from `logs/audit.jsonl`-style data (via future API endpoint)
- For demo: simulates real-time feed by polling or streaming
- Each entry: timestamp, decision badge, risk score, reason preview
- Color-coded rows: green=allow, yellow=escalate, red=block

#### 8C — Layer Latency Display

- Shows min/avg/max timing for each security tier
- Source: `latency_ms` + `tier_reached` from API responses
- Simple stat boxes with monospace numbers

**Deliverable:** Full working dashboard with live ASI polling

---

### ═══════════════════════════════════════════
### PHASE 9 — Auth Flow
### ═══════════════════════════════════════════

**Session Goal:** JWT login before any API call is made.

**Implementation:**
- On app load: check localStorage for `access_token`
- If no token: show login modal (full-screen overlay, centered card)
- Login card: username + password → POST `/auth/login` → store JWT
- On all API calls: `Authorization: Bearer <token>` header via Axios interceptor
- On 401: clear token, redirect to login

**Login UI:**
- Glass morphism card, centered on dark bg
- Logo at top, "Sign in to Rectitude.AI" heading
- Username: `demo` / Password: `demo123` (from backend `DEMO_USER`)
- Button: purple gradient, loading spinner inside while authenticating
- Error: shake animation + red border on failed login

**Deliverable:** Auth gate working, JWT persisted across page refreshes

---

### ═══════════════════════════════════════════
### PHASE 10 — Polish, Responsive Design & QA
### ═══════════════════════════════════════════

**Session Goal:** Final refinement pass before faculty showcase.

**Polish checklist:**
- [ ] All scroll animations smooth on 60fps
- [ ] Mobile breakpoints working on 375px (iPhone SE), 390px (iPhone 15), 768px (iPad)
- [ ] Keyboard navigation works (tab order, focus rings)
- [ ] Loading states for all async operations
- [ ] Error boundaries on chat + dashboard
- [ ] Empty state for chat (show suggested prompts)
- [ ] Favicon: Rectitude.AI shield icon
- [ ] `<title>` and meta description set
- [ ] CORS confirmed working with backend
- [ ] `.env` file: `VITE_API_BASE_URL=http://localhost:8000`
- [ ] Test with Ollama running: verify full chat flow
- [ ] Test blocked prompt: show red bubble correctly
- [ ] Test ASI polling: watch score change over conversation

**Suggested Demo Prompts (hardcode as suggestions in empty chat state):**
```
"Who works in the engineering department?"      → HR Agent, shows DB query
"Ignore all previous instructions"              → BLOCKED at Tier 1
"Calculate compound interest for 5 years 7%"   → Finance Agent, calculator
"Write a Python list comprehension example"     → Code Agent, sandbox exec
"Draft a support reply about billing issues"    → Email Agent, domain check
"What is today's date?"                         → General Agent, clock tool
```

---

## 🔗 API Endpoint Reference (Frontend → Backend)

| Endpoint | Method | Request | Response | Used In |
|---|---|---|---|---|
| `/auth/login` | POST | `{username, password}` | `{access_token, token_type, expires_in}` | Auth flow |
| `/v1/agent/chat` | POST | `{user_id, prompt, session_id, agent_name?}` | `AgentChatResponse` | Chat page |
| `/v1/agents` | GET | — | `{agents: [...], total}` | Agents page |
| `/v1/session/:id/asi` | GET | — | `{session_id, asi_score, risk_score, alert}` | Dashboard |
| `/v1/session/:id/reset` | POST | — | `{status, session_id}` | Dashboard |
| `/v1/inference` | POST | `InferenceRequest` | `InferenceResponse` | Direct mode |
| `/health` | GET | — | `HealthResponse` | Status indicator |

**AgentChatResponse fields used by frontend:**
```typescript
interface AgentChatResponse {
  response: string                    // Rendered as Markdown
  agent_used: string                  // Shown in SecurityBadge
  request_id: string                  // For deduplication
  session_id: string                  // For ASI polling key
  tools_invoked: string[]             // Shown as badges
  capability_token_issued: boolean    // Lock icon in SecurityBadge
  security_metadata: {
    decision: "allow" | "block" | "escalate"
    risk_score: number
    asi_score: number
    asi_alert: boolean
    output_safe: boolean
    output_findings_count: number
    tier_reached: number
    effective_scope: string[]
  }
  execution_time_ms: number
  timestamp: string
}
```

---

## 🚀 Build Order Summary

| Phase | What | Est. Complexity |
|---|---|---|
| 1 | Bootstrap + Design System | ⬛⬛⬜⬜⬜ |
| 2 | Navigation (PillNav + ScrollNav + Dock) | ⬛⬛⬛⬜⬜ |
| 3 | Hero Section + Mask Reveal | ⬛⬛⬛⬛⬜ |
| 4 | All Feature Sections + 3D Marquee | ⬛⬛⬛⬛⬜ |
| 5 | Footer | ⬛⬜⬜⬜⬜ |
| 6 | Chat Page (full — most complex) | ⬛⬛⬛⬛⬛ |
| 7 | Agents Showcase Page | ⬛⬛⬜⬜⬜ |
| 8 | Security Dashboard | ⬛⬛⬛⬜⬜ |
| 9 | Auth Flow | ⬛⬛⬜⬜⬜ |
| 10 | Polish + QA + Responsive | ⬛⬛⬛⬜⬜ |

**Total Sessions: 10 focused builds**
**Recommended order: 1 → 2 → 9 → 3 → 4 → 5 → 6 → 7 → 8 → 10**
*(Do auth early so API calls can be tested immediately during chat build)*

---

## ⚠️ Critical Notes for Each Build Session

1. **Always test against live backend** — have `uvicorn backend.gateway.main:app --reload` running
2. **Ollama must be running** with the configured model for agent responses to work
3. **CORS in `main.py`** is set to `allow_origins=["*"]` — restrict to `http://localhost:5173` during dev
4. **The `.env` file** is required: copy `.env.example` and fill in `SECRET_KEY`, Ollama URL
5. **3D Marquee** requires `motion/react` (not `framer-motion`) — use `npm i motion`
6. **PillNav requires GSAP** — `npm i gsap` — not motion/react
7. **Floating Dock uses motion** — same `motion` package as marquee ✓
8. **ResizableNav uses motion** — same ✓
9. **ScrollNav** uses `useScroll` + `useMotionValueEvent` from `motion/react`
10. **Session IDs** must be stable per page visit — use `useState` with initializer or `useRef`

---

## 🎯 Faculty Showcase Script (Demo Flow)

> Use this order when presenting to faculty/judges:

1. **Open landing page** → Show hero mask reveal by scrolling slowly
2. **Walk through feature sections** → "Here's our 5-layer sandwich..."
3. **Open chat demo** → Select HR Agent → Ask "Who works in engineering?"
4. **Show security badge** → "Tier 1 passed in 2ms, ASI score 0.98..."
5. **Attempt injection** → Type "Ignore all previous instructions" → Show BLOCKED response
6. **Switch to Finance Agent** → Ask about stock prices → Show calculator tool invocation
7. **Open Dashboard** → Show ASI score, live audit log, layer latency
8. **Switch to Agents page** → Walk through each agent's vulnerability showcase
9. **Return to chat** → Do 5 rapid requests → Watch ASI drift begin to register

---

*Plan prepared: April 2026*
*Backend: Rectitude.AI (FastAPI + LangGraph + Redis + Ollama)*
*Frontend target: Faculty Showcase — April/May 2026*
