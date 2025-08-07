import 'package:flutter/material.dart';

class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  bool _showLoginForm = false;
  final _formKey = GlobalKey<FormState>();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void _onLogin() {
    if (_formKey.currentState!.validate()) {
      // TODO: Connect to API later
      print("Logging in...");
      print("Email: ${emailController.text}");
      print("Password: ${passwordController.text}");
      
      // Navigate to dashboard after successful login
      Navigator.pushNamed(context, '/dashboard');
    }
  }

  void _toggleLoginForm() {
    setState(() {
      _showLoginForm = !_showLoginForm;
    });
  }

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
          return null;
        },
      ),
    );
  }

  Widget _buildWelcomeView() {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 240),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo
              Image.asset(
                'assets/app.png',
                width: 120,
                height: 120,
              ),

              const SizedBox(height: 16),

              // App Name
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

              // Login Button
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

              // Sign up link
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
                      Navigator.pushNamed(context, '/register');
                    },
                    child: const Text(
                      "Sign up",
                      style: TextStyle(color: Color(0xFF83bef2)),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // Sign up as Artist button
              TextButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/artist-signup');
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
                // Back button
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

                // Logo
                Image.asset(
                  'assets/app.png',
                  width: 80,
                  height: 80,
                ),

                const SizedBox(height: 16),

                // Title
                const Text(
                  "Welcome Back",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFdfe8f0),
                  ),
                ),

                const SizedBox(height: 32),

                // Form fields
                _buildTextField(emailController, "Email", isEmail: true),
                _buildTextField(passwordController, "Password", isPassword: true),
                const SizedBox(height: 24),

                // Login button
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 240),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _onLogin,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF83bef2),
                        foregroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text("Login"),
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // Sign up link
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF212529),
      body: _showLoginForm ? _buildLoginForm() : _buildWelcomeView(),
    );
  }
}
