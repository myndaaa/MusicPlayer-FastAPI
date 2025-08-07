import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../services/auth_service.dart';

// Screen for creating new user accounts
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> with TickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false; // shows loading spinner during registration
  String? _errorMessage; // stores error message to show in alert
  bool _isSuccessAlert = false; // whether it's a success or error alert
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  // Text controllers for form fields
  final usernameController = TextEditingController();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmPasswordController = TextEditingController();

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
  }

  @override
  void dispose() {
    _animationController.dispose();
    usernameController.dispose();
    firstNameController.dispose();
    lastNameController.dispose();
    emailController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  // shows beautiful alert at the top of the screen
  void _showErrorAlert(String message, {bool isSuccess = false}) {
    setState(() {
      _errorMessage = message;
      _isSuccessAlert = isSuccess;
    });
    _animationController.forward();
    
    // auto-hide after 4 seconds
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

  // handles the registration process
  Future<void> _onRegister() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });

      try {
        final result = await AuthService.register(
          username: usernameController.text.trim(),
          firstName: firstNameController.text.trim(),
          lastName: lastNameController.text.trim(),
          email: emailController.text.trim(),
          password: passwordController.text,
        );

        if (mounted) {
          setState(() {
            _isLoading = false;
          });

          if (result['success']) {
            // registration successful - show success message and go to login
            _showErrorAlert("Account created successfully! Please log in.", isSuccess: true);
            Future.delayed(const Duration(milliseconds: 500), () {
              if (mounted) {
                Navigator.pushReplacementNamed(context, '/'); // go back to welcome screen
              }
            });
          } else {
            // registration failed - show error alert
            _showErrorAlert(result['error'] ?? "Registration failed");
          }
        }
      } catch (e) {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
          _showErrorAlert("An error occurred: $e");
        }
      }
    }
  }

  // beautiful error alert widget
  Widget _buildErrorAlert() {
    if (_errorMessage == null) return const SizedBox.shrink();
    
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Container(
        width: double.infinity,
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: _isSuccessAlert ? Colors.green.withOpacity(0.9) : Colors.red.withOpacity(0.9),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(
              _isSuccessAlert ? Icons.check_circle : Icons.error_outline,
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF212529),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF83bef2)),
          onPressed: () => Navigator.pushReplacementNamed(context, '/'),
        ),
        title: const Text(
          "Create Account",
          style: TextStyle(color: Color(0xFFdfe8f0)),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // error alert at the top
          _buildErrorAlert(),
          
          // main content
          Expanded(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 400),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      children: [
                        // app logo
                        Image.asset(
                          'assets/app.png',
                          width: 80,
                          height: 80,
                        ),
                        const SizedBox(height: 16),
                        
                        // welcome message
                        const Text(
                          "Join Mplayer",
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFFdfe8f0),
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          "Create your account to start listening",
                          style: TextStyle(
                            color: Color(0xFF83bef2),
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 32),

                        // form fields in two columns for better layout
                        Row(
                          children: [
                            Expanded(
                              child: _buildTextField(firstNameController, "First Name"),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildTextField(lastNameController, "Last Name"),
                            ),
                          ],
                        ),
                        _buildTextField(usernameController, "Username"),
                        _buildTextField(emailController, "Email", isEmail: true),
                        _buildTextField(passwordController, "Password", isPassword: true),
                        // Password requirements hint
                        Padding(
                          padding: const EdgeInsets.only(left: 12, bottom: 8),
                          child: Text(
                            "Password must contain: 8+ characters, uppercase, lowercase, and special character",
                            style: TextStyle(
                              color: Color(0xFF83bef2),
                              fontSize: 12,
                            ),
                          ),
                        ),
                        _buildTextField(confirmPasswordController, "Confirm Password", isPassword: true),
                        
                        const SizedBox(height: 24),

                        // register button
                        ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 240),
                          child: SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: _isLoading ? null : _onRegister,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF83bef2),
                                foregroundColor: Colors.black,
                                padding: const EdgeInsets.symmetric(vertical: 16),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: _isLoading
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: SpinKitCircle(
                                        color: Colors.black,
                                        size: 20,
                                      ),
                                    )
                                  : const Text("Create Account"),
                            ),
                          ),
                        ),

                        const SizedBox(height: 16),

                        // login link
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text(
                              "Already have an account? ",
                              style: TextStyle(color: Color(0xFFdfe8f0)),
                            ),
                            TextButton(
                              onPressed: () => Navigator.pushReplacementNamed(context, '/'),
                              child: const Text(
                                "Log in",
                                style: TextStyle(color: Color(0xFF83bef2)),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // creates a styled text field
  Widget _buildTextField(
      TextEditingController controller,
      String label, {
        bool isPassword = false,
        bool isEmail = false,
      }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: TextFormField(
        controller: controller,
        obscureText: isPassword,
        keyboardType:
        isEmail ? TextInputType.emailAddress : TextInputType.text,
        style: const TextStyle(color: Color(0xFFdfe8f0)),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: const TextStyle(color: Color(0xFFdfe8f0)),
          enabledBorder: const OutlineInputBorder(
            borderSide: BorderSide(color: Color(0xFF83bef2)),
          ),
          focusedBorder: const OutlineInputBorder(
            borderSide: BorderSide(color: Color(0xFF83bef2), width: 2),
          ),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return '$label is required';
          }
          if (isEmail && !value.contains('@')) {
            return 'Enter a valid email';
          }
          if (isPassword && label == "Password") {
            if (value.length < 8) {
              return 'Password must be at least 8 characters';
            }
            if (!RegExp(r'[A-Z]').hasMatch(value)) {
              return 'Password must include at least one uppercase letter';
            }
            if (!RegExp(r'[a-z]').hasMatch(value)) {
              return 'Password must include at least one lowercase letter';
            }
            if (!RegExp(r'[\W_]').hasMatch(value)) {
              return 'Password must include at least one special character';
            }
          }
          if (label == "Confirm Password" && value != passwordController.text) {
            return 'Passwords do not match';
          }
          return null;
        },
      ),
    );
  }
}
