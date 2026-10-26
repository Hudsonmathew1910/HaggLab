from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ILLUST_DIR = BASE_DIR / 'static' / 'img' / 'illustrations'
ILLUST_DIR.mkdir(parents=True, exist_ok=True)

ILLUSTRATIONS = {
    # 1. Solution: Document Assistant
    'solution-document-assistant.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="100%" height="100%" fill="none">
  <!-- Stack of Source Documents -->
  <rect x="24" y="44" width="76" height="96" rx="4" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2"/>
  <line x1="36" y1="64" x2="84" y2="64" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="36" y1="80" x2="74" y2="80" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="36" y1="96" x2="80" y2="96" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <rect x="36" y="32" width="76" height="96" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <line x1="48" y1="52" x2="96" y2="52" stroke="#0B6E6E" stroke-width="2" stroke-linecap="round"/>
  <line x1="48" y1="68" x2="86" y2="68" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="48" y1="84" x2="92" y2="84" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="48" y1="100" x2="70" y2="100" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>

  <!-- Connecting Processing Pipeline -->
  <path d="M120 80 H 156" stroke="#0E1B2A" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="154,76 162,80 154,84" fill="#0E1B2A"/>

  <!-- AI / Vector Embedding Engine Node -->
  <circle cx="184" cy="80" r="22" fill="#0E1B2A" stroke="#0E1B2A" stroke-width="2"/>
  <circle cx="184" cy="80" r="14" fill="#0B6E6E"/>
  <polygon points="184,72 191,80 184,88 177,80" fill="#FCFBF8"/>

  <!-- Connecting Output Arrow -->
  <path d="M214 80 H 244" stroke="#0E1B2A" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="242,76 250,80 242,84" fill="#0E1B2A"/>

  <!-- Answer Panel with Source Reference Badge -->
  <rect x="246" y="36" width="60" height="88" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="254" y="46" width="44" height="8" rx="2" fill="#0B6E6E"/>
  <line x1="254" y1="66" x2="298" y2="66" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="254" y1="78" x2="290" y2="78" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="254" y1="90" x2="294" y2="90" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <rect x="254" y="104" width="28" height="12" rx="2" fill="#C4572A"/>

  <!-- Baseline Shelf -->
  <line x1="16" y1="168" x2="304" y2="168" stroke="#0E1B2A" stroke-width="2"/>
  <circle cx="64" cy="168" r="4" fill="#0B6E6E"/>
  <circle cx="184" cy="168" r="4" fill="#C4572A"/>
  <circle cx="276" cy="168" r="4" fill="#0B6E6E"/>
</svg>''',

    # 2. Solution: Store and Booking
    'solution-store-booking.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="100%" height="100%" fill="none">
  <!-- Store Shelf / Product Catalog Frame -->
  <rect x="28" y="38" width="94" height="102" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="38" y="48" width="34" height="34" rx="2" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="1.5"/>
  <rect x="78" y="48" width="34" height="34" rx="2" fill="#0B6E6E"/>
  <line x1="38" y1="96" x2="104" y2="96" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="38" y1="108" x2="88" y2="108" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <rect x="38" y="120" width="40" height="10" rx="2" fill="#C4572A"/>

  <!-- Bi-directional booking calendar bridge -->
  <path d="M130 89 H 176" stroke="#0E1B2A" stroke-width="2"/>
  <polygon points="174,85 182,89 174,93" fill="#0E1B2A"/>

  <!-- Calendar Scheduling Matrix -->
  <rect x="184" y="38" width="108" height="102" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="184" y="38" width="108" height="24" rx="4" fill="#0E1B2A"/>
  <!-- Date Grid Dots -->
  <rect x="194" y="72" width="14" height="14" rx="2" fill="#ECE6D8"/>
  <rect x="214" y="72" width="14" height="14" rx="2" fill="#ECE6D8"/>
  <rect x="234" y="72" width="14" height="14" rx="2" fill="#0B6E6E"/>
  <rect x="254" y="72" width="14" height="14" rx="2" fill="#ECE6D8"/>
  <rect x="194" y="94" width="14" height="14" rx="2" fill="#ECE6D8"/>
  <rect x="214" y="94" width="14" height="14" rx="2" fill="#C4572A"/>
  <rect x="234" y="94" width="14" height="14" rx="2" fill="#ECE6D8"/>
  <rect x="254" y="94" width="14" height="14" rx="2" fill="#0B6E6E"/>
  <rect x="194" y="118" width="74" height="12" rx="2" fill="#0B6E6E"/>

  <!-- Baseline -->
  <line x1="16" y1="168" x2="304" y2="168" stroke="#0E1B2A" stroke-width="2"/>
</svg>''',

    # 3. Solution: Data and Forecast
    'solution-data-forecast.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="100%" height="100%" fill="none">
  <!-- Analytics Chart Frame -->
  <rect x="36" y="32" width="248" height="116" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <line x1="36" y1="60" x2="284" y2="60" stroke="#DDD6C6" stroke-width="1.5"/>
  <line x1="36" y1="92" x2="284" y2="92" stroke="#DDD6C6" stroke-width="1.5"/>
  <line x1="36" y1="124" x2="284" y2="124" stroke="#DDD6C6" stroke-width="1.5"/>

  <!-- Historic Data Bars -->
  <rect x="60" y="96" width="18" height="44" rx="2" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="1.5"/>
  <rect x="90" y="80" width="18" height="60" rx="2" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="1.5"/>
  <rect x="120" y="68" width="18" height="72" rx="2" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="1.5"/>
  <rect x="150" y="52" width="18" height="88" rx="2" fill="#0B6E6E" stroke="#0E1B2A" stroke-width="1.5"/>

  <!-- Predictive Trendline & Confidence Interval Projection -->
  <path d="M168 52 Q 200 44, 230 40 T 264 34" stroke="#C4572A" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Forecast Cone -->
  <polygon points="168,52 264,24 264,48" fill="rgba(196, 87, 42, 0.12)"/>
  <circle cx="264" cy="34" r="5" fill="#C4572A" stroke="#0E1B2A" stroke-width="1.5"/>

  <!-- Baseline -->
  <line x1="16" y1="168" x2="304" y2="168" stroke="#0E1B2A" stroke-width="2"/>
  <circle cx="159" cy="168" r="4" fill="#0B6E6E"/>
  <circle cx="264" cy="168" r="4" fill="#C4572A"/>
</svg>''',

    # 4. Solution: Internal Automations
    'solution-automation.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="100%" height="100%" fill="none">
  <!-- Trigger Event Node -->
  <rect x="32" y="64" width="60" height="52" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="42" y="74" width="40" height="8" rx="2" fill="#C4572A"/>
  <circle cx="62" cy="98" r="6" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="1.5"/>

  <!-- Flow Connector -->
  <path d="M100 90 H 132" stroke="#0E1B2A" stroke-width="2"/>
  <polygon points="130,86 138,90 130,94" fill="#0E1B2A"/>

  <!-- Logic & Branching Node -->
  <polygon points="172,60 204,90 172,120 140,90" fill="#0B6E6E" stroke="#0E1B2A" stroke-width="2"/>
  <circle cx="172" cy="90" r="5" fill="#FCFBF8"/>

  <!-- Dual Action Branch Out -->
  <path d="M204 80 L 236 56" stroke="#0E1B2A" stroke-width="2"/>
  <path d="M204 100 L 236 124" stroke="#0E1B2A" stroke-width="2"/>

  <!-- Target Action 1 -->
  <rect x="236" y="38" width="56" height="40" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <line x1="246" y1="52" x2="282" y2="52" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="246" y1="64" x2="272" y2="64" stroke="#0B6E6E" stroke-width="2" stroke-linecap="round"/>

  <!-- Target Action 2 -->
  <rect x="236" y="104" width="56" height="40" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <line x1="246" y1="118" x2="282" y2="118" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="246" y1="130" x2="268" y2="130" stroke="#C4572A" stroke-width="2" stroke-linecap="round"/>

  <!-- Baseline -->
  <line x1="16" y1="168" x2="304" y2="168" stroke="#0E1B2A" stroke-width="2"/>
</svg>''',

    # 5. Solution: Complete Product Build
    'solution-product-build.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" width="100%" height="100%" fill="none">
  <!-- Isometric Architectural Layers of a Full System -->
  <!-- Layer 3: Database & Infra (bottom) -->
  <polygon points="160,118 244,78 160,38 76,78" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2"/>
  <polygon points="76,78 160,118 160,132 76,92" fill="#DDD6C6" stroke="#0E1B2A" stroke-width="2"/>
  <polygon points="160,118 244,78 244,92 160,132" fill="#CFC9BA" stroke="#0E1B2A" stroke-width="2"/>

  <!-- Layer 2: API & Logic Engine (middle) -->
  <g transform="translate(0, -32)">
    <polygon points="160,118 244,78 160,38 76,78" fill="#0B6E6E" stroke="#0E1B2A" stroke-width="2"/>
    <polygon points="76,78 160,118 160,132 76,92" fill="#084F50" stroke="#0E1B2A" stroke-width="2"/>
    <polygon points="160,118 244,78 244,92 160,132" fill="#063E3E" stroke="#0E1B2A" stroke-width="2"/>
  </g>

  <!-- Layer 1: Web & Mobile Interface (top) -->
  <g transform="translate(0, -64)">
    <polygon points="160,118 244,78 160,38 76,78" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
    <polygon points="76,78 160,118 160,132 76,92" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2"/>
    <polygon points="160,118 244,78 244,92 160,132" fill="#DDD6C6" stroke="#0E1B2A" stroke-width="2"/>
    <!-- Interface detail on top surface -->
    <line x1="130" y1="62" x2="190" y2="62" stroke="#C4572A" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="110" y1="74" x2="170" y2="74" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
    <line x1="140" y1="86" x2="200" y2="86" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  </g>

  <!-- Baseline -->
  <line x1="16" y1="168" x2="304" y2="168" stroke="#0E1B2A" stroke-width="2"/>
</svg>''',

    # 6. Diagram: 4-Step Project Flow
    'diagram-4step-flow.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 140" width="100%" height="100%" fill="none">
  <!-- Timeline Rail -->
  <line x1="60" y1="56" x2="540" y2="56" stroke="#DDD6C6" stroke-width="3"/>
  <line x1="60" y1="56" x2="220" y2="56" stroke="#0B6E6E" stroke-width="3"/>

  <!-- Step 1: Scope -->
  <circle cx="60" cy="56" r="20" fill="#0B6E6E" stroke="#0E1B2A" stroke-width="2"/>
  <text x="60" y="62" text-anchor="middle" font-family="'IBM Plex Mono', monospace" font-size="14" font-weight="600" fill="#FCFBF8">1</text>
  <rect x="20" y="88" width="80" height="24" rx="2" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="1.5"/>
  <line x1="30" y1="100" x2="90" y2="100" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>

  <!-- Step 2: Prototype -->
  <circle cx="220" cy="56" r="20" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <text x="220" y="62" text-anchor="middle" font-family="'IBM Plex Mono', monospace" font-size="14" font-weight="600" fill="#0E1B2A">2</text>
  <rect x="180" y="88" width="80" height="24" rx="2" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="1.5"/>
  <line x1="190" y1="100" x2="250" y2="100" stroke="#0B6E6E" stroke-width="2" stroke-linecap="round"/>

  <!-- Step 3: Build & Integrate -->
  <circle cx="380" cy="56" r="20" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2"/>
  <text x="380" y="62" text-anchor="middle" font-family="'IBM Plex Mono', monospace" font-size="14" font-weight="600" fill="#0E1B2A">3</text>
  <rect x="340" y="88" width="80" height="24" rx="2" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="1.5"/>
  <line x1="350" y1="100" x2="410" y2="100" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>

  <!-- Step 4: Deliver & Handover -->
  <circle cx="540" cy="56" r="20" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2"/>
  <text x="540" y="62" text-anchor="middle" font-family="'IBM Plex Mono', monospace" font-size="14" font-weight="600" fill="#C4572A">4</text>
  <rect x="500" y="88" width="80" height="24" rx="2" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="1.5"/>
  <line x1="510" y1="100" x2="570" y2="100" stroke="#C4572A" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    # 7. Diagram: 3-Layer Result Model (Measured, Expected, Your Result)
    'diagram-3layer-result.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 220" width="100%" height="100%" fill="none">
  <!-- Layer 1: Measured in the Demo (Solid Ground) -->
  <rect x="30" y="148" width="320" height="44" rx="4" fill="#0E1B2A" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="42" y="160" width="20" height="20" rx="2" fill="#1F7A4D"/>
  <line x1="72" y1="166" x2="180" y2="166" stroke="#FCFBF8" stroke-width="2" stroke-linecap="round"/>
  <line x1="72" y1="178" x2="280" y2="178" stroke="#DDD6C6" stroke-width="1.5" stroke-linecap="round"/>

  <!-- Layer 2: Expected Outcome (Calculated Projection) -->
  <rect x="45" y="88" width="290" height="44" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="57" y="100" width="20" height="20" rx="2" fill="#0B6E6E"/>
  <line x1="87" y1="106" x2="195" y2="106" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="87" y1="118" x2="260" y2="118" stroke="#4D5866" stroke-width="1.5" stroke-linecap="round"/>

  <!-- Layer 3: Your Result (Custom Calibration) -->
  <rect x="60" y="28" width="260" height="44" rx="4" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2" stroke-dasharray="6 3"/>
  <rect x="72" y="40" width="20" height="20" rx="2" fill="#C4572A"/>
  <line x1="102" y1="46" x2="210" y2="46" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="102" y1="58" x2="240" y2="58" stroke="#4D5866" stroke-width="1.5" stroke-linecap="round"/>
</svg>''',

    # 8. Diagram: Demo Data Lifecycle (Upload -> Process -> Delete 24h)
    'diagram-data-lifecycle.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 140" width="100%" height="100%" fill="none">
  <!-- Step 1: Upload (Restricted & Ephemeral) -->
  <rect x="24" y="32" width="96" height="76" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <polyline points="56,70 72,54 88,70" stroke="#0B6E6E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="72" y1="56" x2="72" y2="86" stroke="#0B6E6E" stroke-width="2.5" stroke-linecap="round"/>

  <!-- Arrow 1 -->
  <path d="M130 70 H 164" stroke="#0E1B2A" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="162,66 170,70 162,74" fill="#0E1B2A"/>

  <!-- Step 2: Isolated In-Memory Processing -->
  <rect x="180" y="32" width="100" height="76" rx="4" fill="#0E1B2A" stroke="#0E1B2A" stroke-width="2"/>
  <circle cx="230" cy="70" r="18" fill="#084F50" stroke="#FCFBF8" stroke-width="1.5"/>
  <polygon points="230,62 237,70 230,78 223,70" fill="#FCFBF8"/>

  <!-- Arrow 2 -->
  <path d="M290 70 H 324" stroke="#0E1B2A" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="322,66 330,70 322,74" fill="#0E1B2A"/>

  <!-- Step 3: Automated Purge after 24 Hours -->
  <rect x="340" y="32" width="96" height="76" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <circle cx="388" cy="70" r="18" fill="#ECE6D8" stroke="#C4572A" stroke-width="2"/>
  <line x1="380" y1="62" x2="396" y2="78" stroke="#C4572A" stroke-width="2" stroke-linecap="round"/>
  <line x1="396" y1="62" x2="380" y2="78" stroke="#C4572A" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    # 9. Diagram: Fiverr Order Flow
    'diagram-fiverr-flow.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 130" width="100%" height="100%" fill="none">
  <!-- Step 1: Brief on Fiverr -->
  <rect x="20" y="25" width="86" height="80" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="32" y="38" width="62" height="10" rx="2" fill="#0B6E6E"/>
  <line x1="32" y1="58" x2="80" y2="58" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="32" y1="72" x2="72" y2="72" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>

  <!-- Arrow 1 -->
  <path d="M116 65 H 144" stroke="#0E1B2A" stroke-width="2"/>
  <polygon points="142,61 150,65 142,69" fill="#0E1B2A"/>

  <!-- Step 2: Escrow & Buyer Protection -->
  <rect x="160" y="25" width="86" height="80" rx="4" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2"/>
  <path d="M203 45 L 217 52 V 65 C 217 73, 203 80, 203 80 C 203 80, 189 73, 189 65 V 52 Z" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>

  <!-- Arrow 2 -->
  <path d="M256 65 H 284" stroke="#0E1B2A" stroke-width="2"/>
  <polygon points="282,61 290,65 282,69" fill="#0E1B2A"/>

  <!-- Step 3: Milestone Delivery & Approval -->
  <rect x="300" y="25" width="86" height="80" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <polyline points="325,65 338,78 362,50" stroke="#1F7A4D" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>''',

    # 10. Diagram: Documents to Assistant to Answer (Hero Architecture Diagram)
    'diagram-doc-to-answer.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 280" width="100%" height="100%" fill="none">
  <!-- Background Canvas Frame -->
  <rect x="10" y="10" width="500" height="260" rx="8" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <!-- Top Bar / Window Controls -->
  <rect x="10" y="10" width="500" height="34" rx="8" fill="#ECE6D8"/>
  <circle cx="32" cy="27" r="4" fill="#0E1B2A"/>
  <circle cx="46" cy="27" r="4" fill="#0E1B2A"/>
  <circle cx="60" cy="27" r="4" fill="#0E1B2A"/>
  <line x1="10" y1="44" x2="510" y2="44" stroke="#0E1B2A" stroke-width="1.5"/>

  <!-- Left: Source Documents -->
  <rect x="36" y="74" width="100" height="140" rx="4" fill="#ECE6D8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="46" y="86" width="50" height="8" rx="2" fill="#0B6E6E"/>
  <line x1="46" y1="106" x2="116" y2="106" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="46" y1="122" x2="106" y2="122" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="46" y1="138" x2="112" y2="138" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="46" y1="154" x2="96" y2="154" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <rect x="46" y="174" width="44" height="18" rx="2" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="1.5"/>
  <text x="68" y="187" text-anchor="middle" font-family="'IBM Plex Mono', monospace" font-size="9" font-weight="600" fill="#0E1B2A">PDF / DOC</text>

  <!-- Flow 1 -->
  <path d="M148 144 H 194" stroke="#0E1B2A" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="192,140 200,144 192,148" fill="#0E1B2A"/>

  <!-- Center: Vector Index & Verification Core -->
  <rect x="210" y="84" width="100" height="120" rx="4" fill="#0E1B2A" stroke="#0E1B2A" stroke-width="2"/>
  <circle cx="260" cy="134" r="26" fill="#0B6E6E" stroke="#FCFBF8" stroke-width="2"/>
  <polygon points="260,120 272,134 260,148 248,134" fill="#FCFBF8"/>
  <rect x="224" y="174" width="72" height="14" rx="2" fill="#C4572A"/>
  <text x="260" y="184" text-anchor="middle" font-family="'IBM Plex Mono', monospace" font-size="8" font-weight="600" fill="#FCFBF8">RAG PIPELINE</text>

  <!-- Flow 2 -->
  <path d="M320 144 H 366" stroke="#0E1B2A" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="364,140 372,144 364,148" fill="#0E1B2A"/>

  <!-- Right: Verified Answer with Source Citation -->
  <rect x="376" y="74" width="108" height="140" rx="4" fill="#FCFBF8" stroke="#0E1B2A" stroke-width="2"/>
  <rect x="388" y="86" width="60" height="8" rx="2" fill="#1F7A4D"/>
  <line x1="388" y1="106" x2="464" y2="106" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="388" y1="120" x2="456" y2="120" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <line x1="388" y1="134" x2="460" y2="134" stroke="#0E1B2A" stroke-width="2" stroke-linecap="round"/>
  <!-- Citation Tag -->
  <rect x="388" y="156" width="74" height="20" rx="3" fill="#ECE6D8" stroke="#0B6E6E" stroke-width="1.5"/>
  <text x="425" y="170" text-anchor="middle" font-family="'IBM Plex Mono', monospace" font-size="8" font-weight="600" fill="#0B6E6E">&sect; 4.2 SOURCE REF</text>
  <polyline points="448,194 456,186 464,194" stroke="#1F7A4D" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    # 11. Pattern: Grid
    'pattern-grid.svg': '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
  <path d="M 32 0 L 0 0 0 32" fill="none" stroke="rgba(14, 27, 42, 0.05)" stroke-width="1"/>
</svg>''',

    # 12. Pattern: Dots
    'pattern-dots.svg': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <circle cx="2" cy="2" r="1" fill="rgba(14, 27, 42, 0.08)"/>
</svg>''',
}

def main():
    for filename, content in ILLUSTRATIONS.items():
        filepath = ILLUST_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created illustration: {filename}")
    print(f"Done! {len(ILLUSTRATIONS)} illustrations created in {ILLUST_DIR}")

if __name__ == '__main__':
    main()
