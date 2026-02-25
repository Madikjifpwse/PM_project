# PM_project
CityGuard: Institutional Incident Management System
CityGuard is a large-scale information system designed to manage urban infrastructure incidents (leaks, accidents, power outages) and coordinate emergency responses within a structured institutional framework.

👥 Team Members & Roles

Adil Izbassar (Project Manager / Analyst): Responsible for system framing, stakeholder analysis, institutional constraints definition, and ER diagram design.

Madikhan Madiyar (Backend Developer): Responsible for API architecture using FastAPI, H3 spatial indexing integration, RBAC implementation, and audit logging logic.

🏛️ Institutional Problem & Solution
Standard incident reporting often lacks spatial coordination and accountability. CityGuard solves this by:

Spatial Indexing: Using Uber’s H3 grid to partition the city into manageable hexagonal zones.

Accountability: Implementing mandatory Audit Logs for every critical action taken by officials.

Role-Based Control: Ensuring that only authorized dispatchers can resolve incidents, preventing conflict of interest.

🛠️ Tech Stack
Framework: FastAPI (Python)

Geospatial Library: H3-py

Data Validation: Pydantic

Documentation: Swagger UI (OpenAPI)

⬢ How H3 is Used
H3 is the core of our spatial data modeling. Instead of relying on traditional slow geometric calculations (Lat/Lng radius searches), we convert every incident's coordinates into an H3 Cell Index (Resolution 8).

Efficiency: It allows the system to group incidents by "hexagons" instantly.

Dispatching: Dispatchers are assigned to specific H3 cells, ensuring local expertise and faster response.

Analytics: The system can heat-map urban problem areas by aggregating incident counts per H3 cell.

🔐 Security & Constraints
RBAC (Role-Based Access Control):

Citizen: Can report incidents.

Dispatcher: Can view and resolve incidents.

Admin: Full access, including viewing Audit Logs.

Audit Logging: Every status change is recorded with a timestamp and User ID to ensure institutional transparency.

Event-Driven Component: The system uses asynchronous BackgroundTasks to log actions and trigger notifications without blocking the main API response.

🚀 How to Run
Install dependencies:

pip install fastapi uvicorn h3 pydantic
Navigate to the project directory:

cd CityGuard
Start the server:

python -m uvicorn main:app --reload
Access Documentation:
Open http://127.0.0.1:8000/docs to interact with the API via Swagger UI.
