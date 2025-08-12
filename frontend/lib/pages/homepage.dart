import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../constants/app_constants.dart';
import '../widgets/custom_text_field.dart';
import '../widgets/custom_button.dart';
import '../services/auth_service.dart';
import 'dashboard.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final AuthService _authService = AuthService();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
      
      final result = await _authService.login(
        _usernameController.text.trim(),
        _passwordController.text,
      );
      
      setState(() {
        _isLoading = false;
      });
      
      if (result['success']) {
        if (mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const Dashboard()),
          );
        }
      } else {
        setState(() {
          _errorMessage = result['error'];
        });
      }
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
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AppSizes.paddingLarge),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 400),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Logo
                      Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          gradient: AppGradients.primaryGradient,
                          borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.primary.withValues(alpha: 0.3),
                              blurRadius: 15,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.music_note,
                          size: 40,
                          color: AppColors.textPrimary,
                        ),
                      ).animate().scale(delay: 200.ms).then().shake(),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Welcome Text
                      Text(
                        'Welcome to MusicStream',
                        style: AppTextStyles.heading2.copyWith(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                        textAlign: TextAlign.center,
                      ).animate().fadeIn(delay: 400.ms).slideY(begin: -0.3),
                      
                      const SizedBox(height: AppSizes.paddingSmall),
                      
                      Text(
                        'Your ultimate music streaming experience',
                        style: AppTextStyles.body2.copyWith(
                          fontSize: 14,
                          color: AppColors.textSecondary,
                        ),
                        textAlign: TextAlign.center,
                      ).animate().fadeIn(delay: 600.ms).slideY(begin: -0.2),
                      
                      const SizedBox(height: AppSizes.paddingXLarge),
                      
                      // Login Form
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(AppSizes.paddingLarge),
                        decoration: BoxDecoration(
                          color: AppColors.surface.withValues(alpha: 0.8),
                          borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
                          border: Border.all(
                            color: AppColors.primary.withValues(alpha: 0.2),
                            width: 1,
                          ),
                        ),
                        child: Column(
                          children: [
                            Text(
                              'Sign In',
                              style: AppTextStyles.heading2.copyWith(
                                fontSize: 20,
                                fontWeight: FontWeight.w600,
                              ),
                            ).animate().fadeIn(delay: 800.ms).slideY(begin: -0.2),
                            
                            const SizedBox(height: AppSizes.paddingLarge),
                            
                            CustomTextField(
                              label: 'Username',
                              hint: 'Enter your username',
                              controller: _usernameController,
                              prefixIcon: Icons.person,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Please enter your username';
                                }
                                return null;
                              },
                            ),
                            
                            CustomTextField(
                              label: 'Password',
                              hint: 'Enter your password',
                              controller: _passwordController,
                              isPassword: true,
                              prefixIcon: Icons.lock,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Please enter your password';
                                }
                                if (value.length < 6) {
                                  return 'Password must be at least 6 characters';
                                }
                                return null;
                              },
                            ),
                            
                            if (_errorMessage != null) ...[
                              const SizedBox(height: AppSizes.paddingMedium),
                              Container(
                                padding: const EdgeInsets.all(AppSizes.paddingMedium),
                                decoration: BoxDecoration(
                                  color: AppColors.error.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
                                  border: Border.all(
                                    color: AppColors.error.withValues(alpha: 0.3),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Icon(
                                      Icons.error_outline,
                                      color: AppColors.error,
                                      size: 18,
                                    ),
                                    const SizedBox(width: AppSizes.paddingSmall),
                                    Expanded(
                                      child: Text(
                                        _errorMessage!,
                                        style: AppTextStyles.body2.copyWith(
                                          color: AppColors.error,
                                          fontSize: 13,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ).animate().fadeIn().slideX(begin: -0.2),
                            ],
                            
                            const SizedBox(height: AppSizes.paddingLarge),
                            
                            CustomButton(
                              text: 'Sign In',
                              onPressed: _handleLogin,
                              isLoading: _isLoading,
                              width: double.infinity,
                              height: 45,
                              icon: Icons.login,
                            ),
                          ],
                        ),
                      ).animate().fadeIn(delay: 1000.ms).slideY(begin: 0.3),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Sign Up Options
                      Row(
                        children: [
                          Expanded(
                            child: CustomButton(
                              text: 'Create Account',
                              onPressed: () {
                                // TODO: Navigate to signup page
                              },
                              isOutlined: true,
                              height: 40,
                              icon: Icons.person_add,
                            ),
                          ),
                          const SizedBox(width: AppSizes.paddingMedium),
                          Expanded(
                            child: CustomButton(
                              text: 'Artist Signup',
                              onPressed: () {
                                // TODO: Navigate to artist signup page
                              },
                              isOutlined: true,
                              height: 40,
                              icon: Icons.music_note,
                            ),
                          ),
                        ],
                      ).animate().fadeIn(delay: 1200.ms).slideY(begin: 0.3),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Footer Text
                      Text(
                        'Experience music like never before',
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.textSecondary,
                          fontStyle: FontStyle.italic,
                          fontSize: 12,
                        ),
                        textAlign: TextAlign.center,
                      ).animate().fadeIn(delay: 1400.ms).slideY(begin: 0.2),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
