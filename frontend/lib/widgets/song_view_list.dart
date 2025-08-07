import 'package:flutter/material.dart';

class SongViewList extends StatelessWidget {
  const SongViewList({super.key});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.music_note, color: Colors.white),
      title: const Text("Liked Song Placeholder", style: TextStyle(color: Colors.white)),
      onTap: () {
        // TODO: Play this song
      },
    );
  }
}
