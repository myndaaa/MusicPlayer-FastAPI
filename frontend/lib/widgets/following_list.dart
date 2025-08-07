import 'package:flutter/material.dart';

class FollowingList extends StatelessWidget {
  const FollowingList({super.key});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.person, color: Colors.white),
      title: const Text("Followed Artist Placeholder", style: TextStyle(color: Colors.white)),
      onTap: () {
        // TODO: View artist profile
      },
    );
  }
}
