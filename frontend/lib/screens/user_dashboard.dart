import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../services/auth_service.dart';

class UserDashboard extends StatefulWidget {
  const UserDashboard({super.key});

  @override
  State<UserDashboard> createState() => _UserDashboardState();
}

class _UserDashboardState extends State<UserDashboard> with TickerProviderStateMixin {
  Map<String, dynamic>? _userInfo;
  bool _isLoading = true;
  String? _errorMessage;
  bool _isSuccessAlert = false;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
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
    _loadUserInfo();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _loadUserInfo() async {
    try {
      final result = await AuthService.getCurrentUser();
      if (mounted) {
        setState(() {
          _userInfo = result;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = "Failed to load user info: $e";
          _isSuccessAlert = false;
          _isLoading = false;
        });
        _animationController.forward();
      }
    }
  }

  void _showAlert(String message, bool isSuccess) {
    setState(() {
      _errorMessage = message;
      _isSuccessAlert = isSuccess;
    });
    _animationController.forward();
    
    Future.delayed(const Duration(seconds: 4), () {
      if (mounted) {
        _animationController.reverse().then((_) {
          setState(() {
            _errorMessage = null;
          });
        });
      }
    });
  }

  Future<void> _logout() async {
    try {
      await AuthService.logout();
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/');
      }
    } catch (e) {
      _showAlert("Logout failed: $e", false);
    }
  }

  Widget _buildAlert() {
    if (_errorMessage == null) return const SizedBox.shrink();
    
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
                _errorMessage!,
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
                    _errorMessage = null;
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

  String _getUserRole() {
    return _userInfo?['role'] ?? 'listener';
  }

  bool _isAdmin() {
    return _getUserRole() == 'admin';
  }

  bool _isMusician() {
    return _getUserRole() == 'musician';
  }

  Widget _buildAdminDashboard() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Admin Dashboard",
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Color(0xFFdfe8f0),
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          "Manage users, content, and system settings",
          style: TextStyle(
            color: Color(0xFF83bef2),
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 32),
        _buildActionCard(
          "User Management",
          "Manage all users, roles, and permissions",
          Icons.people,
          () => _showAlert("User management coming soon!", true),
        ),
        _buildActionCard(
          "Content Moderation",
          "Review and moderate music content",
          Icons.music_note,
          () => _showAlert("Content moderation coming soon!", true),
        ),
        _buildActionCard(
          "System Analytics",
          "View platform statistics and insights",
          Icons.analytics,
          () => _showAlert("Analytics dashboard coming soon!", true),
        ),
        _buildActionCard(
          "Settings",
          "Configure system settings and preferences",
          Icons.settings,
          () => _showAlert("Settings panel coming soon!", true),
        ),
      ],
    );
  }

  Widget _buildMusicianDashboard() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Artist Dashboard",
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Color(0xFFdfe8f0),
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          "Manage your music and connect with listeners",
          style: TextStyle(
            color: Color(0xFF83bef2),
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 32),
        _buildActionCard(
          "My Music",
          "Upload and manage your tracks",
          Icons.music_note,
          () => _showAlert("Music management coming soon!", true),
        ),
        _buildActionCard(
          "Analytics",
          "View your music performance stats",
          Icons.trending_up,
          () => _showAlert("Artist analytics coming soon!", true),
        ),
        _buildActionCard(
          "Fans",
          "Connect with your listeners",
          Icons.favorite,
          () => _showAlert("Fan management coming soon!", true),
        ),
        _buildActionCard(
          "Profile",
          "Update your artist profile",
          Icons.person,
          () => _showAlert("Profile settings coming soon!", true),
        ),
      ],
    );
  }

  Widget _buildListenerDashboard() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Welcome Back!",
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Color(0xFFdfe8f0),
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          "Discover and enjoy your favorite music",
          style: TextStyle(
            color: Color(0xFF83bef2),
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 32),
        _buildActionCard(
          "Discover",
          "Find new music and artists",
          Icons.explore,
          () => _showAlert("Music discovery coming soon!", true),
        ),
        _buildActionCard(
          "My Playlists",
          "Manage your music collections",
          Icons.playlist_play,
          () => _showAlert("Playlist management coming soon!", true),
        ),
        _buildActionCard(
          "Following",
          "Artists and friends you follow",
          Icons.people,
          () => _showAlert("Following list coming soon!", true),
        ),
        _buildActionCard(
          "Profile",
          "Update your profile settings",
          Icons.person,
          () => _showAlert("Profile settings coming soon!", true),
        ),
      ],
    );
  }

  Widget _buildActionCard(String title, String subtitle, IconData icon, VoidCallback onTap) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Card(
        color: const Color(0xFF2c3e50),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF83bef2).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    icon,
                    color: const Color(0xFF83bef2),
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFdfe8f0),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: const TextStyle(
                          color: Color(0xFF83bef2),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(
                  Icons.arrow_forward_ios,
                  color: Color(0xFF83bef2),
                  size: 16,
                ),
              ],
            ),
          ),
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
          _buildAlert(),
          Expanded(
            child: _isLoading
                ? const Center(
                    child: SpinKitCircle(
                      color: Color(0xFF83bef2),
                      size: 50,
                    ),
                  )
                : Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    "Hello, ${_userInfo?['first_name'] ?? 'User'}!",
                                    style: const TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFFdfe8f0),
                                    ),
                                  ),
                                  Text(
                                    "@${_userInfo?['username'] ?? 'username'}",
                                    style: const TextStyle(
                                      color: Color(0xFF83bef2),
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              onPressed: _logout,
                              icon: const Icon(
                                Icons.logout,
                                color: Color(0xFF83bef2),
                                size: 24,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 32),
                        Expanded(
                          child: SingleChildScrollView(
                            child: _isAdmin()
                                ? _buildAdminDashboard()
                                : _isMusician()
                                    ? _buildMusicianDashboard()
                                    : _buildListenerDashboard(),
                          ),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
