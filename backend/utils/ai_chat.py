import re
import os
from models import db
from openai import OpenAI

client = None


def get_client():
    global client
    if client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('OPENAI_API_KEY environment variable is not set')
        client = OpenAI(api_key=api_key)
    return client


SCHEMA_DESCRIPTION = """
You are a SQL query generator for a PostgreSQL database with these tables:

TABLE: worker
- id (INTEGER, primary key)
- name (VARCHAR(80), not null)
- phone (VARCHAR(80), not null)
- email (VARCHAR(80), not null)
- role (VARCHAR(50), nullable) -- e.g. 'driver', 'mechanic'
- "givingServiceTo" (VARCHAR(50), nullable) -- company/fleet being serviced
- is_active (BOOLEAN, default true)

TABLE: vehicle
- id (INTEGER, primary key)
- driver_id (INTEGER, foreign key -> worker.id)
- make (VARCHAR(80), not null) -- e.g. 'Toyota'
- model (VARCHAR(80), not null) -- e.g. 'Camry'
- plate (VARCHAR(80), not null)
- year (INTEGER, not null)

TABLE: reminder
- id (INTEGER, primary key)
- assigned_worker_id (INTEGER, foreign key -> worker.id, not null)
- vehicle_id (INTEGER, foreign key -> vehicle.id, nullable)
- reminder_type (VARCHAR(50), not null) -- e.g. 'oil_change', 'inspection'
- scheduled_date (DATE, not null)
- message (TEXT, not null)
- status (VARCHAR(20), default 'pending') -- 'pending', 'sent', 'completed'
- sent_at (TIMESTAMP, nullable)
- completed_at (TIMESTAMP, nullable)
- created_at (TIMESTAMP, default now)

TABLE: task_event
- id (INTEGER, primary key)
- reminder_id (INTEGER, foreign key -> reminder.id)
- worker_id (INTEGER, foreign key -> worker.id)
- event_type (VARCHAR(30)) -- 'created', 'sent', 'completed', 'overdue'
- occurred_at (TIMESTAMP, default now)
- notes (TEXT, nullable)

IMPORTANT RULES:
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, or any other modifying statement.
- Use double quotes for the column "givingServiceTo" since it has mixed case.
- Return ONLY the SQL query, nothing else. No markdown, no explanation.
- Limit results to 100 rows maximum.
"""


def generate_sql(question):
    """Send the schema + user question to OpenAI, get back a SQL query."""
    ai = get_client()
    response = ai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': SCHEMA_DESCRIPTION},
            {'role': 'user', 'content': question},
        ],
        temperature=0,
        max_tokens=500,
    )
    sql = response.choices[0].message.content.strip()
    # Remove markdown code fences if present
    sql = re.sub(r'^```(?:sql)?\s*', '', sql)
    sql = re.sub(r'\s*```$', '', sql)
    return sql.strip()


def validate_query(sql):
    """Ensure the query is read-only."""
    normalized = sql.strip().upper()
    if not normalized.startswith('SELECT'):
        return False
    forbidden = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']
    for word in forbidden:
        if re.search(r'\b' + word + r'\b', normalized):
            return False
    return True


def execute_safe_query(sql):
    """Execute a validated read-only query and return the results."""
    if not validate_query(sql):
        raise ValueError('Query is not a safe SELECT statement')

    result = db.session.execute(db.text(sql))
    columns = list(result.keys())
    rows = [dict(zip(columns, row)) for row in result.fetchmany(100)]
    return columns, rows


def format_answer(question, columns, rows):
    """Send query results back to LLM to produce a human-readable answer."""
    ai = get_client()

    if not rows:
        result_text = 'The query returned no results.'
    else:
        result_text = f'Columns: {columns}\nRows ({len(rows)} results):\n'
        for row in rows[:20]:
            result_text += str(row) + '\n'
        if len(rows) > 20:
            result_text += f'... and {len(rows) - 20} more rows'

    response = ai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'system',
                'content': 'You are a helpful assistant. The user asked a question about their business data. '
                           'Based on the SQL query results below, provide a clear, concise answer. '
                           'Format numbers nicely. Use bullet points for lists. Be brief.'
            },
            {
                'role': 'user',
                'content': f'Question: {question}\n\nQuery results:\n{result_text}'
            },
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
