# Proxy Manager Frontend

Production-ready React + TypeScript frontend for the Proxy Manager FastAPI application.

## Features

- 🔐 Authentication (JWT-based login/register)
- 👤 User area: View proxies, get proxy, view logs
- 🔧 Admin area: Manage proxies, users, blacklist, view all logs
- 🎨 Tron Legacy inspired theme (neon cyan/magenta on dark background)
- ♿ Accessible (keyboard navigation, ARIA attributes)
- 📱 Responsive design
- 🧪 Comprehensive testing (Vitest + Playwright)

## Tech Stack

- React 18 + TypeScript
- Vite
- TailwindCSS
- React Router v6
- TanStack Query (React Query)
- TanStack Table
- React Hook Form + Zod
- Axios
- Recharts
- Vitest + React Testing Library
- Playwright

## Project Structure

```
.
├── client/
│   └── app/              # React SPA
├── packages/
│   ├── api/              # API client with typed OpenAPI integration
│   └── ui/               # Shared UI components
└── package.json          # Workspace root
```

## Setup

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Generate API types:
```bash
cd packages/api
npm run generate
cd ../..
```

3. Create environment file:
```bash
cp client/app/.env.example client/app/.env
```

4. Update `.env` with your API URL if needed:
```env
VITE_API_URL=http://localhost:8000
```

## Development

### Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build

```bash
npm run build
```

### Type Check

```bash
npm run type-check
```

### Lint

```bash
npm run lint
```

### Format

```bash
npm run format
```

## Testing

### Unit Tests

```bash
npm run test:unit
```

### E2E Tests

```bash
npm run test:e2e
```

### All Tests

```bash
npm test
```

## Deployment

### Environment Variables

- `VITE_API_URL`: API base URL (default: http://localhost:8000)
- `NODE_ENV`: Environment (development/production)

### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel`
3. Set environment variables in Vercel dashboard

### Netlify

1. Install Netlify CLI: `npm i -g netlify-cli`
2. Build: `npm run build`
3. Deploy: `netlify deploy --prod --dir=client/app/dist`
4. Set environment variables in Netlify dashboard

## Routes

### Public
- `/` - Redirects to `/app/proxies`
- `/login` - Login page
- `/register` - Registration page

### User Area (`/app/*`)
- `/app/proxies` - Proxy list
- `/app/proxies/:id` - Proxy details
- `/app/get-proxy` - Get proxy interface
- `/app/logs` - User logs

### Admin Area (`/admin/*`)
- `/admin/dashboard` - Admin dashboard
- `/admin/proxies` - Manage proxies
- `/admin/users` - Manage users
- `/admin/blacklist` - Manage blacklist rules
- `/admin/logs` - View all logs

## Authentication

- Access tokens are stored in memory
- Refresh tokens are stored in localStorage
- Automatic token refresh on 401 responses
- Protected routes require authentication
- Admin routes require admin role

## API Integration

The frontend uses the OpenAPI spec from `packages/api/openapi.json` to generate typed API clients. All API calls go through the Axios client in `packages/api/src/client.ts` which handles:

- Authentication headers
- Token refresh
- Error handling
- Request/response interceptors

## Theme

The Tron Legacy theme uses CSS variables defined in `packages/ui/src/theme.css`:

- `--bg: #020204` - Background
- `--panel: #071023` - Panel background
- `--neon-cyan: #00FFF7` - Primary accent
- `--neon-magenta: #FF00E1` - Secondary accent
- `--accent: #0FF0D8` - Accent color
- `--muted: #6b7684` - Muted text

## Accessibility

- Keyboard navigation for all interactive elements
- ARIA attributes on modals, forms, and tables
- Focus management (focus trap in modals)
- Screen reader support
- Sufficient color contrast (WCAG AA)

## License

MIT

