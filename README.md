


Requirements:
- Node.js >= 20 (https://nodejs.org)
- Python 3.11+

Setup Instructions: (bash)
cd backend
pip install -r requirements.txt
python seed.py
python main.py

cd frontend
npm install
npm run dev

The backend runs at http://localhost:8000
Interactive API docs are available at http://localhost:8000/docs

Auth note:
The /auth/session endpoint is simulated for demo purposes. It accepts a role
(GP, PHYSIO, DIETITIAN, or PSYCHOLOGIST) and returns the first practitioner in
the database matching that role. In production this would validate a JWT and
return the authenticated user.