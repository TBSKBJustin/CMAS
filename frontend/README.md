# Church Media Automation System - Frontend

Modern React-based web interface for managing church media workflows.

## Features

- 📊 Dashboard with system status and recent events
- 📅 Event management (create, view, edit)
- 🔧 Dependency checker and installer
- ⚙️ Workflow configuration
- 📈 Real-time progress tracking

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **TanStack Query** - Data fetching
- **Lucide React** - Icons

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   └── Layout.jsx
│   ├── pages/           # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Events.jsx
│   │   ├── EventCreate.jsx
│   │   ├── EventDetail.jsx
│   │   ├── Dependencies.jsx
│   │   └── Settings.jsx
│   ├── api.js           # API client
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## API Integration

The frontend communicates with the FastAPI server (default: http://localhost:5000) via REST endpoints:

- `GET /api/events` - List all events
- `POST /api/events` - Create new event
- `GET /api/events/:id` - Get event details
- `POST /api/events/:id/run` - Run workflow
- `GET /api/dependencies` - Check dependencies
- `POST /api/dependencies/:key/install` - Install dependency

## Customization

### Branding

Edit `src/components/Layout.jsx` to customize the header and navigation.

### Theme Colors

Modify `tailwind.config.js` to adjust the color scheme.

### Additional Pages

1. Create new page in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation item in `src/components/Layout.jsx`

## Building for Production

```bash
npm run build
```

Outputs to `dist/` directory. Serve with any static file server or integrate with Flask:

```python
# In api_server.py
from flask import send_from_directory

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(f'frontend/dist/{path}'):
        return send_from_directory('frontend/dist', path)
    return send_from_directory('frontend/dist', 'index.html')
```

## Troubleshooting

### Port conflict
Edit `vite.config.js` to change the development port.

### API connection errors
Verify the API server is running and the proxy configuration in `vite.config.js` is correct.

### Build errors
Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```
