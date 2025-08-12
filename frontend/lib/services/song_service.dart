import 'package:dio/dio.dart';
import 'api_service.dart';

class SongService {
  final ApiService _apiService = ApiService();

  Future<List<Map<String, dynamic>>> getAllSongs({
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get('/song/', queryParameters: {
        'skip': skip,
        'limit': limit,
      });
      
      if (response.statusCode == 200) {
        final List<dynamic> songs = response.data;
        return songs.cast<Map<String, dynamic>>();
      }
      
      return [];
    } on DioException catch (e) {
      print('Error fetching songs: $e');
      return [];
    } catch (e) {
      print('Unexpected error fetching songs: $e');
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> searchSongs({
    required String query,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get('/song/search', queryParameters: {
        'query': query,
        'skip': skip,
        'limit': limit,
      });
      
      if (response.statusCode == 200) {
        final List<dynamic> songs = response.data;
        return songs.cast<Map<String, dynamic>>();
      }
      
      return [];
    } on DioException catch (e) {
      print('Error searching songs: $e');
      return [];
    } catch (e) {
      print('Unexpected error searching songs: $e');
      return [];
    }
  }

  Future<Map<String, dynamic>?> getSongById(int songId) async {
    try {
      final response = await _apiService.get('/song/$songId');
      
      if (response.statusCode == 200) {
        return response.data;
      }
      
      return null;
    } on DioException catch (e) {
      print('Error fetching song: $e');
      return null;
    } catch (e) {
      print('Unexpected error fetching song: $e');
      return null;
    }
  }

  Future<List<Map<String, dynamic>>> getSongsByArtist({
    required int artistId,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get('/song/artist/$artistId', queryParameters: {
        'skip': skip,
        'limit': limit,
      });
      
      if (response.statusCode == 200) {
        final List<dynamic> songs = response.data;
        return songs.cast<Map<String, dynamic>>();
      }
      
      return [];
    } on DioException catch (e) {
      print('Error fetching artist songs: $e');
      return [];
    } catch (e) {
      print('Unexpected error fetching artist songs: $e');
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> getSongsByGenre({
    required int genreId,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get('/song/genre/$genreId', queryParameters: {
        'skip': skip,
        'limit': limit,
      });
      
      if (response.statusCode == 200) {
        final List<dynamic> songs = response.data;
        return songs.cast<Map<String, dynamic>>();
      }
      
      return [];
    } on DioException catch (e) {
      print('Error fetching genre songs: $e');
      return [];
    } catch (e) {
      print('Unexpected error fetching genre songs: $e');
      return [];
    }
  }

  Future<Map<String, dynamic>?> uploadSongByArtist({
    required String title,
    required int genreId,
    required int artistId,
    required DateTime releaseDate,
    required int songDuration,
    required String filePath,
    String? coverImage,
  }) async {
    try {
      final response = await _apiService.post('/song/artist/upload', data: {
        'title': title,
        'genre_id': genreId,
        'artist_id': artistId,
        'release_date': releaseDate.toIso8601String(),
        'song_duration': songDuration,
        'file_path': filePath,
        if (coverImage != null) 'cover_image': coverImage,
      });

      if (response.statusCode == 201) {
        return response.data;
      }
      
      return null;
    } on DioException catch (e) {
      String errorMessage = 'Failed to upload song';
      
      if (e.response?.statusCode == 400) {
        errorMessage = 'Invalid song data';
      } else if (e.response?.statusCode == 403) {
        errorMessage = 'You can only upload songs for your own artist profile';
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Network error. Please try again.');
    }
  }

  Future<Map<String, dynamic>?> uploadSongByBand({
    required String title,
    required int genreId,
    required int bandId,
    required DateTime releaseDate,
    required int songDuration,
    required String filePath,
    String? coverImage,
  }) async {
    try {
      final response = await _apiService.post('/song/band/upload', data: {
        'title': title,
        'genre_id': genreId,
        'band_id': bandId,
        'release_date': releaseDate.toIso8601String(),
        'song_duration': songDuration,
        'file_path': filePath,
        if (coverImage != null) 'cover_image': coverImage,
      });

      if (response.statusCode == 201) {
        return response.data;
      }
      
      return null;
    } on DioException catch (e) {
      String errorMessage = 'Failed to upload song';
      
      if (e.response?.statusCode == 400) {
        errorMessage = 'Invalid song data';
      } else if (e.response?.statusCode == 403) {
        errorMessage = 'You can only upload songs for bands you are a member of';
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Network error. Please try again.');
    }
  }

  Future<Map<String, dynamic>?> updateSongMetadata({
    required int songId,
    String? title,
    int? genreId,
    DateTime? releaseDate,
    int? songDuration,
    String? coverImage,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (title != null) data['title'] = title;
      if (genreId != null) data['genre_id'] = genreId;
      if (releaseDate != null) data['release_date'] = releaseDate.toIso8601String();
      if (songDuration != null) data['song_duration'] = songDuration;
      if (coverImage != null) data['cover_image'] = coverImage;

      final response = await _apiService.put('/song/$songId', data: data);

      if (response.statusCode == 200) {
        return response.data;
      }
      
      return null;
    } on DioException catch (e) {
      String errorMessage = 'Failed to update song';
      
      if (e.response?.statusCode == 404) {
        errorMessage = 'Song not found';
      } else if (e.response?.statusCode == 403) {
        errorMessage = 'You can only update your own songs';
      } else if (e.response?.data != null && e.response?.data['detail'] != null) {
        errorMessage = e.response!.data['detail'];
      }
      
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Network error. Please try again.');
    }
  }

  String formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final remainingSeconds = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}';
  }

  Future<bool> checkSongFileExists(int songId) async {
    try {
      final response = await _apiService.get('/stream/song/$songId/info');
      return response.statusCode == 200;
    } on DioException catch (e) {
      return false;
    } catch (e) {
      return false;
    }
  }
}
