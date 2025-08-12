import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/song_service.dart';
import '../services/genre_service.dart';
import '../constants/app_constants.dart';
import 'custom_text_field.dart';
import 'custom_button.dart';
import 'genre_dropdown_widget.dart';

class SongSearchWidget extends StatefulWidget {
  final Function(Map<String, dynamic>)? onSongSelected;
  final bool showFilters;

  const SongSearchWidget({
    super.key,
    this.onSongSelected,
    this.showFilters = true,
  });

  @override
  State<SongSearchWidget> createState() => _SongSearchWidgetState();
}

class _SongSearchWidgetState extends State<SongSearchWidget> {
  final SongService _songService = SongService();
  final TextEditingController _searchController = TextEditingController();
  
  List<Map<String, dynamic>> _searchResults = [];
  bool _isLoading = false;
  bool _isLoadingMore = false;
  String? _errorMessage;
  int _currentPage = 0;
  bool _hasMoreResults = true;
  String _searchQuery = '';
  int? _selectedGenreId;
  bool _showFilters = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _performSearch({bool refresh = false}) async {
    if (_searchQuery.trim().isEmpty) {
      setState(() {
        _searchResults = [];
        _isLoading = false;
        _isLoadingMore = false;
      });
      return;
    }

    if (refresh) {
      setState(() {
        _currentPage = 0;
        _searchResults = [];
        _hasMoreResults = true;
      });
    }

    if (!_hasMoreResults && !refresh) return;

    setState(() {
      if (refresh) {
        _isLoading = true;
      } else {
        _isLoadingMore = true;
      }
      _errorMessage = null;
    });

    try {
      final songs = await _songService.searchSongs(
        query: _searchQuery.trim(),
        skip: _currentPage * 20,
        limit: 20,
      );

      setState(() {
        if (refresh) {
          _searchResults = songs;
        } else {
          _searchResults.addAll(songs);
        }
        _currentPage++;
        _hasMoreResults = songs.length == 20;
        _isLoading = false;
        _isLoadingMore = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to search songs: ${e.toString()}';
        _isLoading = false;
        _isLoadingMore = false;
      });
    }
  }

  void _handleSearch(String query) {
    setState(() {
      _searchQuery = query;
    });
    
    if (query.trim().isNotEmpty) {
      _performSearch(refresh: true);
    } else {
      setState(() {
        _searchResults = [];
        _isLoading = false;
        _isLoadingMore = false;
      });
    }
  }

  void _loadMoreResults() {
    if (_hasMoreResults && !_isLoadingMore) {
      _performSearch();
    }
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
                  Icons.search,
                  color: AppColors.primary,
                  size: 24,
                ),
                const SizedBox(width: AppSizes.paddingMedium),
                Text(
                  'Search Songs',
                  style: AppTextStyles.heading2.copyWith(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                if (widget.showFilters)
                  IconButton(
                    onPressed: () {
                      setState(() {
                        _showFilters = !_showFilters;
                      });
                    },
                    icon: Icon(
                      _showFilters ? Icons.filter_list_off : Icons.filter_list,
                      color: AppColors.textSecondary,
                      size: 20,
                    ),
                  ),
              ],
            ),
          ).animate().fadeIn().slideX(begin: -0.2),
          
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppSizes.paddingLarge),
            child: CustomTextField(
              label: 'Search',
              hint: 'Search by song title, artist, or band name',
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
          
          if (widget.showFilters && _showFilters) ...[
            const SizedBox(height: AppSizes.paddingMedium),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSizes.paddingLarge),
              child: GenreDropdownWidget(
                label: 'Filter by Genre',
                hint: 'All genres',
                onGenreSelected: (genre) {
                  setState(() {
                    _selectedGenreId = genre['id'];
                  });
                  // Re-filter results based on genre
                  if (_searchQuery.trim().isNotEmpty) {
                    _performSearch(refresh: true);
                  }
                },
              ),
            ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.2),
          ],
          
          const SizedBox(height: AppSizes.paddingMedium),
          
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
                      onPressed: () => _performSearch(refresh: true),
                      isOutlined: true,
                      height: 32,
                    ),
                  ],
                ),
              ),
            ),
          ] else if (_searchQuery.trim().isEmpty) ...[
            Padding(
              padding: const EdgeInsets.all(AppSizes.paddingLarge),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.search,
                      color: AppColors.textSecondary,
                      size: 48,
                    ),
                    const SizedBox(height: AppSizes.paddingMedium),
                    Text(
                      'Search for songs',
                      style: AppTextStyles.body1.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: AppSizes.paddingSmall),
                    Text(
                      'Enter a song title, artist, or band name',
                      style: AppTextStyles.body2.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ] else if (_searchResults.isEmpty) ...[
            Padding(
              padding: const EdgeInsets.all(AppSizes.paddingLarge),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.search_off,
                      color: AppColors.textSecondary,
                      size: 48,
                    ),
                    const SizedBox(height: AppSizes.paddingMedium),
                    Text(
                      'No songs found',
                      style: AppTextStyles.body1.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: AppSizes.paddingSmall),
                    Text(
                      'Try different keywords or check your spelling',
                      style: AppTextStyles.body2.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ] else ...[
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: AppSizes.paddingLarge),
                    child: Text(
                      '${_searchResults.length} result${_searchResults.length == 1 ? '' : 's'} found',
                      style: AppTextStyles.body2.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(height: AppSizes.paddingSmall),
                  Expanded(
                    child: ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: AppSizes.paddingLarge),
                      itemCount: _searchResults.length + (_hasMoreResults ? 1 : 0),
                      itemBuilder: (context, index) {
                        if (index == _searchResults.length) {
                          return _buildLoadMoreButton();
                        }
                        
                        final song = _searchResults[index];
                        return _buildSongCard(song, index);
                      },
                    ),
                  ),
                ],
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
                onPressed: _loadMoreResults,
                isOutlined: true,
                height: 40,
                icon: Icons.expand_more,
              ),
      ),
    );
  }
}
