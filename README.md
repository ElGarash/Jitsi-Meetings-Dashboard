# Meetings 

![continuous deployment status](https://github.com/elgarash/meetings/actions/workflows/continuous-deployment.yml/badge.svg)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads)

A serverless meetings application with a dashboard hosted on GitHub Pages.

## Technology stack

- **Azure Functions**
- **SQLAlchemy**
- **PyGitHub**
- [**sql.js-httpvfs**](https://github.com/phiresky/sql.js-httpvfs)
- **Auth0**

## How it works

The application uses [**Jitsi**](https://github.com/jitsi/jitsi-meet) IFrame API to perform the following functions:

- Start meetings and manage concurrent meeting rooms.
- Send meeting's participants and labels data to the database using the Azure function API.
- Stream the meeting on YouTube.

The backend is an Azure Function App written in Python used to perform CRUD operations on the database by cloning it, performing the database operation, then pushing it again to GitHub.

Backend uses **PyGitHub** library which is used to access the GitHub REST API, and **SQLAlchemy** as an ORM for the database.

GitHub Pages uses **sql.js-httpvfs** which is used to perform SQL queries to read from the database hosted at GitHub Pages.

Any requests to the API must be authorized, authentication is performed with [**Auth0**](https://auth0.com).

## Backend API Documentation

The documentation report is generated with [ScanAPI](https://github.com/scanapi/scanapi) library and the report can be found [here](https://refined-github-html-preview.kidonng.workers.dev/ElGarash/meetings/raw/functions-documentation/docs/scanapi-report.html).
![Function Endpoints](/docs/images/api-documentation.png)
