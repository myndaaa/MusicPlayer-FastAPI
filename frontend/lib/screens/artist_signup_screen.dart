import 'package:flutter/material.dart';

class ArtistSignupScreen extends StatefulWidget {
  const ArtistSignupScreen({super.key});

  @override
  State<ArtistSignupScreen> createState() => _ArtistSignupScreenState();
}

class _ArtistSignupScreenState extends State<ArtistSignupScreen> {
  final _formKey = GlobalKey<FormState>();

  // Text controllers
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final usernameController = TextEditingController();
  final stageNameController = TextEditingController();
  final bioController = TextEditingController();

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    firstNameController.dispose();
    lastNameController.dispose();
    usernameController.dispose();
    stageNameController.dispose();
    bioController.dispose();
    super.dispose();
  }

  void _onArtistRegister() {
    if (_formKey.currentState!.validate()) {
      // TODO: Connect to API
      print("Registering artist...");
      print("Email: ${emailController.text}");
      print("Password: ${passwordController.text}");
      print("First Name: ${firstNameController.text}");
      print("Last Name: ${lastNameController.text}");
      print("Username: ${usernameController.text}");
      print("Stage Name: ${stageNameController.text}");
      print("Bio: ${bioController.text}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF212529),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text("Sign Up as an Artist"),
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
                  _buildTextField(firstNameController, "First Name"),
                  _buildTextField(lastNameController, "Last Name"),
                  _buildTextField(usernameController, "Username"),
                  _buildTextField(emailController, "Email", isEmail: true),
                  _buildTextField(passwordController, "Password", isPassword: true),
                  _buildTextField(stageNameController, "Stage Name"),
                  _buildTextField(bioController, "Bio", maxLines: 3),
                  const SizedBox(height: 18),

                  ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 240),
                    child: SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _onArtistRegister,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF83bef2),
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text("Register as Artist"),
                      ),
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
        int maxLines = 1,
      }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: TextFormField(
        controller: controller,
        obscureText: isPassword,
        keyboardType: isEmail ? TextInputType.emailAddress : TextInputType.text,
        style: const TextStyle(color: Color(0xFFdfe8f0)),
        maxLines: maxLines,
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
