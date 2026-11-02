"""
Draws HaggLab's site illustrations as SVG files in static/img/hagglab/.

Run:  python scripts/make_illustrations.py
All images are original, drawn here from simple shapes in the site's colours (tokens.css). They contain no words,
so they need no translation and stay sharp at any size. Edit a function and re-run to change one.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / 'static' / 'img' / 'hagglab'

# Colours from static/css/tokens.css
BG, CARD = '#F4F5F2', '#FFFFFF'
LINE, LINE2 = '#E2E5E1', '#C9CFCB'
INK, BAR = '#0E1A1C', '#D5DBD7'
ACC, SOFT, TINT = '#0E7568', '#CFE8E2', '#E5F1EE'
AMB, AMBT = '#A14A07', '#FBF0E4'
DOT = '#DCE1DD'


def svg(w, h, body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<defs>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{DOT}"/></pattern>
  <filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="{INK}" flood-opacity="0.09"/></filter>
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/>
<rect width="{w}" height="{h}" fill="url(#dots)"/>
{body}
</svg>
'''


def card(x, y, w, h, rx=12, fill=CARD, stroke=LINE, shadow=True):
    f = ' filter="url(#sh)"' if shadow else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"{f}/>'


def bar(x, y, w, color=BAR, h=7):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{color}"/>'


def window(x, y, w, h):
    """A browser or app window with a title bar."""
    return (card(x, y, w, h) +
            f'<path d="M{x} {y + 12}a12 12 0 0 1 12-12h{w - 24}a12 12 0 0 1 12 12v14h-{w}z" fill="{BG}"/>'
            f'<line x1="{x}" y1="{y + 26}" x2="{x + w}" y2="{y + 26}" stroke="{LINE}"/>' +
            ''.join(f'<circle cx="{x + 16 + i * 12}" cy="{y + 13}" r="3.5" fill="{LINE2}"/>' for i in range(3)))


def check(cx, cy, r=13, fill=ACC):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
            f'<path d="M{cx - r * 0.38} {cy}l{r * 0.26} {r * 0.27}l{r * 0.5}-{r * 0.55}" fill="none" stroke="#fff" '
            f'stroke-width="{max(2, r / 5):.1f}" stroke-linecap="round" stroke-linejoin="round"/>')


def arrow(x1, y, x2, color=ACC):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2 - 6}" y2="{y}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>'
            f'<path d="M{x2 - 10} {y - 6}l8 6-8 6" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- services (480 x 300)

def service_ai_chatbots():
    b = card(44, 58, 150, 190)  # source document
    b += bar(64, 82, 90, INK) + ''.join(bar(64, 104 + i * 18, w) for i, w in enumerate([108, 96, 104]))
    b += f'<rect x="58" y="154" width="122" height="22" rx="6" fill="{TINT}"/>' + bar(64, 161, 98, ACC)
    b += ''.join(bar(64, 190 + i * 18, w) for i, w in enumerate([100, 70]))
    b += window(222, 46, 216, 214)  # chat
    b += f'<rect x="300" y="88" width="122" height="34" rx="12" fill="{INK}"/>' + bar(314, 101, 80, '#5C6A6C')
    b += f'<rect x="238" y="138" width="166" height="66" rx="12" fill="{TINT}"/>'
    b += bar(252, 152, 132, ACC) + bar(252, 168, 110, SOFT) + bar(252, 184, 80, SOFT)
    b += f'<rect x="238" y="214" width="92" height="22" rx="11" fill="{CARD}" stroke="{ACC}"/>'
    b += f'<path d="M252 225h6m-6-4h10m-10 8h8" stroke="{ACC}" stroke-width="2" stroke-linecap="round"/>' + bar(270, 222, 46, SOFT, 6)
    b += f'<path d="M180 165 C 205 165, 210 225, 238 225" fill="none" stroke="{ACC}" stroke-width="2" stroke-dasharray="4 5"/>'
    return svg(480, 300, b, 'An assistant answering from your own document, with the source shown')


def service_saas_mvp():
    b = window(40, 34, 400, 232)
    b += f'<rect x="41" y="61" width="88" height="204" fill="{BG}"/>'
    b += ''.join(bar(56, 82 + i * 24, w, ACC if i == 0 else BAR) for i, w in enumerate([52, 44, 56, 40]))
    for i in range(3):  # stat tiles
        x = 148 + i * 94
        b += card(x, 78, 82, 52, 10, shadow=False) + bar(x + 12, 92, 34) + bar(x + 12, 108, 50, INK, 9)
    b += card(148, 144, 270, 104, 10, shadow=False)  # chart
    for i, h in enumerate([34, 52, 44, 76]):
        b += f'<rect x="{166 + i * 38}" y="{232 - h}" width="22" height="{h}" rx="4" fill="{ACC if i == 3 else SOFT}"/>'
    b += card(330, 168, 120, 108, 12)  # login card
    b += f'<circle cx="390" cy="194" r="12" fill="{TINT}"/><circle cx="390" cy="191" r="4.5" fill="{ACC}"/>'
    b += f'<path d="M382 202a8 8 0 0 1 16 0" fill="{ACC}"/>'
    b += f'<rect x="344" y="216" width="92" height="14" rx="5" fill="{BG}" stroke="{LINE}"/>'
    b += f'<rect x="344" y="240" width="92" height="20" rx="6" fill="{ACC}"/>'
    return svg(480, 300, b, 'A first version of a web app: dashboard, chart and login')


def service_nlp_ml():
    b = card(36, 50, 160, 200)  # messages sorted by label
    for i, (tag, fill, txt) in enumerate([(AMBT, AMB, 1), (TINT, ACC, 0), (TINT, ACC, 0), (BG, LINE2, 0)]):
        y = 68 + i * 44
        b += bar(52, y + 6, 74 if i % 2 else 86) + bar(52, y + 20, 56)
        b += f'<rect x="142" y="{y + 4}" width="38" height="20" rx="6" fill="{tag}" stroke="{fill}"/>'
    b += card(214, 50, 230, 200)  # forecast chart
    b += f'<line x1="236" y1="222" x2="426" y2="222" stroke="{LINE2}"/><line x1="236" y1="72" x2="236" y2="222" stroke="{LINE2}"/>'
    b += f'<path d="M330 140 L 380 112 L 426 96 L 426 150 L 380 152 L 330 150 Z" fill="{SOFT}" opacity="0.8"/>'
    b += f'<polyline points="242,196 266,180 290,186 312,160 330,145" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
    b += f'<polyline points="330,145 380,132 426,122" fill="none" stroke="{ACC}" stroke-width="3" stroke-dasharray="7 6" stroke-linecap="round"/>'
    b += f'<line x1="330" y1="72" x2="330" y2="222" stroke="{LINE2}" stroke-dasharray="3 4"/><circle cx="330" cy="145" r="5" fill="{ACC}"/>'
    return svg(480, 300, b, 'Messages sorted by label, and a forecast with its error range')


def service_python_automation():
    b = ''
    for i in range(3):  # input files
        x, y = 40 + i * 12, 70 + i * 14
        b += card(x, y, 86, 108, 10)
        b += f'<path d="M{x + 62} {y}v18h24" fill="{BG}" stroke="{LINE}"/>'
        b += ''.join(bar(x + 14, y + 36 + j * 16, w) for j, w in enumerate([52, 40, 56]))
    b += arrow(150, 150, 196)
    b += f'<circle cx="240" cy="150" r="40" fill="{ACC}" filter="url(#sh)"/>'  # the program (gear)
    teeth = ''.join(f'<rect x="234" y="114" width="12" height="16" rx="3" fill="{CARD}" transform="rotate({a} 240 150)"/>' for a in range(0, 360, 45))
    b += teeth + f'<circle cx="240" cy="150" r="20" fill="{CARD}"/><circle cx="240" cy="150" r="8" fill="{ACC}"/>'
    b += arrow(286, 150, 330)
    b += card(338, 64, 108, 172)  # report
    b += bar(354, 84, 60, INK)
    for i, h in enumerate([30, 46, 38, 58]):
        b += f'<rect x="{356 + i * 20}" y="{176 - h}" width="13" height="{h}" rx="3" fill="{ACC if i == 3 else SOFT}"/>'
    b += bar(354, 192, 76) + bar(354, 208, 54)
    b += check(440, 72, 15)
    return svg(480, 300, b, 'Files go through a Python program and come out as a finished report')


def service_ai_integration():
    b = window(36, 70, 190, 160)  # the client's existing app
    b += ''.join(bar(54, 116 + i * 18, w) for i, w in enumerate([120, 96, 132]))
    b += f'<rect x="52" y="178" width="158" height="36" rx="10" fill="{TINT}" stroke="{ACC}"/>'
    b += f'<path d="M66 196l6-6 6 6-6 6z" fill="{ACC}"/>' + bar(86, 193, 100, ACC)
    nodes = [(392, 78, AMB, AMBT), (392, 150, ACC, TINT), (392, 222, LINE2, CARD)]
    for i, (x, y, c, f) in enumerate(nodes):  # three AI providers, in order
        dash = ' stroke-dasharray="5 6"' if i != 1 else ''
        b += f'<path d="M226 196 C 300 196, 300 {y}, {x - 30} {y}" fill="none" stroke="{c}" stroke-width="{3 if i == 1 else 2}"{dash}/>'
        b += f'<circle cx="{x}" cy="{y}" r="28" fill="{f}" stroke="{c}" stroke-width="2" filter="url(#sh)"/>'
    b += f'<path d="M384 70l16 16m0-16l-16 16" stroke="{AMB}" stroke-width="3" stroke-linecap="round"/>'
    b += check(392, 150, 13)
    b += ''.join(f'<circle cx="{384 + k * 8}" cy="222" r="2.5" fill="{LINE2}"/>' for k in range(3))
    return svg(480, 300, b, 'Your app with AI added: when one provider fails it switches to the next')


# ---------------------------------------------------------------- pages (480 x 300)

def about_studio():
    b = window(56, 40, 210, 150)  # a chat tool
    b += f'<rect x="146" y="80" width="100" height="24" rx="10" fill="{INK}"/>' + f'<rect x="74" y="114" width="140" height="44" rx="10" fill="{TINT}"/>'
    b += bar(86, 126, 104, ACC) + bar(86, 142, 70, SOFT)
    b += card(206, 108, 210, 150)  # a chart
    for i, h in enumerate([40, 64, 52, 86, 74]):
        b += f'<rect x="{230 + i * 36}" y="{236 - h}" width="22" height="{h}" rx="5" fill="{ACC if i == 3 else SOFT}"/>'
    b += card(306, 30, 136, 92)  # code
    b += f'<path d="M332 62l-12 12 12 12m28-24l12 12-12 12" fill="none" stroke="{ACC}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
    b += f'<path d="M350 58l-8 32" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>' + bar(390, 66, 34) + bar(390, 82, 26)
    b += check(426, 252, 16)
    return svg(480, 300, b, 'A chat assistant, a chart and code: the kinds of tools we build')


def security_data():
    b = f'<path d="M240 40 L 320 70 V 150 C 320 205, 284 240, 240 258 C 196 240, 160 205, 160 150 V 70 Z" fill="{ACC}" filter="url(#sh)"/>'
    b += f'<path d="M240 58 L 304 82 V 150 C 304 196, 276 226, 240 240 Z" fill="#fff" opacity="0.12"/>'
    b += f'<rect x="214" y="138" width="52" height="44" rx="8" fill="{CARD}"/>'
    b += f'<path d="M224 138v-12a16 16 0 0 1 32 0v12" fill="none" stroke="{CARD}" stroke-width="7"/>'
    b += f'<circle cx="240" cy="156" r="6" fill="{ACC}"/><rect x="237.5" y="158" width="5" height="12" rx="2" fill="{ACC}"/>'
    b += card(40, 88, 96, 124, 10)  # document with hidden values
    b += bar(54, 108, 52, INK) + bar(54, 128, 64) + f'<rect x="54" y="146" width="66" height="10" rx="3" fill="{INK}"/>'
    b += bar(54, 166, 50) + f'<rect x="54" y="184" width="44" height="10" rx="3" fill="{INK}"/>'
    b += card(344, 96, 96, 108, 10)  # server
    for i in range(3):
        b += f'<rect x="356" y="{110 + i * 30}" width="72" height="20" rx="5" fill="{BG}" stroke="{LINE}"/><circle cx="416" cy="{120 + i * 30}" r="3.5" fill="{ACC}"/>'
    b += f'<path d="M136 150h24m160 0h24" stroke="{LINE2}" stroke-width="2" stroke-dasharray="4 5"/>'
    return svg(480, 300, b, 'A shield with a lock between your documents and the server')


def start_project():
    b = card(48, 54, 176, 196)  # your message
    b += bar(66, 76, 70, INK) + f'<rect x="66" y="96" width="140" height="74" rx="8" fill="{BG}" stroke="{LINE}"/>'
    b += ''.join(bar(78, 110 + i * 16, w) for i, w in enumerate([108, 90, 100]))
    b += f'<rect x="66" y="184" width="140" height="22" rx="7" fill="{TINT}" stroke="{ACC}"/>' + bar(78, 191, 60, ACC)
    b += f'<rect x="66" y="218" width="80" height="20" rx="7" fill="{ACC}"/>'
    b += arrow(236, 152, 276)
    b += card(286, 40, 150, 220)  # the one-page scope
    b += bar(304, 62, 82, INK)
    for i in range(4):
        y = 92 + i * 34
        b += check(314, y + 4, 9, ACC if i < 3 else LINE2) + bar(332, y, 80 - (i % 2) * 18)
    b += bar(304, 232, 60, SOFT)
    return svg(480, 300, b, 'Your message becomes a one-page scope with what is included')


# ---------------------------------------------------------------- process steps (320 x 200)

def step_tell():
    b = card(56, 40, 180, 100, 16)
    b += f'<path d="M96 140l-14 26 36-26z" fill="{CARD}" stroke="{LINE}"/><path d="M90 139h34" stroke="{CARD}" stroke-width="3"/>'
    b += bar(78, 64, 130) + bar(78, 82, 110)
    b += f'<rect x="72" y="98" width="98" height="24" rx="8" fill="{TINT}" stroke="{ACC}"/>' + bar(84, 106, 64, ACC)
    b += f'<circle cx="250" cy="120" r="26" fill="{ACC}" filter="url(#sh)"/><path d="M240 120h20m-8-8l8 8-8 8" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    return svg(320, 200, b, 'Tell us the problem and one starting number')


def step_scope():
    b = card(104, 24, 120, 156, 12)
    b += bar(120, 44, 64, INK)
    for i in range(3):
        b += check(127, 76 + i * 30, 8) + bar(142, 72 + i * 30, 58 - i * 8)
    b += f'<path d="M150 160c10-12 18 6 28-6s14 4 24-4" fill="none" stroke="{ACC}" stroke-width="2.5" stroke-linecap="round"/>'
    return svg(320, 200, b, 'A one-page scope you agree before you pay')


def step_grow():
    b = window(56, 30, 208, 140)
    b += f'<circle cx="160" cy="98" r="28" fill="{TINT}" stroke="{ACC}" stroke-width="2"/><path d="M152 84l22 14-22 14z" fill="{ACC}"/>'
    for i in range(4):
        b += f'<rect x="{80 + i * 42}" y="146" width="32" height="8" rx="4" fill="{ACC if i < 3 else LINE}"/>'
    return svg(320, 200, b, 'A working demo every week')


def step_handover():
    b = card(70, 56, 140, 110, 12)
    b += f'<path d="M70 80h140" stroke="{LINE}"/><path d="M70 68a12 12 0 0 1 12-12h40l12 12" fill="{BG}" stroke="{LINE}"/>'
    b += f'<path d="M116 104l-14 12 14 12m40-24l14 12-14 12" fill="none" stroke="{ACC}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
    b += f'<circle cx="236" cy="128" r="22" fill="{ACC}" filter="url(#sh)"/><circle cx="230" cy="128" r="7" fill="none" stroke="#fff" stroke-width="3"/>'
    b += f'<path d="M237 128h12m-4 0v6" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
    return svg(320, 200, b, 'You get the code, the keys and a handover guide')


IMAGES = {
    'service-ai-chatbots': service_ai_chatbots,
    'service-saas-mvp': service_saas_mvp,
    'service-nlp-ml': service_nlp_ml,
    'service-python-automation': service_python_automation,
    'service-ai-integration': service_ai_integration,
    'about-studio': about_studio,
    'security-data': security_data,
    'start-project': start_project,
    'step-1-tell': step_tell,
    'step-2-scope': step_scope,
    'step-3-grow': step_grow,
    'step-4-handover': step_handover,
}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name, draw in IMAGES.items():
        (OUT / f'{name}.svg').write_text(draw(), encoding='utf-8')
    print(f'{len(IMAGES)} images written to {OUT}')
