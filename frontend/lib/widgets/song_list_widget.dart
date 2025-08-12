import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/song_service.dart';
import '../constants/app_constants.dart';
import 'custom_button.dart';
import 'custom_text_field.dart';

class SongListWidget extends StatefulWidget {
  final Function(Map<String, dynamic>)? onSongSelected;
  final bool showSearch;
  final int? artistId;
  final int? genreId;

  const SongListWidget({
    super.key,
    this.onSongSelected,
    this.showSearch = true,
    this.artistId,
    this.genreId,
  });

  @override
  State<SongListWidget> createState() => _SongListWidgetState();
}

class _SongListWidgetState extends State<SongListWidget> {
  final SongService _songService = SongService();
  final TextEditingController _searchController = TextEditingController();
  
  List<Map<String, dynamic>> _songs = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  String? _errorMessage;
  int _currentPage = 0;
  int _totalSongs = 0;
  bool _hasMoreSongs = true;
  String? _searchQuery;

  @override
  void initState() {
    super.initState();
    _loadSongs();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadSongs({bool refresh = false}) async {
    if (refresh) {
      setState(() {
        _currentPage = 0;
        _songs = [];
        _hasMoreSongs = true;
      });
    }

    if (!_hasMoreSongs && !refresh) return;

    setState(() {
      if (refresh) {
        _isLoading = true;
      } else {
        _isLoadingMore = true;
      }
      _errorMessage = null;
    });

    try {
      List<Map<String, dynamic>> songs;
      
      if (_searchQuery != null && _searchQuery!.isNotEmpty) {
        songs = await _songService.searchSongs(
          query: _searchQuery!,
          skip: _currentPage * 20,
          limit: 20,
        );
      } else if (widget.artistId != null) {
        songs = await _songService.getSongsByArtist(
          artistId: widget.artistId!,
          skip: _currentPage * 20,
          limit: 20,
        );
      } else if (widget.genreId != null) {
        songs = await _songService.getSongsByGenre(
          genreId: widget.genreId!,
          skip: _currentPage * 20,
          limit: 20,
        );
      } else {
        songs = await _songService.getAllSongs(
          skip: _currentPage * 20,
          limit: 20,
        );
      }

      setState(() {
        if (refresh) {
          _songs = songs;
        } else {
          _songs.addAll(songs);
        }
        _currentPage++;
        _hasMoreSongs = songs.length == 20;
        _isLoading = false;
        _isLoadingMore = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load songs: ${e.toString()}';
        _isLoading = false;
        _isLoadingMore = false;
      });
    }
  }

  void _handleSearch(String query) {
    setState(() {
      _searchQuery = query.isEmpty ? null : query;
    });
    _loadSongs(refresh: true);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(AppSizes.paddingLarge),
            child: Row(
              children: [
                Icon(
                  Icons.music_note,
                  color: AppColors.primary,
                  size: 24,
                ),
                const SizedBox(width: AppSizes.paddingMedium),
                Text(
                  widget.artistId != null 
                      ? 'Artist Songs'
                      : widget.genreId != null
                          ? 'Genre Songs'
                          : 'All Songs',
                  style: AppTextStyles.heading2.copyWith(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: () => _loadSongs(refresh: true),
                  icon: Icon(
                    Icons.refresh,
                    color: AppColors.textSecondary,
                    size: 20,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn().slideX(begin: -0.2),
          
          if (widget.showSearch) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSizes.paddingLarge),
              child: CustomTextField(
                label: 'Search Songs',
                hint: 'Search by title, artist, or band',
                controller: _searchController,
                prefixIcon: Icons.search,
                onChanged: (value) {
                  // Debounce search
                  Future.delayed(const Duration(milliseconds: 500), () {
                    if (_searchController.text == value) {
                      _handleSearch(value);
                    }
                  });
                },
              ),
            ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2),
            
            const SizedBox(height: AppSizes.paddingMedium),
          ],
          
          if (_isLoading) ...[
            const Padding(
              padding: EdgeInsets.all(AppSizes.paddingLarge),
              child: Center(
                child: CircularProgressIndicator(
                  color: AppColors.primary,
                ),
              ),
            ),
          ] else if (_errorMessage != null) ...[
            Padding(
              padding: const EdgeInsets.all(AppSizes.paddingLarge),
              child: Container(
                padding: const EdgeInsets.all(AppSizes.paddingMedium),
                decoration: BoxDecoration(
                  color: AppColors.error.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
                  border: Border.all(
                    color: AppColors.error.withValues(alpha: 0.3),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.error_outline,
                      color: AppColors.error,
                      size: 18,
                    ),
                    const SizedBox(width: AppSizes.paddingSmall),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.error,
                          fontSize: 13,
                        ),
                      ),
                    ),
                    CustomButton(
                      text: 'Retry',
                      onPressed: () => _loadSongs(refresh: true),
                      isOutlined: true,
                      height: 32,
                    ),
                  ],
                ),
              ),
            ),
          ] else if (_songs.isEmpty) ...[
            Padding(
              padding: const EdgeInsets.all(AppSizes.paddingLarge),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.music_off,
                      color: AppColors.textSecondary,
                      size: 48,
                    ),
                    const SizedBox(height: AppSizes.paddingMedium),
                    Text(
                      _searchQuery != null ? 'No songs found' : 'No songs available',
                      style: AppTextStyles.body1.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ] else ...[
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: AppSizes.paddingLarge),
                itemCount: _songs.length + (_hasMoreSongs ? 1 : 0),
                itemBuilder: (context, index) {
                  if (index == _songs.length) {
                    return _buildLoadMoreButton();
                  }
                  
                  final song = _songs[index];
                  return _buildSongCard(song, index);
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSongCard(Map<String, dynamic> song, int index) {
    final title = song['title'] ?? '';
    final artistName = song['artist_name'];
    final bandName = song['band_name'];
    final genre = song['genre'];
    final duration = song['song_duration'] ?? 0;
    final coverImage = song['cover_image'];
    
    return Container(
      margin: const EdgeInsets.only(bottom: AppSizes.paddingMedium),
      decoration: BoxDecoration(
        gradient: AppGradients.cardGradient,
        borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.3),
        ),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(AppSizes.paddingMedium),
        leading: Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
            gradient: coverImage != null 
                ? null 
                : AppGradients.primaryGradient,
          ),
          child: coverImage != null
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
                  child: Image.network(
                    coverImage,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        decoration: BoxDecoration(
                          gradient: AppGradients.primaryGradient,
                          borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
                        ),
                        child: const Icon(
                          Icons.music_note,
                          color: AppColors.textPrimary,
                          size: 24,
                        ),
                      );
                    },
                  ),
                )
              : const Icon(
                  Icons.music_note,
                  color: AppColors.textPrimary,
                  size: 24,
                ),
        ),
        title: Text(
          title,
          style: AppTextStyles.body1.copyWith(
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (artistName != null || bandName != null)
              Text(
                artistName ?? bandName ?? '',
                style: AppTextStyles.body2.copyWith(
                  color: AppColors.textSecondary,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            if (genre != null)
              Text(
                genre['name'] ?? '',
                style: AppTextStyles.body2.copyWith(
                  color: AppColors.textSecondary,
                  fontSize: 12,
                ),
              ),
            Text(
              _songService.formatDuration(duration),
              style: AppTextStyles.body2.copyWith(
                color: AppColors.textSecondary,
                fontSize: 12,
              ),
            ),
          ],
        ),
        trailing: widget.onSongSelected != null
            ? IconButton(
                onPressed: () => widget.onSongSelected!(song),
                icon: const Icon(
                  Icons.play_circle_outline,
                  color: AppColors.primary,
                  size: 32,
                ),
              )
            : null,
        onTap: widget.onSongSelected != null
            ? () => widget.onSongSelected!(song)
            : null,
      ),
    ).animate().fadeIn(delay: (index * 50).ms).slideX(begin: 0.2);
  }

  Widget _buildLoadMoreButton() {
    return Padding(
      padding: const EdgeInsets.all(AppSizes.paddingMedium),
      child: Center(
        child: _isLoadingMore
            ? const CircularProgressIndicator(
                color: AppColors.primary,
              )
            : CustomButton(
                text: 'Load More',
                onPressed: _loadSongs,
                isOutlined: true,
                height: 40,
                icon: Icons.expand_more,
              ),
      ),
    );
  }
}
