import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// This service handles all the login/logout stuff and talks to backend
class AuthService {

  static const String baseUrl = 'http://localhost:8000';
  
  // keeps tokens safe and encrypted on the phone
  static const FlutterSecureStorage _secureStorage = FlutterSecureStorage();
  
  // stores basic user info like email and username
  static late SharedPreferences _prefs;
  
  // Sets up everything needed to store user data
  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }
  
  // Tries to log the user in by sending their username and password to backend
  // If it works, it saves the tokens and user info for later use
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      // Send the login request to backend
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'username': username, // Backend expects username field
          'password': password,
        }),
      );
      
      // Check what the backend sent back aka parse the response
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        // Login worked. Save the tokens so to use them later
        await _secureStorage.write(key: 'access_token', value: data['access_token']);
        await _secureStorage.write(key: 'refresh_token', value: data['refresh_token']);
        
        // Also save basic user info for easy access
        await _prefs.setString('user_email', data['email'] ?? '');
        await _prefs.setString('user_username', data['username'] ?? '');
        await _prefs.setString('user_role', data['role'] ?? '');
        await _prefs.setBool('is_logged_in', true);
        
        return {'success': true, 'data': data};
      } else {
        // Login failed n tell the user what went wrong
        return {'success': false, 'error': data['detail'] ?? 'Login failed'};
      }
    } catch (e) {
      // Something went wrong with the network or the request
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // Creates a new user account by sending registration data to backend
  static Future<Map<String, dynamic>> register({
    required String username,
    required String firstName,
    required String lastName,
    required String email,
    required String password,
  }) async {
    try {
      // Send registration request to backend
      final response = await http.post(
        Uri.parse('$baseUrl/user/signup'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'username': username,
          'first_name': firstName,
          'last_name': lastName,
          'email': email,
          'password': password,
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        // Registration successful
        return {'success': true, 'data': data};
      } else {
        // Registration failed
        return {'success': false, 'error': data['detail'] ?? 'Registration failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  // Logs the user out by telling the backend to forget their tokens
  // Then clears all the stored data from the phone
  static Future<void> logout() async {
    try {
      // Get the tokens we have stored
      final accessToken = await _secureStorage.read(key: 'access_token');
      final refreshToken = await _secureStorage.read(key: 'refresh_token');
      
      // Tell the backend to forget about this user's session
      if (accessToken != null && refreshToken != null) {
        await http.post(
          Uri.parse('$baseUrl/auth/logout'),
          headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'refresh_token': refreshToken,
          }),
        );
      }
    } catch (e) {
      // Even if the backend call fails, still clear local data
      print('Logout API call failed: $e');
    }
    
    // Clear everything we stored about the user
    await _secureStorage.deleteAll();
    await _prefs.clear();
  }
  
  // Checks if the user is logged in by seeing if we have a token stored
  static Future<bool> isLoggedIn() async {
    final accessToken = await _secureStorage.read(key: 'access_token');
    return accessToken != null;
  }
  
  // Gets the current access token (used by other parts of the app)
  static Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: 'access_token');
  }
  
  // When the access token expires, this gets a new one using the refresh token
  // This happens automatically when the user is using the app
  static Future<Map<String, dynamic>> refreshToken() async {
    try {
      final refreshToken = await _secureStorage.read(key: 'refresh_token');
      
      if (refreshToken == null) {
        return {'success': false, 'error': 'No refresh token available'};
      }
      
      // Ask the backend for a new access token
      final response = await http.post(
        Uri.parse('$baseUrl/auth/refresh'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'refresh_token': refreshToken,
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        // Save the new tokens
        await _secureStorage.write(key: 'access_token', value: data['access_token']);
        await _secureStorage.write(key: 'refresh_token', value: data['refresh_token']);
        
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Token refresh failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  // Gets the current user's info from the backend
  static Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final accessToken = await _secureStorage.read(key: 'access_token');
      
      if (accessToken == null) {
        return {'success': false, 'error': 'No access token available'};
      }
      
      // Ask the backend for the current user's info
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Failed to get user info'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
} 
