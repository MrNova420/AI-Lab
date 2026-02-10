"""
Project Templates - Like Copilot/Claude Project Creation
Create complete project structures from templates
"""

from typing import Dict, Any


# Project templates that can be created anywhere
PROJECT_TEMPLATES = {
    "python-cli": {
        "name": "Python CLI Application",
        "dirs": [
            "src",
            "tests",
            "docs"
        ],
        "files": {
            "README.md": """# Python CLI Application

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python src/main.py
```
""",
            "requirements.txt": """click
requests
""",
            "src/main.py": """#!/usr/bin/env python3
\"\"\"Main CLI application entry point.\"\"\"

import click

@click.command()
@click.option('--name', default='World', help='Name to greet')
def main(name):
    \"\"\"Simple CLI application.\"\"\"
    click.echo(f'Hello, {name}!')

if __name__ == '__main__':
    main()
""",
            "src/__init__.py": "",
            "tests/__init__.py": "",
            "tests/test_main.py": """import pytest
from src.main import main

def test_main():
    # Add your tests here
    pass
""",
            ".gitignore": """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
.pytest_cache/
"""
        }
    },
    
    "python-api": {
        "name": "Python Flask API",
        "dirs": [
            "app",
            "app/routes",
            "app/models",
            "tests",
            "config"
        ],
        "files": {
            "README.md": """# Python Flask API

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
python run.py
```

## Test
```bash
pytest
```
""",
            "requirements.txt": """flask
flask-cors
python-dotenv
pytest
""",
            "run.py": """from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
""",
            "app/__init__.py": """from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    from app.routes import api
    app.register_blueprint(api.bp)
    
    return app
""",
            "app/routes/__init__.py": "",
            "app/routes/api.py": """from flask import Blueprint, jsonify

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@bp.route('/hello/<name>', methods=['GET'])
def hello(name):
    return jsonify({'message': f'Hello, {name}!'})
""",
            "app/models/__init__.py": "",
            ".env": """FLASK_ENV=development
FLASK_APP=run.py
""",
            ".gitignore": """__pycache__/
*.py[cod]
venv/
.env
"""
        }
    },
    
    "nodejs-app": {
        "name": "Node.js Application",
        "dirs": [
            "src",
            "tests",
            "public"
        ],
        "files": {
            "README.md": """# Node.js Application

## Install
```bash
npm install
```

## Run
```bash
npm start
```
""",
            "package.json": """{
  "name": "nodejs-app",
  "version": "1.0.0",
  "description": "Node.js application",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
""",
            "src/index.js": """const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Hello World!' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
""",
            ".gitignore": """node_modules/
.env
*.log
"""
        }
    },
    
    "react-app": {
        "name": "React Application",
        "dirs": [
            "src",
            "src/components",
            "public"
        ],
        "files": {
            "README.md": """# React Application

Created with template.

## Setup
```bash
npm install
```

## Run
```bash
npm start
```
""",
            "package.json": """{
  "name": "react-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}
""",
            "src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
""",
            "src/App.js": """import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>Hello React!</h1>
    </div>
  );
}

export default App;
""",
            "public/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>React App</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
""",
            ".gitignore": """node_modules/
build/
.env
"""
        }
    },
    
    "html-website": {
        "name": "Static HTML Website",
        "dirs": [
            "css",
            "js",
            "images"
        ],
        "files": {
            "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Website</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>Welcome to My Website</h1>
    </header>
    <main>
        <p>This is a simple static website.</p>
    </main>
    <script src="js/main.js"></script>
</body>
</html>
""",
            "css/style.css": """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
}

header {
    background: #333;
    color: #fff;
    padding: 1rem;
    text-align: center;
}

main {
    padding: 2rem;
}
""",
            "js/main.js": """console.log('Website loaded');
""",
            "README.md": """# Static Website

Open index.html in a browser to view.
"""
        }
    }
}


def get_template(template_name: str) -> Dict[str, Any]:
    """Get a project template by name."""
    return PROJECT_TEMPLATES.get(template_name)


def list_templates() -> Dict[str, Any]:
    """List all available templates."""
    return {
        template_name: info["name"]
        for template_name, info in PROJECT_TEMPLATES.items()
    }


def create_project_from_template(template_name: str, project_path: str) -> Dict[str, Any]:
    """
    Create a complete project from a template.
    
    Args:
        template_name: Name of the template to use
        project_path: Where to create the project
        
    Returns:
        Dictionary with creation status
    """
    template = get_template(template_name)
    
    if not template:
        return {
            "success": False,
            "error": f"Template '{template_name}' not found",
            "available_templates": list(PROJECT_TEMPLATES.keys())
        }
    
    from tools.filesystem.full_access import create_project_structure
    
    result = create_project_structure(project_path, template)
    
    if result.get("success"):
        result["template"] = template_name
        result["template_name"] = template["name"]
    
    return result
