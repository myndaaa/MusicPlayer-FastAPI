import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:frontend/widgets/custom_button.dart';
import '../constants/app_constants.dart';
import '../widgets/custom_text_field.dart';
import '../services/auth_service.dart';
import 'verify.dart';

class ArtistSignupPage extends StatefulWidget {
  const ArtistSignupPage({super.key});

  @override
  State<ArtistSignupPage> createState() => _ArtistSignupPageState();
}

class _ArtistSignupPageState extends State<ArtistSignupPage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _stageNameController = TextEditingController();
  final _bioController = TextEditingController();
  final _instagramController = TextEditingController();
  final _twitterController = TextEditingController();
  final _youtubeController = TextEditingController();
  final AuthService _authService = AuthService();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _stageNameController.dispose();
    _bioController.dispose();
    _instagramController.dispose();
    _twitterController.dispose();
    _youtubeController.dispose();
    super.dispose();
  }

  Map<String, dynamic>? _buildSocialLinks() {
    final links = <String, dynamic>{};
    if (_instagramController.text.isNotEmpty) {
      links['instagram'] = _instagramController.text.trim();
    }
    if (_twitterController.text.isNotEmpty) {
      links['twitter'] = _twitterController.text.trim();
    }
    if (_youtubeController.text.isNotEmpty) {
      links['youtube'] = _youtubeController.text.trim();
    }
    return links.isNotEmpty ? links : null;
  }

  Future<void> _handleSignup() async {
    if (_formKey.currentState!.validate()) {
      if (_passwordController.text != _confirmPasswordController.text) {
        setState(() {
          _errorMessage = 'Passwords do not match';
        });
        return;
      }

      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });

      final result = await _authService.artistSignup(
        username: _usernameController.text.trim(),
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text,
        stageName: _stageNameController.text.trim(),
        bio: _bioController.text.trim().isNotEmpty ? _bioController.text.trim() : null,
        socialLinks: _buildSocialLinks(),
      );

      setState(() {
        _isLoading = false;
      });

      if (result['success']) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                result['message'],
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w500,
                ),
              ),
              backgroundColor: AppColors.success.withValues(alpha: 0.8),
              behavior: SnackBarBehavior.floating,
              margin: EdgeInsets.only(
                bottom: MediaQuery.of(context).size.height - 100,
                right: 20,
                left: 20,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
              ),
            ),
          );
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (context) => const VerifyPage()),
            (route) => false,
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
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: AppGradients.backgroundGradient,
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSizes.paddingLarge),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 500),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Back Button and Title
                      Row(
                        children: [
                          IconButton(
                            onPressed: () => Navigator.of(context).pop(),
                            icon: const Icon(
                              Icons.arrow_back_ios,
                              color: AppColors.textPrimary,
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: AppSizes.paddingMedium),
                          Text(
                            'Artist Signup',
                            style: AppTextStyles.heading2.copyWith(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.3),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Signup Form
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
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Personal Information',
                              style: AppTextStyles.heading2.copyWith(
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                              ),
                            ).animate().fadeIn(delay: 300.ms).slideX(begin: -0.2),
                            
                            const SizedBox(height: AppSizes.paddingMedium),
                            
                            CustomTextField(
                              label: 'Username',
                              hint: 'Enter your username',
                              controller: _usernameController,
                              prefixIcon: Icons.person,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Please enter a username';
                                }
                                if (value.length < 3) {
                                  return 'Username must be at least 3 characters';
                                }
                                return null;
                              },
                            ),
                            
                            Row(
                              children: [
                                Expanded(
                                  child: CustomTextField(
                                    label: 'First Name',
                                    hint: 'First name',
                                    controller: _firstNameController,
                                    prefixIcon: Icons.person_outline,
                                    validator: (value) {
                                      if (value == null || value.isEmpty) {
                                        return 'Please enter your first name';
                                      }
                                      return null;
                                    },
                                  ),
                                ),
                                const SizedBox(width: AppSizes.paddingMedium),
                                Expanded(
                                  child: CustomTextField(
                                    label: 'Last Name',
                                    hint: 'Last name',
                                    controller: _lastNameController,
                                    prefixIcon: Icons.person_outline,
                                    validator: (value) {
                                      if (value == null || value.isEmpty) {
                                        return 'Please enter your last name';
                                      }
                                      return null;
                                    },
                                  ),
                                ),
                              ],
                            ),
                            
                            CustomTextField(
                              label: 'Email',
                              hint: 'Enter your email',
                              controller: _emailController,
                              keyboardType: TextInputType.emailAddress,
                              prefixIcon: Icons.email,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Please enter your email';
                                }
                                if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                                  return 'Please enter a valid email';
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
                                  return 'Please enter a password';
                                }
                                if (value.length < 8) {
                                  return 'Password must be at least 8 characters';
                                }
                                if (!RegExp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\W)').hasMatch(value)) {
                                  return 'Password must include uppercase, lowercase, and special character';
                                }
                                return null;
                              },
                            ),
                            
                            CustomTextField(
                              label: 'Confirm Password',
                              hint: 'Confirm your password',
                              controller: _confirmPasswordController,
                              isPassword: true,
                              prefixIcon: Icons.lock_outline,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Please confirm your password';
                                }
                                if (value != _passwordController.text) {
                                  return 'Passwords do not match';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: AppSizes.paddingLarge),
                            
                            Text(
                              'Artist Information',
                              style: AppTextStyles.heading2.copyWith(
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                              ),
                            ).animate().fadeIn(delay: 500.ms).slideX(begin: -0.2),
                            
                            const SizedBox(height: AppSizes.paddingMedium),
                            
                            CustomTextField(
                              label: 'Stage Name',
                              hint: 'Enter your artist stage name',
                              controller: _stageNameController,
                              prefixIcon: Icons.music_note,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Please enter your stage name';
                                }
                                if (value.length < 2) {
                                  return 'Stage name must be at least 2 characters';
                                }
                                return null;
                              },
                            ),
                            
                            CustomTextField(
                              label: 'Bio (Optional)',
                              hint: 'Tell us about yourself and your music',
                              controller: _bioController,
                              prefixIcon: Icons.description,
                            ),
                            
                            const SizedBox(height: AppSizes.paddingMedium),
                            
                            Text(
                              'Social Media (Optional)',
                              style: AppTextStyles.body1.copyWith(
                                fontWeight: FontWeight.w500,
                                color: AppColors.textSecondary,
                              ),
                            ),
                            
                            const SizedBox(height: AppSizes.paddingSmall),
                            
                            CustomTextField(
                              label: 'Instagram',
                              hint: 'Your Instagram handle',
                              controller: _instagramController,
                              prefixIcon: Icons.camera_alt,
                            ),
                            
                            CustomTextField(
                              label: 'Twitter/X',
                              hint: 'Your Twitter/X handle',
                              controller: _twitterController,
                              prefixIcon: Icons.flutter_dash,
                            ),
                            
                            CustomTextField(
                              label: 'YouTube',
                              hint: 'Your YouTube channel',
                              controller: _youtubeController,
                              prefixIcon: Icons.play_circle_outline,
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
                              text: 'Create Artist Account',
                              onPressed: _handleSignup,
                              isLoading: _isLoading,
                              width: double.infinity,
                              height: 45,
                              icon: Icons.music_note,
                            ),
                          ],
                        ),
                      ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.3),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Login Link
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Already have an account? ',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          GestureDetector(
                            onTap: () => Navigator.of(context).pop(),
                            child: Text(
                              'Sign In',
                              style: AppTextStyles.body2.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.2),
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
