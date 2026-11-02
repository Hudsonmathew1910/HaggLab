"""
MVPStarter: a small client request portal for FixRight Home Services (sample company).

It shows what a first version of a web app does: two user roles, records saved per account, a status
workflow with rules, and a dashboard. No AI is needed.
Each visitor gets a private copy kept in their session, so nothing they type is shown to anyone else,
and it is gone when the session ends.
"""
SESSION_KEY = 'mvpstarter'
JOB_TYPES = {
    'plumbing': 'Plumbing',
    'electrical': 'Electrical',
    'cleaning': 'Deep cleaning',
    'painting': 'Painting',
}
ROLES = {'customer': 'Customer', 'staff': 'Office staff'}
STEPS = ['New', 'Quoted', 'Scheduled', 'Done']
MAX_REQUESTS = 20  # per visitor, keeps the session small
SOURCE = 'FixRight Home Services (sample company). Your requests are private to you and reset when your visit ends.'


class WorkflowError(ValueError):
    """A visitor-facing problem, such as a role that is not allowed to do something."""


def starting_state():
    """Requests from other (sample) customers, so the staff view is not empty."""
    return {'next_id': 104, 'requests': [
        {'id': 101, 'mine': False, 'customer': 'Priya S.', 'job': 'plumbing',
         'details': 'Kitchen tap leaks under the sink.', 'step': 1},
        {'id': 102, 'mine': False, 'customer': 'Tom R.', 'job': 'cleaning',
         'details': 'End-of-lease clean, two-bedroom flat.', 'step': 2},
        {'id': 103, 'mine': False, 'customer': 'Grace L.', 'job': 'electrical',
         'details': 'Two sockets in the office stopped working.', 'step': 0},
    ]}


def visible(state, role):
    """Customers see only their own requests; staff see every request."""
    return [r for r in state['requests'] if role == 'staff' or r['mine']]


def dashboard(state, role, message):
    rows = visible(state, role)
    labels = [f'Signed in as: {ROLES[role]}']
    labels += [f'{step}: {sum(1 for r in rows if STEPS[r["step"]] == step)}' for step in STEPS]
    reply = {'text': message, 'labels': labels, 'source': SOURCE}
    if rows:
        reply['table'] = {
            # Status before the long details, so it stays in view on a phone
            'columns': ['#', 'Customer', 'Job', 'Status', 'Details'],
            'rows': [[r['id'], 'You' if r['mine'] else r['customer'], JOB_TYPES[r['job']], STEPS[r['step']],
                      r['details']] for r in rows],
        }
    return reply


def submit(state, role, job, details):
    if role != 'customer':
        raise WorkflowError('Requests are submitted by customers. Switch the role to Customer to add one.')
    if not details:
        raise WorkflowError('Please describe the job in a few words.')
    if sum(1 for r in state['requests'] if r['mine']) >= MAX_REQUESTS:
        raise WorkflowError(f'This sample account is full ({MAX_REQUESTS} requests). Choose "Start over" to reset it.')
    request_id = state['next_id']
    state['requests'].append({'id': request_id, 'mine': True, 'customer': 'You', 'job': job,
                              'details': details, 'step': 0})
    state['next_id'] += 1
    return f'Request #{request_id} saved with status New. Switch the role to Office staff to quote and schedule it.'


def advance(state, role, request_id):
    if role != 'staff':
        raise WorkflowError('Only office staff can change a status. Switch the role to Office staff.')
    if not request_id:
        raise WorkflowError('Please enter the request number, for example 103.')
    request = next((r for r in state['requests'] if r['id'] == request_id), None)
    if not request:
        raise WorkflowError(f'There is no request #{request_id}. Check the number in the table.')
    if request['step'] == len(STEPS) - 1:
        raise WorkflowError(f'Request #{request_id} is already Done.')
    request['step'] += 1
    step = STEPS[request['step']]
    note = ' In the real system the customer would now get an email.' if request['mine'] else ''
    return f'Request #{request_id} moved to {step}.{note}'


def run(payload, session):
    role = payload.get('role', 'customer')
    action = payload.get('action', 'view')
    if action == 'reset' or SESSION_KEY not in session:
        session[SESSION_KEY] = starting_state()
    state = session[SESSION_KEY]

    if action == 'submit':
        message = submit(state, role, payload.get('job', 'plumbing'), payload.get('details', ''))
    elif action == 'advance':
        message = advance(state, role, payload.get('request_id'))
    elif action == 'reset':
        message = 'Started over with the sample requests.'
    else:
        message = ('All requests, newest last.' if role == 'staff'
                   else 'Your requests. Customers see only their own; staff see everyone\'s.')
    session[SESSION_KEY] = state  # reassign so the session is saved
    return dashboard(state, role, message)
