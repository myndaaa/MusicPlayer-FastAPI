import 'package:flutter/material.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();

  // Text controllers
  final usernameController = TextEditingController();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  @override
  void dispose() {
    usernameController.dispose();
    firstNameController.dispose();
    lastNameController.dispose();
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void _onRegister() {
    if (_formKey.currentState!.validate()) {
      // TODO: Connect to API later
      print("Registering...");
      print("Username: ${usernameController.text}");
      print("First name: ${firstNameController.text}");
      print("Last name: ${lastNameController.text}");
      print("Email: ${emailController.text}");
      print("Password: ${passwordController.text}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF212529),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text("Sign Up"),
        centerTitle: true,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  _buildTextField(usernameController, "Username"),
                  _buildTextField(firstNameController, "First Name"),
                  _buildTextField(lastNameController, "Last Name"),
                  _buildTextField(emailController, "Email", isEmail: true),
                  _buildTextField(passwordController, "Password", isPassword: true),
                  const SizedBox(height: 24),

                  // Button with max width 240
                  ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 240),
                    child: SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _onRegister,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF83bef2),
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text("Sign Up"),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  TextButton(
                    onPressed: () {
                      Navigator.pushNamed(context, '/login');
                    },
                    child: const Text(
                      "Already have an account? Login",
                      style: TextStyle(color: Color(0xFF83bef2)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
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
}
