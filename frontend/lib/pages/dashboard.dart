import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../constants/app_constants.dart';
import '../widgets/custom_button.dart';
import '../services/auth_service.dart';
import 'homepage.dart';

class Dashboard extends StatefulWidget {
  const Dashboard({super.key});

  @override
  State<Dashboard> createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  final AuthService _authService = AuthService();
  Map<String, dynamic>? _userData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    final userData = await _authService.getUserData();
    setState(() {
      _userData = userData;
      _isLoading = false;
    });
  }

  Future<void> _handleLogout() async {
    await _authService.logout();
    if (mounted) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const HomePage()),
        (route) => false,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppGradients.backgroundGradient,
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(AppSizes.paddingLarge),
            child: Column(
              children: [
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Dashboard',
                      style: AppTextStyles.heading1,
                    ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.3),
                    CustomButton(
                      text: 'Logout',
                      onPressed: _handleLogout,
                      isOutlined: true,
                      icon: Icons.logout,
                    ).animate().fadeIn(delay: 400.ms).slideX(begin: 0.3),
                  ],
                ),
                
                const SizedBox(height: AppSizes.paddingXLarge),
                
                // User Info Card
                if (_isLoading)
                  const Center(
                    child: CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                    ),
                  )
                else if (_userData != null)
                  Container(
                    padding: const EdgeInsets.all(AppSizes.paddingLarge),
                    decoration: BoxDecoration(
                      gradient: AppGradients.cardGradient,
                      borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
                      border: Border.all(
                        color: AppColors.primary.withValues(alpha: 0.3),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      children: [
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            gradient: AppGradients.primaryGradient,
                            borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
                          ),
                          child: Icon(
                            _userData!['role'] == 'admin' 
                                ? Icons.admin_panel_settings
                                : _userData!['role'] == 'musician'
                                    ? Icons.music_note
                                    : Icons.person,
                            size: 40,
                            color: AppColors.textPrimary,
                          ),
                        ).animate().scale(delay: 600.ms).then().shake(),
                        
                        const SizedBox(height: AppSizes.paddingLarge),
                        
                        Text(
                          'Welcome, ${_userData!['username'] ?? 'User'}!',
                          style: AppTextStyles.heading2,
                          textAlign: TextAlign.center,
                        ).animate().fadeIn(delay: 800.ms).slideY(begin: -0.2),
                        
                        const SizedBox(height: AppSizes.paddingMedium),
                        
                        Text(
                          'Role: ${_userData!['role']?.toString().toUpperCase() ?? 'USER'}',
                          style: AppTextStyles.body1.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ).animate().fadeIn(delay: 1000.ms).slideY(begin: -0.2),
                        
                        const SizedBox(height: AppSizes.paddingMedium),
                        
                        Text(
                          'Email: ${_userData!['email'] ?? 'N/A'}',
                          style: AppTextStyles.body2,
                        ).animate().fadeIn(delay: 1200.ms).slideY(begin: -0.2),
                      ],
                    ),
                  ).animate().fadeIn(delay: 1000.ms).slideY(begin: 0.3)
                else
                  Container(
                    padding: const EdgeInsets.all(AppSizes.paddingLarge),
                    decoration: BoxDecoration(
                      gradient: AppGradients.cardGradient,
                      borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
                      border: Border.all(
                        color: AppColors.error.withValues(alpha: 0.3),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          Icons.error_outline,
                          size: 60,
                          color: AppColors.error,
                        ),
                        const SizedBox(height: AppSizes.paddingMedium),
                        Text(
                          'Failed to load user data',
                          style: AppTextStyles.heading2.copyWith(
                            color: AppColors.error,
                          ),
                        ),
                      ],
                    ),
                  ),
                
                const Spacer(),
                
                // Footer
                Text(
                  'MusicStream Dashboard',
                  style: AppTextStyles.body2.copyWith(
                    color: AppColors.textSecondary,
                    fontStyle: FontStyle.italic,
                  ),
                ).animate().fadeIn(delay: 1400.ms).slideY(begin: 0.2),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
