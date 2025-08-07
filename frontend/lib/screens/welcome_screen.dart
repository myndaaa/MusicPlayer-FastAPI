import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:fluttertoast/fluttertoast.dart';
import '../services/auth_service.dart';

// This is the first screen users see when they open the app
// It shows a welcome message and lets them log in
class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  // These variables keep track of what the screen should show
  bool _showLoginForm = false; // Whether to show the login form or welcome screen
  bool _isLoading = false; // Whether we're currently trying to log in
  final _formKey = GlobalKey<FormState>(); // Helps us validate the login form
  final usernameController = TextEditingController(); // Holds what the user types for username
  final passwordController = TextEditingController(); // Holds what the user types for password

  // This runs when the screen first loads
  // It sets up the auth service and checks if the user is already logged in
  @override
  void initState() {
    super.initState();
    _initializeAuth();
  }

  // Sets up the auth service and checks if the user is already logged in
  // If they are, it automatically takes them to the dashboard
  Future<void> _initializeAuth() async {
    await AuthService.init();
    // Check if user is already logged in
    final isLoggedIn = await AuthService.isLoggedIn();
    if (isLoggedIn && mounted) {
      Navigator.pushReplacementNamed(context, '/dashboard');
    }
  }

  // Clean up when done with this screen to prevent memory leaks
  @override
  void dispose() {
    usernameController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  // validates input, shows a loading spinner, and tries to log them in
  Future<void> _onLogin() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });

      try {
        // Try to log the user in with what they typed
        final result = await AuthService.login(
          usernameController.text.trim(),
          passwordController.text,
        );

        if (mounted) {
          setState(() {
            _isLoading = false;
          });

          if (result['success']) {
            // Show a success message and go to dashboard
            Fluttertoast.showToast(
              msg: "Login successful!",
              toastLength: Toast.LENGTH_SHORT,
              gravity: ToastGravity.BOTTOM,
              backgroundColor: Colors.green,
            );
            Navigator.pushReplacementNamed(context, '/dashboard');
          } else {
            // Login failed - show the error message
            Fluttertoast.showToast(
              msg: result['error'] ?? "Login failed",
              toastLength: Toast.LENGTH_LONG,
              gravity: ToastGravity.BOTTOM,
              backgroundColor: Colors.red,
            );
          }
        }
      } catch (e) {
        // Something unexpected went wrong
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
          Fluttertoast.showToast(
            msg: "An error occurred: $e",
            toastLength: Toast.LENGTH_LONG,
            gravity: ToastGravity.BOTTOM,
            backgroundColor: Colors.red,
          );
        }
      }
    }
  }

  // Switches between showing the welcome screen and the login form
  void _toggleLoginForm() {
    setState(() {
      _showLoginForm = !_showLoginForm;
    });
  }

  // Creates a text field that looks nice and matches our app's style
  // This is used for both username and password fields
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
        obscureText: isPassword, // Hide the text if it's a password field
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
          // Make sure the user actually typed something
          if (value == null || value.isEmpty) {
            return '$label is required';
          }
          if (isEmail && !value.contains('@')) {
            return 'Enter a valid email';
          }
          return null;
        },
      ),
    );
  }

  // Shows the welcome screen with the app logo and login button
  Widget _buildWelcomeView() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 240),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Show the app logo
              Image.asset(
                'assets/app.png',
                width: 120,
                height: 120,
              ),

              const SizedBox(height: 16),

              // Show the app name
              const Text(
                "Mplayer",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFdfe8f0),
                ),
              ),

              const SizedBox(height: 48),

              // The main login button that switches to the login form
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF83bef2),
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: _toggleLoginForm,
                  child: const Text(
                    "Login",
                    style: TextStyle(fontSize: 16),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Link to sign up as a regular user
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Flexible(
                    child: Text(
                      "Don't have an account?",
                      style: TextStyle(color: Color(0xFFdfe8f0)),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      Navigator.pushReplacementNamed(context, '/register');
                    },
                    child: const Text(
                      "Sign up",
                      style: TextStyle(color: Color(0xFF83bef2)),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // Link to sign up as an artist
              TextButton(
                onPressed: () {
                  Navigator.pushReplacementNamed(context, '/artist-signup');
                },
                child: const Text(
                  "Sign up as an Artist",
                  style: TextStyle(color: Color(0xFF83bef2)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Shows the login form with username and password fields
  Widget _buildLoginForm() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 400),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                // Back button to go back to the welcome screen
                Row(
                  children: [
                    IconButton(
                      onPressed: _toggleLoginForm,
                      icon: const Icon(
                        Icons.arrow_back,
                        color: Color(0xFF83bef2),
                      ),
                    ),
                    const Text(
                      "Back to Welcome",
                      style: TextStyle(
                        color: Color(0xFF83bef2),
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                // Smaller app logo
                Image.asset(
                  'assets/app.png',
                  width: 80,
                  height: 80,
                ),

                const SizedBox(height: 16),

                // Welcome message
                const Text(
                  "Welcome Back",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFdfe8f0),
                  ),
                ),

                const SizedBox(height: 32),

                // The username and password fields
                _buildTextField(usernameController, "Username"),
                _buildTextField(passwordController, "Password", isPassword: true),
                const SizedBox(height: 24),

                // The login button that tries to log the user in
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 240),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _onLogin, // Don't let them click while loading
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
                          : const Text("Login"),
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // Link to sign up if they don't have an account
                TextButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/register');
                  },
                  child: const Text(
                    "Don't have an account? Sign up",
                    style: TextStyle(color: Color(0xFF83bef2)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // This decides whether to show the welcome screen or the login form
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF212529), // Dark background
      body: _showLoginForm ? _buildLoginForm() : _buildWelcomeView(),
    );
  }
}
