import 'package:flutter/material.dart';

class MusicPlayer extends StatelessWidget {
  const MusicPlayer({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Container(
        padding: const EdgeInsets.all(16),
        color: const Color(0xFF1e2329),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Album Cover
            Center(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.asset(
                  'assets/app.png',
                  height: 250,
                  width: 250,
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Song Title
            const Text(
              "Imagine",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),

            // Artist/Band Name
            const Text(
              "John Lennon",
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 24),

            // Playback Controls
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  icon: const Icon(Icons.skip_previous_rounded, color: Colors.white),
                  iconSize: 36,
                  onPressed: () {
                    // TODO: Previous track
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.play_circle_fill_rounded, color: Colors.white),
                  iconSize: 56,
                  onPressed: () {
                    // TODO: Play/Pause
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.skip_next_rounded, color: Colors.white),
                  iconSize: 36,
                  onPressed: () {
                    // TODO: Next track
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Playline (slider)
            Column(
              children: [
                Slider(
                  value: 84,
                  min: 0,
                  max: 225,
                  onChanged: (value) {
                    // TODO: Seek position
                  },
                  activeColor: Colors.white,
                  inactiveColor: Colors.grey[700],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Text("1:24", style: TextStyle(color: Colors.white70, fontSize: 12)),
                    Text("3:45", style: TextStyle(color: Colors.white70, fontSize: 12)),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Upload Info and Likes
            const Text(
              "Uploaded at: Jan 1, 2024     Likes: 8.2K",
              style: TextStyle(color: Colors.grey, fontSize: 13),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),

            // Genre Tag
            GestureDetector(
              onTap: () {
                // TODO: Navigate to genre screen
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.blueGrey.shade700,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text(
                  "Genre: Pop",
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ),
            const SizedBox(height: 35),

            // Artist/Band Profile Widget
            const _ArtistProfile(),
          ],
        ),
      ),
    );
  }
}

// Dummy Artist Profile
class _ArtistProfile extends StatelessWidget {
  const _ArtistProfile();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 32),
      decoration: BoxDecoration(
        color: const Color(0xFF2c333a),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text(
            "Artist Profile",
            style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text(
            "John Lennon was a legendary singer-songwriter and peace activist. He was a co-founder of The Beatles and created timeless music.",
            style: TextStyle(color: Colors.white70),
          ),
        ],
      ),
    );
  }
}
