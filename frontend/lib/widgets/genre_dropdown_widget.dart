import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/genre_service.dart';
import '../constants/app_constants.dart';

class GenreDropdownWidget extends StatefulWidget {
  final int? selectedGenreId;
  final Function(Map<String, dynamic>)? onGenreSelected;
  final String? label;
  final String? hint;
  final String? Function(int?)? validator;

  const GenreDropdownWidget({
    super.key,
    this.selectedGenreId,
    this.onGenreSelected,
    this.label,
    this.hint,
    this.validator,
  });

  @override
  State<GenreDropdownWidget> createState() => _GenreDropdownWidgetState();
}

class _GenreDropdownWidgetState extends State<GenreDropdownWidget> {
  final GenreService _genreService = GenreService();
  List<Map<String, dynamic>> _genres = [];
  bool _isLoading = true;
  String? _errorMessage;
  Map<String, dynamic>? _selectedGenre;

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
      final genres = await _genreService.getAllGenres();
      
      setState(() {
        _genres = genres;
        _isLoading = false;
      });

      if (widget.selectedGenreId != null) {
        _selectedGenre = _genres.firstWhere(
          (genre) => genre['id'] == widget.selectedGenreId,
          orElse: () => _genres.isNotEmpty ? _genres.first : {},
        );
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load genres: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppSizes.paddingMedium),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (widget.label != null) ...[
            Text(
              widget.label!,
              style: AppTextStyles.body1.copyWith(
                fontWeight: FontWeight.w500,
                color: AppColors.textPrimary,
              ),
            ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.2),
            const SizedBox(height: AppSizes.paddingSmall),
          ],
          
          Container(
            decoration: BoxDecoration(
              gradient: AppGradients.cardGradient,
              borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
              border: Border.all(
                color: AppColors.primary.withValues(alpha: 0.3),
                width: 1,
              ),
            ),
            child: _isLoading
                ? Container(
                    padding: const EdgeInsets.all(AppSizes.paddingMedium),
                    child: const Row(
                      children: [
                        SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: AppColors.primary,
                          ),
                        ),
                        SizedBox(width: AppSizes.paddingMedium),
                        Text(
                          'Loading genres...',
                          style: AppTextStyles.body2,
                        ),
                      ],
                    ),
                  )
                : _errorMessage != null
                    ? Container(
                        padding: const EdgeInsets.all(AppSizes.paddingMedium),
                        child: Row(
                          children: [
                            Icon(
                              Icons.error_outline,
                              color: AppColors.error,
                              size: 16,
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
                            TextButton(
                              onPressed: _loadGenres,
                              child: const Text(
                                'Retry',
                                style: TextStyle(
                                  color: AppColors.primary,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ],
                        ),
                      )
                    : DropdownButtonFormField<Map<String, dynamic>>(
                        value: _selectedGenre,
                        decoration: InputDecoration(
                          hintText: widget.hint ?? 'Select a genre',
                          hintStyle: AppTextStyles.body2,
                          prefixIcon: const Icon(
                            Icons.music_note,
                            color: AppColors.textSecondary,
                            size: 20,
                          ),
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.all(AppSizes.paddingMedium),
                        ),
                        style: AppTextStyles.body1,
                        dropdownColor: AppColors.surface,
                        icon: const Icon(
                          Icons.arrow_drop_down,
                          color: AppColors.textSecondary,
                        ),
                        validator: widget.validator != null
                            ? (value) => widget.validator!(value?['id'])
                            : null,
                        onChanged: (Map<String, dynamic>? newValue) {
                          setState(() {
                            _selectedGenre = newValue;
                          });
                          if (newValue != null) {
                            widget.onGenreSelected?.call(newValue);
                          }
                        },
                        items: _genres.map<DropdownMenuItem<Map<String, dynamic>>>((genre) {
                          final isActive = genre['is_active'] ?? true;
                          return DropdownMenuItem<Map<String, dynamic>>(
                            value: genre,
                            child: Row(
                              children: [
                                Container(
                                  width: 12,
                                  height: 12,
                                  decoration: BoxDecoration(
                                    color: isActive ? AppColors.success : AppColors.textSecondary,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: AppSizes.paddingSmall),
                                Expanded(
                                  child: Text(
                                    genre['name'] ?? '',
                                    style: AppTextStyles.body1.copyWith(
                                      color: isActive ? AppColors.textPrimary : AppColors.textSecondary,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),
          ).animate().fadeIn(delay: 300.ms).slideX(begin: -0.1),
        ],
      ),
    );
  }
}
