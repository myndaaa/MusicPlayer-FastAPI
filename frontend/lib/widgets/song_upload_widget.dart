import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:file_picker/file_picker.dart';
import 'package:intl/intl.dart';
import '../services/song_service.dart';
import '../services/genre_service.dart';
import '../constants/app_constants.dart';
import 'custom_text_field.dart';
import 'custom_button.dart';
import 'genre_dropdown_widget.dart';

class SongUploadWidget extends StatefulWidget {
  final bool isArtist;
  final int? artistId;
  final int? bandId;
  final VoidCallback? onSongUploaded;

  const SongUploadWidget({
    super.key,
    this.isArtist = true,
    this.artistId,
    this.bandId,
    this.onSongUploaded,
  });

  @override
  State<SongUploadWidget> createState() => _SongUploadWidgetState();
}

class _SongUploadWidgetState extends State<SongUploadWidget> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _songService = SongService();
  final _genreService = GenreService();
  
  DateTime? _selectedReleaseDate;
  int? _selectedGenreId;
  PlatformFile? _selectedAudioFile;
  PlatformFile? _selectedCoverFile;
  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _titleController.dispose();
    super.dispose();
  }

  Future<void> _selectReleaseDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.dark(
              primary: AppColors.primary,
              onPrimary: AppColors.textPrimary,
              surface: AppColors.surface,
              onSurface: AppColors.textPrimary,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        _selectedReleaseDate = picked;
      });
    }
  }

  Future<void> _pickAudioFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.audio,
        allowMultiple: false,
      );

      if (result != null) {
        setState(() {
          _selectedAudioFile = result.files.first;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick audio file: $e';
      });
    }
  }

  Future<void> _pickCoverFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: false,
      );

      if (result != null) {
        setState(() {
          _selectedCoverFile = result.files.first;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick cover image: $e';
      });
    }
  }

  Future<void> _handleUpload() async {
    if (_formKey.currentState!.validate()) {
      if (_selectedAudioFile == null) {
        setState(() {
          _errorMessage = 'Please select an audio file';
        });
        return;
      }

      if (_selectedGenreId == null) {
        setState(() {
          _errorMessage = 'Please select a genre';
        });
        return;
      }

      if (_selectedReleaseDate == null) {
        setState(() {
          _errorMessage = 'Please select a release date';
        });
        return;
      }

      setState(() {
        _isLoading = true;
        _errorMessage = null;
        _successMessage = null;
      });

      try {
        // For now, we'll simulate the upload process
        // In a real app, you'd upload the file first, then create the song record
        final songDuration = 180; // This would be extracted from the audio file
        final filePath = _selectedAudioFile!.path ?? '';
        final coverImage = _selectedCoverFile?.path;

        Map<String, dynamic>? result;
        
        if (widget.isArtist && widget.artistId != null) {
          result = await _songService.uploadSongByArtist(
            title: _titleController.text.trim(),
            genreId: _selectedGenreId!,
            artistId: widget.artistId!,
            releaseDate: _selectedReleaseDate!,
            songDuration: songDuration,
            filePath: filePath,
            coverImage: coverImage,
          );
        } else if (!widget.isArtist && widget.bandId != null) {
          result = await _songService.uploadSongByBand(
            title: _titleController.text.trim(),
            genreId: _selectedGenreId!,
            bandId: widget.bandId!,
            releaseDate: _selectedReleaseDate!,
            songDuration: songDuration,
            filePath: filePath,
            coverImage: coverImage,
          );
        }

        if (result != null) {
          setState(() {
            _successMessage = 'Song "${_titleController.text.trim()}" uploaded successfully!';
            _titleController.clear();
            _selectedReleaseDate = null;
            _selectedGenreId = null;
            _selectedAudioFile = null;
            _selectedCoverFile = null;
          });
          
          widget.onSongUploaded?.call();
          
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted) {
              setState(() {
                _successMessage = null;
              });
            }
          });
        } else {
          setState(() {
            _errorMessage = 'Failed to upload song';
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
                  Icons.upload_file,
                  color: AppColors.primary,
                  size: 24,
                ),
                const SizedBox(width: AppSizes.paddingMedium),
                Text(
                  'Upload New Song',
                  style: AppTextStyles.heading2.copyWith(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ).animate().fadeIn().slideX(begin: -0.2),
            
            const SizedBox(height: AppSizes.paddingLarge),
            
            CustomTextField(
              label: 'Song Title',
              hint: 'Enter song title',
              controller: _titleController,
              prefixIcon: Icons.music_note,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a song title';
                }
                if (value.trim().length > 150) {
                  return 'Song title must be less than 150 characters';
                }
                return null;
              },
            ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2),
            
            const SizedBox(height: AppSizes.paddingMedium),
            
            GenreDropdownWidget(
              label: 'Genre',
              hint: 'Select a genre',
              onGenreSelected: (genre) {
                setState(() {
                  _selectedGenreId = genre['id'];
                });
              },
              validator: (genreId) {
                if (genreId == null) {
                  return 'Please select a genre';
                }
                return null;
              },
            ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.2),
            
            const SizedBox(height: AppSizes.paddingMedium),
            
            // Release Date Picker
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Release Date',
                  style: AppTextStyles.body1.copyWith(
                    fontWeight: FontWeight.w500,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: AppSizes.paddingSmall),
                Container(
                  decoration: BoxDecoration(
                    gradient: AppGradients.cardGradient,
                    borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                    border: Border.all(
                      color: AppColors.primary.withValues(alpha: 0.3),
                      width: 1,
                    ),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(AppSizes.paddingMedium),
                    leading: const Icon(
                      Icons.calendar_today,
                      color: AppColors.textSecondary,
                      size: 20,
                    ),
                    title: Text(
                      _selectedReleaseDate != null
                          ? DateFormat('MMM dd, yyyy').format(_selectedReleaseDate!)
                          : 'Select release date',
                      style: AppTextStyles.body1.copyWith(
                        color: _selectedReleaseDate != null 
                            ? AppColors.textPrimary 
                            : AppColors.textSecondary,
                      ),
                    ),
                    trailing: const Icon(
                      Icons.arrow_drop_down,
                      color: AppColors.textSecondary,
                    ),
                    onTap: _selectReleaseDate,
                  ),
                ),
              ],
            ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2),
            
            const SizedBox(height: AppSizes.paddingMedium),
            
            // Audio File Picker
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Audio File',
                  style: AppTextStyles.body1.copyWith(
                    fontWeight: FontWeight.w500,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: AppSizes.paddingSmall),
                Container(
                  decoration: BoxDecoration(
                    gradient: AppGradients.cardGradient,
                    borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                    border: Border.all(
                      color: AppColors.primary.withValues(alpha: 0.3),
                      width: 1,
                    ),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(AppSizes.paddingMedium),
                    leading: const Icon(
                      Icons.audio_file,
                      color: AppColors.textSecondary,
                      size: 20,
                    ),
                    title: Text(
                      _selectedAudioFile?.name ?? 'Select audio file',
                      style: AppTextStyles.body1.copyWith(
                        color: _selectedAudioFile != null 
                            ? AppColors.textPrimary 
                            : AppColors.textSecondary,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                    subtitle: _selectedAudioFile != null
                        ? Text(
                            '${(_selectedAudioFile!.size / 1024 / 1024).toStringAsFixed(2)} MB',
                            style: AppTextStyles.body2,
                          )
                        : null,
                    trailing: const Icon(
                      Icons.upload_file,
                      color: AppColors.textSecondary,
                    ),
                    onTap: _pickAudioFile,
                  ),
                ),
              ],
            ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.2),
            
            const SizedBox(height: AppSizes.paddingMedium),
            
            // Cover Image Picker (Optional)
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Cover Image (Optional)',
                  style: AppTextStyles.body1.copyWith(
                    fontWeight: FontWeight.w500,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: AppSizes.paddingSmall),
                Container(
                  decoration: BoxDecoration(
                    gradient: AppGradients.cardGradient,
                    borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                    border: Border.all(
                      color: AppColors.primary.withValues(alpha: 0.3),
                      width: 1,
                    ),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(AppSizes.paddingMedium),
                    leading: const Icon(
                      Icons.image,
                      color: AppColors.textSecondary,
                      size: 20,
                    ),
                    title: Text(
                      _selectedCoverFile?.name ?? 'Select cover image',
                      style: AppTextStyles.body1.copyWith(
                        color: _selectedCoverFile != null 
                            ? AppColors.textPrimary 
                            : AppColors.textSecondary,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: const Icon(
                      Icons.upload_file,
                      color: AppColors.textSecondary,
                    ),
                    onTap: _pickCoverFile,
                  ),
                ),
              ],
            ).animate().fadeIn(delay: 500.ms).slideY(begin: 0.2),
            
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
              text: 'Upload Song',
              onPressed: _handleUpload,
              isLoading: _isLoading,
              width: double.infinity,
              height: 45,
              icon: Icons.upload,
            ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.2),
          ],
        ),
      ),
    );
  }
}
