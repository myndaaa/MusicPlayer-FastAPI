import 'package:flutter/material.dart';
import 'song_view_list.dart';
import 'playlist_view_list.dart';
import 'following_list.dart';

class SidePanel extends StatelessWidget {
  const SidePanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF1e2329),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title
          const Text(
            "Your Libraries",
            style: TextStyle(
              color: Color(0xFFdfe8f0),
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),

          // Liked Songs Section
          GestureDetector(
            onTap: () {
              // TODO: Navigate to liked songs screen
            },
            child: const Text(
              "Your Liked Songs",
              style: TextStyle(
                color: Color(0xFF83bef2),
                fontWeight: FontWeight.w600,
                fontSize: 16,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            flex: 1,
            child: ListView.builder(
              itemCount: 5, // Placeholder count
              itemBuilder: (context, index) {
                // TODO: Replace with fetched liked songs
                return const SongViewList();
              },
            ),
          ),

          const SizedBox(height: 16),

          // Playlists Section
          GestureDetector(
            onTap: () {
              // TODO: Navigate to playlists screen
            },
            child: const Text(
              "Your Playlists",
              style: TextStyle(
                color: Color(0xFF83bef2),
                fontWeight: FontWeight.w600,
                fontSize: 16,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            flex: 1,
            child: ListView.builder(
              itemCount: 3, // Placeholder
              itemBuilder: (context, index) {
                // TODO: Replace with user's playlists
                return const PlaylistViewList();
              },
            ),
          ),

          const SizedBox(height: 16),

          // Following Section
          GestureDetector(
            onTap: () {
              // TODO: Navigate to following screen
            },
            child: const Text(
              "You Following",
              style: TextStyle(
                color: Color(0xFF83bef2),
                fontWeight: FontWeight.w600,
                fontSize: 16,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            flex: 1,
            child: ListView.builder(
              itemCount: 4, // Placeholder
              itemBuilder: (context, index) {
                // TODO: Replace with followed artists/bands
                return const FollowingList();
              },
            ),
          ),
        ],
      ),
    );
  }
}
