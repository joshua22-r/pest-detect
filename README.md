# BioGuard AI - Disease & Pest Detection Platform

An intelligent AI-powered detection system for diagnosing diseases, pests, and health issues in both plants and livestock.

## Features

### 🌿 Plant Disease Detection
- Detects fungal, bacterial, and viral plant diseases
- Identifies pest damage and infestations
- Provides treatment and prevention recommendations
- Supports all major crop and ornamental plants

### 🐄 Livestock Health Detection  
- Identifies common animal health conditions
- Detects pest infestations (ticks, mites, flies)
- Recognizes skin diseases and lesions
- Supports cattle, sheep, goats, horses, pigs, and poultry

### 📊 Features
- **Instant AI Analysis** - Get results in seconds
- **Confidence Scores** - Understand how confident the AI is
- **Severity Assessment** - Know how urgent the issue is
- **Detailed Recommendations** - Specific treatment and prevention steps
- **Scan History** - Keep records of all your detections
- **Export Data** - Download scans as CSV for records
- **Mobile Friendly** - Works on all devices
- **User Management** - Secure accounts with role-based access
- **Admin Dashboard** - Manage users and disease database

## Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript
- **UI Components**: shadcn/ui, Tailwind CSS
- **Authentication**: JWT-based auth system
- **State Management**: React Context + Custom Hooks
- **Icons**: Lucide React
- **Notifications**: Sonner Toast

## Getting Started

### Prerequisites
- Node.js 18+
- pnpm (package manager)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd bioguard-ai
```

2. Install dependencies
```bash
pnpm install
```

3. Set up environment variables
```bash
# Create .env.local file
cp .env.example .env.local
```

4. Run the development server
```bash
pnpm dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── app/                      # Next.js app directory
│   ├── page.tsx             # Home page
│   ├── predict/             # Detection page
│   ├── history/             # Scan history
│   ├── profile/             # User profile
│   ├── admin/               # Admin dashboard
│   ├── auth/                # Authentication pages
│   └── layout.tsx           # Root layout
├── components/              # Reusable components
│   ├── ui/                  # shadcn/ui components
│   ├── navbar.tsx           # Navigation bar
│   ├── image-upload.tsx     # Image upload component
│   ├── detection-results.tsx # Results display
│   └── ...
├── contexts/                # React contexts
│   └── auth-context.tsx     # Authentication context
├── lib/                     # Utilities and helpers
│   ├── api-client.ts       # API client
│   ├── auth.ts             # Auth utilities
│   ├── types.ts            # TypeScript types
│   └── ...
└── hooks/                   # Custom React hooks
    └── use-toast.ts        # Toast notifications
```

## Key Pages

### Home (`/`)
- Landing page with features overview
- Authentication links
- User dashboard (when logged in)

### Detect & Analyze (`/predict`)
- Choose between plant or livestock analysis
- Upload images via drag-drop, file browser, or camera
- Get instant AI analysis with treatment recommendations
- Save results to history

### History (`/history`)
- View all your detection scans
- Filter by type (plant/livestock), disease, or search
- View detailed scan information
- Delete or export scans
- Download as CSV

### Profile (`/profile`)
- Edit personal information
- Change password
- View account statistics
- Manage preferences

### Admin Dashboard (`/admin/dashboard`)
- System analytics
- User management
- Disease database management
- Scan statistics

## API Integration

The frontend is designed to work with a Django backend API. Update `NEXT_PUBLIC_API_URL` in your environment to point to your backend.

### Expected API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/detect/` - Submit image for analysis
- `GET /api/scans/` - Get user's scans
- `DELETE /api/scans/{id}` - Delete a scan
- `GET /api/admin/stats` - Get admin statistics

## Development

### Adding New Features

1. **New Page**
   - Create directory under `app/`
   - Add `page.tsx` and any needed components
   - Update navbar navigation if needed

2. **New Component**
   - Create in `components/` directory
   - Use TypeScript interfaces for props
   - Follow existing styling patterns

3. **New Types**
   - Add to `lib/types.ts`
   - Export for use across app

### Styling

- Uses Tailwind CSS v4 for styling
- Design tokens in `app/globals.css`
- Color scheme: Green (plants), Blue (livestock), Grays (neutral)
- Mobile-first responsive design

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=BioGuard AI
NEXT_PUBLIC_APP_DESCRIPTION=AI-Powered Disease Detection
```

## Building for Production

```bash
# Build the application
pnpm build

# Start production server
pnpm start
```

## Deployment

### Deploy to Vercel

1. Push code to GitHub
2. Import project to Vercel
3. Set environment variables in Vercel dashboard
4. Vercel auto-deploys on push

### Deploy to Other Platforms

The app is a standard Next.js application and can be deployed to:
- AWS (Amplify, EC2)
- Google Cloud (App Engine, Cloud Run)
- Azure (App Service)
- Heroku, DigitalOcean, or any Node.js host

## Performance Optimizations

- Next.js Image optimization
- Code splitting and lazy loading
- API request caching with SWR
- Optimized bundle size
- Mobile-first responsive design

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Common Issues

1. **Images not uploading**
   - Check file size (max 5MB)
   - Ensure supported format (JPG, PNG, WebP)
   - Check browser console for errors

2. **Auth not working**
   - Verify API URL is correct
   - Check network tab for API errors
   - Clear browser cache and try again

3. **Page not loading**
   - Check browser console for errors
   - Verify all dependencies are installed
   - Try hard refresh (Ctrl+Shift+R)

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Contact support team
- Check documentation in PUBLIC_GUIDE.md

## Credits

Built with:
- Next.js & React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide Icons

---

**BioGuard AI - Protecting Plants and Livestock with AI**
