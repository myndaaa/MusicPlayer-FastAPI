import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _apiService = ApiService();
  
  static const String _tokenKey = 'auth_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userDataKey = 'user_data';

  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await _apiService.post('/auth/login', data: {
        'username': username,
        'password': password,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        
        // Store tokens
        await _storeTokens(data['access_token'], data['refresh_token']);
        
        // Store user data
        await _storeUserData(data);
        
        // Set auth header for future requests
        _apiService.setAuthToken(data['access_token']);
        
        return {
          'success': true,
          'data': data,
        };
      }
      
      return {
        'success': false,
        'error': 'Login failed',
      };
    } on DioException catch (e) {
      String errorMessage = 'Login failed';
      
      if (e.response?.statusCode == 401) {
        errorMessage = 'Incorrect username or password';
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      return {
        'success': false,
        'error': errorMessage,
      };
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error. Please try again.',
      };
    }
  }

  Future<Map<String, dynamic>> userSignup({
    required String username,
    required String firstName,
    required String lastName,
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiService.post('/user/signup', data: {
        'username': username,
        'first_name': firstName,
        'last_name': lastName,
        'email': email,
        'password': password,
      });

      if (response.statusCode == 201) {
        return {
          'success': true,
          'message': 'Account created successfully! Please sign in.',
        };
      }
      
      return {
        'success': false,
        'error': 'Signup failed',
      };
    } on DioException catch (e) {
      String errorMessage = 'Signup failed';
      
      if (e.response?.statusCode == 409) {
        if (e.response?.data['detail']?.contains('Username') == true) {
          errorMessage = 'Username already exists';
        } else if (e.response?.data['detail']?.contains('Email') == true) {
          errorMessage = 'Email already registered';
        } else {
          errorMessage = e.response!.data['detail'];
        }
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      return {
        'success': false,
        'error': errorMessage,
      };
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error. Please try again.',
      };
    }
  }

  Future<Map<String, dynamic>> artistSignup({
    required String username,
    required String firstName,
    required String lastName,
    required String email,
    required String password,
    required String stageName,
    String? bio,
    Map<String, dynamic>? socialLinks,
  }) async {
    try {
      final response = await _apiService.post('/artist/signup', data: {
        'username': username,
        'first_name': firstName,
        'last_name': lastName,
        'email': email,
        'password': password,
        'artist_stage_name': stageName,
        'artist_bio': bio,
        'artist_social_link': socialLinks,
      });

      if (response.statusCode == 201) {
        return {
          'success': true,
          'message': 'Artist account created successfully! Please sign in.',
        };
      }
      
      return {
        'success': false,
        'error': 'Signup failed',
      };
    } on DioException catch (e) {
      String errorMessage = 'Signup failed';
      
      if (e.response?.statusCode == 409) {
        if (e.response?.data['detail']?.contains('Username') == true) {
          errorMessage = 'Username already exists';
        } else if (e.response?.data['detail']?.contains('Email') == true) {
          errorMessage = 'Email already registered';
        } else if (e.response?.data['detail']?.contains('stage name') == true) {
          errorMessage = 'Stage name already taken';
        } else {
          errorMessage = e.response!.data['detail'];
        }
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      return {
        'success': false,
        'error': errorMessage,
      };
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error. Please try again.',
      };
    }
  }

  Future<void> logout() async {
    try {
      final refreshToken = await _getRefreshToken();
      final accessToken = await _getToken();
      
      if (refreshToken != null && accessToken != null) {
        // Set the auth token before making the logout request
        _apiService.setAuthToken(accessToken);
        
        await _apiService.post('/auth/logout', data: {
          'refresh_token': refreshToken,
        });
      }
    } catch (e) {
      print('Logout error: $e');
      // Continue with logout even if API call fails
    } finally {
      await _clearTokens();
      _apiService.removeAuthToken();
    }
  }

  Future<bool> isLoggedIn() async {
    final token = await _getToken();
    return token != null;
  }

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<String?> _getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_refreshTokenKey);
  }

  Future<void> _storeTokens(String accessToken, String refreshToken) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, accessToken);
    await prefs.setString(_refreshTokenKey, refreshToken);
  }

  Future<void> _storeUserData(Map<String, dynamic> data) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userDataKey, jsonEncode(data));
  }

  Future<void> _clearTokens() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_refreshTokenKey);
    await prefs.remove(_userDataKey);
  }

  Future<Map<String, dynamic>?> getUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString(_userDataKey);
    if (userDataString != null) {
      return jsonDecode(userDataString);
    }
    return null;
  }
}
