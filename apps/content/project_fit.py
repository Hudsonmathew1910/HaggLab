"""
Who each project suits ("Built for") and concrete scenarios ("Use cases").
These describe fit, not past clients. Real client counts go in Project.delivered_count.
The seed copies these into a project only while its fields are still blank, so admin edits win.
"""

PROJECT_FIT = {
    'documind': (
        'Clinics · Coaching centres · HR teams · Small offices',
        [
            'A clinic answers staff questions from its policy handbook, with the page shown.',
            'A coaching centre answers student questions about fees, leave and timetables.',
            'An HR team answers repeat questions about leave and expense rules.',
        ],
    ),
    'insightdesk': (
        'Retail shops · Restaurants · Distributors · Small finance teams',
        [
            'A shop owner asks which products sold best last month and gets the chart.',
            'A restaurant compares weekday and weekend orders without building a report.',
            'A distributor checks which region is behind target this quarter.',
        ],
    ),
    'shopassist': (
        'Online stores · Fashion and footwear · Electronics shops',
        [
            'A shopper describes what they need and gets matching products with links.',
            'A store answers size and stock questions at any hour.',
            'A small shop guides first-time visitors to the right category.',
        ],
    ),
    'bookit': (
        'Sports turfs · Salons · Clinics · Tutors and studios',
        [
            'A sports turf takes slot bookings online and stops double bookings.',
            'A salon lets customers pick a free time and confirms by email.',
            'A tutor shares one link for students to book sessions.',
        ],
    ),
    'supportflow': (
        'Online stores · Service businesses · Small support teams',
        [
            'A store sorts incoming messages so urgent ones are answered first.',
            'A service business gets a draft reply for each message, approved by a person.',
            'A small team sees which topics come up most each week.',
        ],
    ),
    'forecastboard': (
        'Retail shops · Cafes and restaurants · Wholesalers',
        [
            'A cafe estimates next week’s demand before ordering stock.',
            'A shop plans seasonal stock using past sales.',
            'A wholesaler sees the expected range, not just one number.',
        ],
    ),
    'voicedesk': (
        'Clinics · Hotels · Service businesses',
        [
            'A clinic answers opening-hours and booking questions after hours.',
            'A hotel answers common guest questions instantly.',
            'A service business takes a message when the answer needs a person.',
        ],
    ),
    'pagemind': (
        'Researchers · Sales teams · Content teams',
        [
            'A sales rep summarises a prospect’s website in three points.',
            'A researcher asks questions about a long article.',
            'A content team pulls the key facts from a page without copy-paste.',
        ],
    ),
    'deskpilot': (
        'Office teams · Accountants · Admin staff',
        [
            'An accountant renames and files invoice PDFs by date.',
            'An admin team moves weekly reports into the right folders.',
            'An office drafts routine emails from a short instruction.',
        ],
    ),
    'reportbot': (
        'Managers · Small finance teams · Agencies',
        [
            'A manager gets the weekly sales report without copying numbers.',
            'A finance team gets monthly totals with charts from one sheet.',
            'An agency sends each client a consistent weekly summary.',
        ],
    ),
}
