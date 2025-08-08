import 'package:flutter/material.dart';

class PlaylistViewList extends StatelessWidget {
  const PlaylistViewList({super.key});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.queue_music, color: Colors.white),
      title: const Text("Playlist Placeholder", style: TextStyle(color: Colors.white)),
      onTap: () {
        // TODO: Navigate to playlist
      },
    );
  }
}
