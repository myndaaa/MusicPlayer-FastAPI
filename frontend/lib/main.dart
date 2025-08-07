// lib/main.dart

import 'package:flutter/material.dart';
import 'package:music_app/screens/artist_signup_screen.dart';
import 'package:music_app/screens/register_screen.dart';
import 'package:music_app/screens/user_dashboard.dart';
import 'package:music_app/screens/welcome_screen.dart';


void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mplayer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF212529),
        primaryColor: const Color(0xFF83bef2),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Color(0xFFdfe8f0)),
          bodyMedium: TextStyle(color: Color(0xFFdfe8f0)),
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const WelcomeScreen(),
        '/login': (context) => const WelcomeScreen(), // same as welcome screen
        '/register': (context) => const RegisterScreen(),
        '/artist-signup': (context) => const ArtistSignupScreen(),
        '/dashboard': (context) => const UserDashboardScreen(),
      },
    );
  }
}
