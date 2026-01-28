# MarketMind Pro Frontend

Professional React frontend for institutional financial analysis and reporting platform.

## Features

- **Professional UI Design** - Corporate styling with MarketMind Pro branding
- **Responsive Layout** - Works on desktop, tablet, and mobile devices
- **Print-Friendly** - Optimized CSS for professional report printing
- **Real-time Progress** - Live updates during report generation
- **Interactive Forms** - Clean, accessible form design
- **Loading States** - Professional animations and loading indicators
- **Corporate Colors** - Consistent brand colors (#1f4e79, #2e75b6)

## Components

### Header
- Professional branding with logo and navigation
- Corporate color scheme
- Responsive design

### StockForm
- Clean input form for stock symbol and options
- Real-time validation
- Loading states with animations
- Checkbox options for charts and tables

### ProgressTracker
- Step-by-step progress visualization
- Real-time status updates
- Professional animations
- Estimated completion times

### ReportDisplay
- Institutional report preview
- Download and print functionality
- Professional styling
- Report metadata display

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Styling

Built with Tailwind CSS and custom corporate styling:

- **Primary Colors**: #1f4e79 (dark blue), #2e75b6 (medium blue)
- **Typography**: Inter font family
- **Components**: Reusable button, card, and form styles
- **Animations**: Smooth transitions and loading states
- **Print Styles**: Professional PDF-ready formatting

## Print Functionality

The application includes comprehensive print styles for professional reports:

- Optimized typography for print
- Page break controls
- Corporate headers and footers
- Color-accurate printing
- Professional margins and spacing

## API Integration

Connects to MarketMind Pro backend API:

- `POST /api/v1/generate-report` - Start report generation
- `GET /api/v1/status/{job_id}` - Check generation status
- `GET /api/v1/download/{job_id}` - Download completed report

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

The application uses:
- React 18 with hooks
- Tailwind CSS for styling
- Heroicons for icons
- PostCSS for processing
- Professional animations and transitions