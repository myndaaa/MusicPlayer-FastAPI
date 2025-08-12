import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/genre_service.dart';
import '../constants/app_constants.dart';
import 'custom_text_field.dart';
import 'custom_button.dart';

class GenreCreateWidget extends StatefulWidget {
  final VoidCallback? onGenreCreated;

  const GenreCreateWidget({
    super.key,
    this.onGenreCreated,
  });

  @override
  State<GenreCreateWidget> createState() => _GenreCreateWidgetState();
}

class _GenreCreateWidgetState extends State<GenreCreateWidget> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _genreService = GenreService();
  
  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _handleCreateGenre() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
        _successMessage = null;
      });

      try {
        final result = await _genreService.createGenre(
          name: _nameController.text.trim(),
          description: _descriptionController.text.trim().isNotEmpty 
              ? _descriptionController.text.trim() 
              : null,
        );

        if (result != null) {
          setState(() {
            _successMessage = 'Genre "${_nameController.text.trim()}" created successfully!';
            _nameController.clear();
            _descriptionController.clear();
          });
          
          widget.onGenreCreated?.call();
          
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted) {
              setState(() {
                _successMessage = null;
              });
            }
          });
        } else {
          setState(() {
            _errorMessage = 'Failed to create genre';
          });
        }
      } catch (e) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception: ', '');
        });
      } finally {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSizes.paddingLarge),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(
                  Icons.add_circle_outline,
                  color: AppColors.primary,
                  size: 24,
                ),
                const SizedBox(width: AppSizes.paddingMedium),
                Text(
                  'Create New Genre',
                  style: AppTextStyles.heading2.copyWith(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ).animate().fadeIn().slideX(begin: -0.2),
            
            const SizedBox(height: AppSizes.paddingLarge),
            
            CustomTextField(
              label: 'Genre Name',
              hint: 'Enter genre name (e.g., Rock, Pop, Jazz)',
              controller: _nameController,
              prefixIcon: Icons.music_note,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a genre name';
                }
                if (value.trim().length < 2) {
                  return 'Genre name must be at least 2 characters';
                }
                if (value.trim().length > 255) {
                  return 'Genre name must be less than 255 characters';
                }
                return null;
              },
            ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2),
            
            const SizedBox(height: AppSizes.paddingMedium),
            
            CustomTextField(
              label: 'Description (Optional)',
              hint: 'Enter genre description',
              controller: _descriptionController,
              prefixIcon: Icons.description,
              maxLines: 3,
            ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.2),
            
            if (_errorMessage != null) ...[
              const SizedBox(height: AppSizes.paddingMedium),
              Container(
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
                  ],
                ),
              ).animate().fadeIn().slideX(begin: -0.2),
            ],
            
            if (_successMessage != null) ...[
              const SizedBox(height: AppSizes.paddingMedium),
              Container(
                padding: const EdgeInsets.all(AppSizes.paddingMedium),
                decoration: BoxDecoration(
                  color: AppColors.success.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(AppSizes.radiusSmall),
                  border: Border.all(
                    color: AppColors.success.withValues(alpha: 0.3),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.check_circle_outline,
                      color: AppColors.success,
                      size: 18,
                    ),
                    const SizedBox(width: AppSizes.paddingSmall),
                    Expanded(
                      child: Text(
                        _successMessage!,
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.success,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn().slideX(begin: -0.2),
            ],
            
            const SizedBox(height: AppSizes.paddingLarge),
            
            CustomButton(
              text: 'Create Genre',
              onPressed: _handleCreateGenre,
              isLoading: _isLoading,
              width: double.infinity,
              height: 45,
              icon: Icons.add,
            ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2),
          ],
        ),
      ),
    );
  }
}
