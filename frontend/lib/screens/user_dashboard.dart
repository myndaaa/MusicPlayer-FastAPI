import 'package:flutter/material.dart';
import '../widgets/details_panel.dart';
import '../widgets/music_player.dart';
import '../widgets/side_panel.dart';


class UserDashboardScreen extends StatelessWidget {
  const UserDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: const Color(0xFF212529),
      body: Column(
        children: [
          // Top Banner
          Container(
            color: const Color(0xFF1c1f22),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                // Logo and App Name
                Row(
                  children: [
                    Image.asset('assets/app.png', width: 40, height: 40),
                    const SizedBox(width: 8),
                    const Text(
                      "M Player",
                      style: TextStyle(
                        color: Color(0xFFdfe8f0),
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const Spacer(),

                // User Profile and Welcome Message
                Row(
                  children: [
                    CircleAvatar(
                      radius: 20,
                      backgroundImage: AssetImage('assets/user.png'),
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      "Welcome, User",
                      style: TextStyle(
                        color: Color(0xFFdfe8f0),
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Main Content
          Expanded(
            child: Row(
              children: [
                // Side Panel - 25%
                const Expanded(
                  flex: 1,
                  child: SidePanel(),
                ),

                // Music Player - 50%
                const Expanded(
                  flex: 2,
                  child: MusicPlayer(),
                ),

                // Details Panel - 25%
                const Expanded(
                  flex: 1,
                  child: DetailsPanel(),
                ),
              ],
            ),
          ),

        ],
      ),
    );
  }
}
