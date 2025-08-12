import 'package:dio/dio.dart';
import 'api_service.dart';

class GenreService {
  final ApiService _apiService = ApiService();

  Future<List<Map<String, dynamic>>> getAllGenres() async {
    try {
      final response = await _apiService.get('/genre/');
      
      if (response.statusCode == 200) {
        final List<dynamic> genres = response.data;
        return genres.cast<Map<String, dynamic>>();
      }
      
      return [];
    } on DioException catch (e) {
      print('Error fetching genres: $e');
      return [];
    } catch (e) {
      print('Unexpected error fetching genres: $e');
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> getAllGenresAdmin() async {
    try {
      final response = await _apiService.get('/genre/admin/all');
      
      if (response.statusCode == 200) {
        final List<dynamic> genres = response.data;
        return genres.cast<Map<String, dynamic>>();
      }
      
      return [];
    } on DioException catch (e) {
      print('Error fetching all genres (admin): $e');
      return [];
    } catch (e) {
      print('Unexpected error fetching all genres (admin): $e');
      return [];
    }
  }

  Future<Map<String, dynamic>?> createGenre({
    required String name,
    String? description,
  }) async {
    try {
      final response = await _apiService.post('/genre/', data: {
        'name': name,
        if (description != null) 'description': description,
      });

      if (response.statusCode == 201) {
        return response.data;
      }
      
      return null;
    } on DioException catch (e) {
      String errorMessage = 'Failed to create genre';
      
      if (e.response?.statusCode == 409) {
        errorMessage = 'Genre name already exists';
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Network error. Please try again.');
    }
  }

  Future<Map<String, dynamic>?> updateGenre({
    required int genreId,
    String? name,
    String? description,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (name != null) data['name'] = name;
      if (description != null) data['description'] = description;

      final response = await _apiService.put('/genre/$genreId', data: data);

      if (response.statusCode == 200) {
        return response.data;
      }
      
      return null;
    } on DioException catch (e) {
      String errorMessage = 'Failed to update genre';
      
      if (e.response?.statusCode == 409) {
        errorMessage = 'Genre name already exists';
      } else if (e.response?.statusCode == 404) {
        errorMessage = 'Genre not found';
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Network error. Please try again.');
    }
  }

  Future<bool> disableGenre(int genreId) async {
    try {
      final response = await _apiService.post('/genre/$genreId/disable');
      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error disabling genre: $e');
      return false;
    } catch (e) {
      print('Unexpected error disabling genre: $e');
      return false;
    }
  }

  Future<bool> enableGenre(int genreId) async {
    try {
      final response = await _apiService.post('/genre/$genreId/enable');
      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error enabling genre: $e');
      return false;
    } catch (e) {
      print('Unexpected error enabling genre: $e');
      return false;
    }
  }

  Future<Map<String, dynamic>?> getGenreStatistics() async {
    try {
      final response = await _apiService.get('/genre/admin/statistics');
      
      if (response.statusCode == 200) {
        return response.data;
      }
      
      return null;
    } on DioException catch (e) {
      print('Error fetching genre statistics: $e');
      return null;
    } catch (e) {
      print('Unexpected error fetching genre statistics: $e');
      return null;
    }
  }
}
