import 'package:flutter/material.dart';
import '../widgets/details_panel.dart';
import '../widgets/music_player.dart';
import '../widgets/side_panel.dart';
import '../services/auth_service.dart';

// This is the main screen users see after they log in
// It shows the music player and user info
class UserDashboardScreen extends StatefulWidget {
  const UserDashboardScreen({super.key});

  @override
  State<UserDashboardScreen> createState() => _UserDashboardScreenState();
}

class _UserDashboardScreenState extends State<UserDashboardScreen> with TickerProviderStateMixin {
  // This holds the user's info like their name and email
  Map<String, dynamic>? _userInfo;
  // This tells us if we're still loading the user's info
  bool _isLoading = true;
  String? _alertMessage; // stores alert message to show
  bool _isSuccessAlert = false; // whether it's a success or error alert
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  // This runs when the screen first loads
  // It gets the user's info from the backend
  @override
  void initState() {
    super.initState();
    _loadUserInfo();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  // Gets the current user's info from the backend
  // This shows their name in the top bar
  Future<void> _loadUserInfo() async {
    try {
      final result = await AuthService.getCurrentUser();
      if (mounted) {
        setState(() {
          _isLoading = false;
          if (result['success']) {
            _userInfo = result['data'];
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // shows beautiful alert at the top of the screen
  void _showAlert(String message, bool isSuccess) {
    setState(() {
      _alertMessage = message;
      _isSuccessAlert = isSuccess;
    });
    _animationController.forward();
    
    // auto-hide after 4 seconds
    Future.delayed(const Duration(seconds: 4), () {
      if (mounted) {
        _animationController.reverse().then((_) {
          setState(() {
            _alertMessage = null;
          });
        });
      }
    });
  }

  // This logs the user out and takes them back to the welcome screen
  Future<void> _logout() async {
    try {
      await AuthService.logout();
      if (mounted) {
        _showAlert("Logged out successfully", true);
        Future.delayed(const Duration(milliseconds: 500), () {
          if (mounted) {
            Navigator.pushReplacementNamed(context, '/');
          }
        });
      }
    } catch (e) {
      if (mounted) {
        _showAlert("Error logging out: $e", false);
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  // beautiful alert widget
  Widget _buildAlert() {
    if (_alertMessage == null) return const SizedBox.shrink();
    
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Container(
        width: double.infinity,
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: _isSuccessAlert 
              ? Colors.green.withValues(alpha: 0.9)
              : Colors.red.withValues(alpha: 0.9),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.2),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(
              _isSuccessAlert ? Icons.check_circle_outline : Icons.error_outline,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                _alertMessage!,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            IconButton(
              onPressed: () {
                _animationController.reverse().then((_) {
                  setState(() {
                    _alertMessage = null;
                  });
                });
              },
              icon: const Icon(
                Icons.close,
                color: Colors.white,
                size: 18,
              ),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(
                minWidth: 24,
                minHeight: 24,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF212529),
      body: Column(
        children: [
          // alert at the top
          _buildAlert(),
          
          // The top bar with the app logo and user info
          Container(
            color: const Color(0xFF1c1f22),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                // Show the app logo and name on the left
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

                // Show the user's profile picture and name on the right
                Row(
                  children: [
                    CircleAvatar(
                      radius: 20,
                      backgroundImage: AssetImage('assets/user.png'),
                    ),
                    const SizedBox(width: 8),
                    // Show a loading spinner while getting user info, or their name
                    _isLoading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Color(0xFF83bef2),
                              ),
                            ),
                          )
                        : Text(
                            "Welcome, ${_userInfo?['username'] ?? 'User'}",
                            style: const TextStyle(
                              color: Color(0xFFdfe8f0),
                              fontSize: 16,
                            ),
                          ),
                    const SizedBox(width: 16),
                    // The logout button
                    IconButton(
                      onPressed: _logout,
                      icon: const Icon(
                        Icons.logout,
                        color: Color(0xFF83bef2),
                      ),
                      tooltip: 'Logout',
                    ),
                  ],
                ),
              ],
            ),
          ),

          // The main content area with the music player
          Expanded(
            child: Row(
              children: [
                // The side panel on the left (25% of screen)
                const Expanded(
                  flex: 1,
                  child: SidePanel(),
                ),

                // The main music player in the middle (50% of screen)
                const Expanded(
                  flex: 2,
                  child: MusicPlayer(),
                ),

                // The details panel on the right (25% of screen)
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
