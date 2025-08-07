# Angular Chatbot Application

A modern Angular-based chatbot application with a clean and responsive user interface.

## Features

- **Modern UI**: Clean and responsive design
- **Real-time Chat**: Interactive chat interface
- **Component-based Architecture**: Modular Angular components
- **TypeScript**: Full TypeScript support
- **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

```bash
npm install
```

### Development Server

```bash
ng serve
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

### Build

```bash
ng build
```

The build artifacts will be stored in the `dist/` directory.

### Running Unit Tests

```bash
ng test
```

### Running End-to-End Tests

```bash
ng e2e
```

## Project Structure

```
src/
├── app/
│   ├── components/
│   │   ├── chat-messages/     # Chat message display component
│   │   ├── header/            # Header component
│   │   └── message-input/     # Message input component
│   ├── services/
│   │   ├── chat.ts           # Chat service
│   │   └── screenshot.ts     # Screenshot service
│   └── app.component.ts      # Main app component
├── assets/                   # Static assets
└── styles.css               # Global styles
```

## Components

### Chat Messages Component
Displays the conversation history with support for different message types.

### Header Component
Application header with title and navigation.

### Message Input Component
Input field for user messages with send functionality.

## Services

### Chat Service
Handles chat functionality and message management.

### Screenshot Service
Manages screenshot capture and processing.

## Technologies Used

- **Angular**: Frontend framework
- **TypeScript**: Programming language
- **CSS**: Styling
- **HTML**: Markup

## Development

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 17.0.0.

## License

This project is licensed under the MIT License.
