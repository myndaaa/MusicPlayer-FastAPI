<h1 align="center">🎵 Music Streamer Mobile App 🎵</h1>  

<p align="center">
	<a href="https://flutter.dev/"><img src="https://img.shields.io/badge/Flutter-3.22-blue.svg?logo=flutter" alt="Flutter"></a>
	<a href="https://dart.dev/"><img src="https://img.shields.io/badge/Dart-3.2-blue.svg?logo=dart" alt="Dart"></a>
	<a href="https://pub.dev/"><img src="https://img.shields.io/badge/Pub-Dev-orange.svg?logo=pub" alt="Pub"></a>
</p>

## Getting Started

### Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) (3.22 or higher)
- [Dart SDK](https://dart.dev/get-dart) (3.2 or higher)
- [Android Studio](https://developer.android.com/studio) or [VS Code](https://code.visualstudio.com/)
- Backend server running (see main README.md)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/myndaaa/MusicPlayer-FastAPI.git
cd MusicPlayer-FastAPI/frontend
```

2. **Install dependencies**
```bash
flutter pub get
```

3. **Run the app**
```bash
flutter run
```

### Development Commands

```bash
# Get dependencies
flutter pub get


# Run the app
flutter run


# Run on specific platform
flutter run -d chrome # Web
flutter run -d ios # iOS simulator
flutter run -d android # Android emulator
  

# Build for production
flutter build apk # Android APK
flutter build ios # iOS
flutter build web # Web

# Run tests
flutter test
```

##  Troubleshooting

**App won't start:**
```bash
flutter clean
flutter pub get
flutter run

```

**Backend connection failed:**
- Ensure backend server is running
- Check base URL in `auth_service.dart`
- Verify CORS settings in `backend/app/main.py`

**Build errors:**
```bash
flutter doctor
flutter analyze
```

  