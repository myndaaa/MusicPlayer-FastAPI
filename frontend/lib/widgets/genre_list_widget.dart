import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/genre_service.dart';
import '../constants/app_constants.dart';
import 'custom_button.dart';

class GenreListWidget extends StatefulWidget {
  final bool isAdmin;
  final Function(Map<String, dynamic>)? onGenreSelected;
  final bool showSelection;

  const GenreListWidget({
    super.key,
    this.isAdmin = false,
    this.onGenreSelected,
    this.showSelection = false,
  });

  @override
  State<GenreListWidget> createState() => _GenreListWidgetState();
}

class _GenreListWidgetState extends State<GenreListWidget> {
  final GenreService _genreService = GenreService();
  List<Map<String, dynamic>> _genres = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadGenres();
  }

  Future<void> _loadGenres() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final genres = widget.isAdmin 
          ? await _genreService.getAllGenresAdmin()
          : await _genreService.getAllGenres();
      
      setState(() {
        _genres = genres;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load genres: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  Future<void> _toggleGenreStatus(int genreId, bool isActive) async {
    try {
      bool success;
      if (isActive) {
        success = await _genreService.disableGenre(genreId);
      } else {
        success = await _genreService.enableGenre(genreId);
      }

      if (success) {
        _loadGenres();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Genre ${isActive ? 'disabled' : 'enabled'} successfully'),
              backgroundColor: AppColors.success,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update genre: ${e.toString()}'),
            backgroundColor: AppColors.error,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
            ),
          ),
        );
      }
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
                  Icons.music_note,
                  color: AppColors.primary,
                  size: 24,
                ),
                const SizedBox(width: AppSizes.paddingMedium),
                Text(
                  widget.isAdmin ? 'All Genres' : 'Available Genres',
                  style: AppTextStyles.heading2.copyWith(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                if (widget.isAdmin)
                  IconButton(
                    onPressed: _loadGenres,
                    icon: Icon(
                      Icons.refresh,
                      color: AppColors.textSecondary,
                      size: 20,
                    ),
                  ),
              ],
            ),
          ).animate().fadeIn().slideX(begin: -0.2),
          
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
                       onPressed: _loadGenres,
                       isOutlined: true,
                       height: 32,
                     ),
                  ],
                ),
              ),
            ),
          ] else if (_genres.isEmpty) ...[
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
                      'No genres found',
                      style: AppTextStyles.body1.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ] else ...[
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _genres.length,
              itemBuilder: (context, index) {
                final genre = _genres[index];
                final isActive = genre['is_active'] ?? true;
                
                return Container(
                  margin: const EdgeInsets.symmetric(
                    horizontal: AppSizes.paddingLarge,
                    vertical: AppSizes.paddingSmall,
                  ),
                  decoration: BoxDecoration(
                    gradient: AppGradients.cardGradient,
                    borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                    border: Border.all(
                      color: isActive 
                          ? AppColors.primary.withValues(alpha: 0.3)
                          : AppColors.textSecondary.withValues(alpha: 0.3),
                    ),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(AppSizes.paddingMedium),
                    leading: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        gradient: AppGradients.primaryGradient,
                        borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
                      ),
                      child: Icon(
                        Icons.music_note,
                        color: AppColors.textPrimary,
                        size: 20,
                      ),
                    ),
                    title: Text(
                      genre['name'] ?? '',
                      style: AppTextStyles.body1.copyWith(
                        fontWeight: FontWeight.w600,
                        color: isActive ? AppColors.textPrimary : AppColors.textSecondary,
                      ),
                    ),
                    subtitle: genre['description'] != null
                        ? Text(
                            genre['description'],
                            style: AppTextStyles.body2.copyWith(
                              color: isActive ? AppColors.textSecondary : AppColors.textSecondary.withValues(alpha: 0.5),
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          )
                        : null,
                    trailing: widget.isAdmin
                        ? Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              if (!isActive)
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: AppSizes.paddingSmall,
                                    vertical: 4,
                                  ),
                                  decoration: BoxDecoration(
                                    color: AppColors.textSecondary.withValues(alpha: 0.2),
                                    borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
                                  ),
                                  child: Text(
                                    'Disabled',
                                    style: AppTextStyles.body2.copyWith(
                                      fontSize: 12,
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                ),
                              const SizedBox(width: AppSizes.paddingSmall),
                              IconButton(
                                onPressed: () => _toggleGenreStatus(
                                  genre['id'],
                                  isActive,
                                ),
                                icon: Icon(
                                  isActive ? Icons.block : Icons.check_circle,
                                  color: isActive ? AppColors.error : AppColors.success,
                                  size: 20,
                                ),
                              ),
                            ],
                          )
                        : widget.showSelection
                            ? Icon(
                                Icons.arrow_forward_ios,
                                color: AppColors.textSecondary,
                                size: 16,
                              )
                            : null,
                    onTap: widget.showSelection
                        ? () => widget.onGenreSelected?.call(genre)
                        : null,
                  ),
                ).animate().fadeIn(delay: (index * 50).ms).slideX(begin: 0.2);
              },
            ),
          ],
        ],
      ),
    );
  }
}
