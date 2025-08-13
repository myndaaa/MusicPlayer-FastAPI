import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../constants/app_constants.dart';
import '../widgets/custom_text_field.dart';
import '../widgets/custom_button.dart';

class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleResetPassword() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });
      
      // TODO: Implement password reset logic
      await Future.delayed(const Duration(seconds: 2)); // Simulate API call
      
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Password reset link sent to your email',
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
        Navigator.of(context).pop();
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
                constraints: const BoxConstraints(maxWidth: 400),
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
                            'Forgot Password',
                            style: AppTextStyles.heading2.copyWith(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.3),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Icon
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
                          Icons.lock_reset,
                          size: 40,
                          color: AppColors.textPrimary,
                        ),
                      ).animate().scale(delay: 400.ms).then().shake(),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Description
                      Text(
                        'Enter your email address and we\'ll send you a link to reset your password',
                        style: AppTextStyles.body2.copyWith(
                          fontSize: 16,
                          color: AppColors.textSecondary,
                          height: 1.5,
                        ),
                        textAlign: TextAlign.center,
                      ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.3),
                      
                      const SizedBox(height: AppSizes.paddingXLarge),
                      
                      // Reset Form
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
                            CustomTextField(
                              label: 'Email Address',
                              hint: 'Enter your email address',
                              controller: _emailController,
                              prefixIcon: Icons.email,
                              keyboardType: TextInputType.emailAddress,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Please enter your email address';
                                }
                                if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                                  return 'Please enter a valid email address';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: AppSizes.paddingLarge),
                            
                            CustomButton(
                              text: 'Send Reset Link',
                              onPressed: _handleResetPassword,
                              isLoading: _isLoading,
                              width: double.infinity,
                              height: 45,
                              icon: Icons.send,
                            ),
                          ],
                        ),
                      ).animate().fadeIn(delay: 800.ms).slideY(begin: 0.3),
                      
                      const SizedBox(height: AppSizes.paddingLarge),
                      
                      // Back to Login
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: Text(
                          'Back to Login',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ).animate().fadeIn(delay: 1000.ms).slideY(begin: 0.2),
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
