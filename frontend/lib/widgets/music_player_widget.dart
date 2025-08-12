import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/song_service.dart';
import '../constants/app_constants.dart';
import 'custom_button.dart';

class MusicPlayerWidget extends StatefulWidget {
  final Map<String, dynamic>? currentSong;
  final List<Map<String, dynamic>> playlist;
  final int currentIndex;
  final Function(Map<String, dynamic>)? onSongChanged;
  final VoidCallback? onPlayPause;
  final VoidCallback? onNext;
  final VoidCallback? onPrevious;
  final bool isPlaying;
  final Duration position;
  final Duration duration;

  const MusicPlayerWidget({
    super.key,
    this.currentSong,
    this.playlist = const [],
    this.currentIndex = 0,
    this.onSongChanged,
    this.onPlayPause,
    this.onNext,
    this.onPrevious,
    this.isPlaying = false,
    this.position = Duration.zero,
    this.duration = Duration.zero,
  });

  @override
  State<MusicPlayerWidget> createState() => _MusicPlayerWidgetState();
}

class _MusicPlayerWidgetState extends State<MusicPlayerWidget> {
  final SongService _songService = SongService();
  double _sliderValue = 0.0;
  bool _isDragging = false;

  @override
  void initState() {
    super.initState();
    _updateSliderValue();
  }

  @override
  void didUpdateWidget(MusicPlayerWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!_isDragging) {
      _updateSliderValue();
    }
  }

  void _updateSliderValue() {
    if (widget.duration.inMilliseconds > 0) {
      setState(() {
        _sliderValue = widget.position.inMilliseconds / widget.duration.inMilliseconds;
      });
    }
  }

  void _onSliderChanged(double value) {
    setState(() {
      _sliderValue = value;
      _isDragging = true;
    });
  }

  void _onSliderChangedEnd(double value) {
    setState(() {
      _isDragging = false;
    });
    // Here you would seek to the new position
    // widget.onSeek?.call(Duration(milliseconds: (value * widget.duration.inMilliseconds).round()));
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    if (widget.currentSong == null) {
      return Container(
        height: 100,
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
          border: Border.all(
            color: AppColors.primary.withValues(alpha: 0.2),
          ),
        ),
        child: const Center(
          child: Text(
            'No song playing',
            style: AppTextStyles.body2,
          ),
        ),
      );
    }

    final song = widget.currentSong!;
    final title = song['title'] ?? '';
    final artistName = song['artist_name'];
    final bandName = song['band_name'];
    final coverImage = song['cover_image'];

    return Container(
      height: 120,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        children: [
          // Progress Bar
          Container(
            height: 4,
            decoration: BoxDecoration(
              color: AppColors.textSecondary.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(2),
            ),
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: _sliderValue,
              child: Container(
                decoration: BoxDecoration(
                  gradient: AppGradients.primaryGradient,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
          ),
          
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(AppSizes.paddingMedium),
              child: Row(
                children: [
                  // Cover Image
                  Container(
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
                  
                  const SizedBox(width: AppSizes.paddingMedium),
                  
                  // Song Info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          title,
                          style: AppTextStyles.body1.copyWith(
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          artistName ?? bandName ?? 'Unknown Artist',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${_formatDuration(widget.position)} / ${_formatDuration(widget.duration)}',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(width: AppSizes.paddingMedium),
                  
                  // Controls
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Previous Button
                      IconButton(
                        onPressed: widget.onPrevious,
                        icon: const Icon(
                          Icons.skip_previous,
                          color: AppColors.textSecondary,
                          size: 28,
                        ),
                      ),
                      
                      // Play/Pause Button
                      Container(
                        decoration: BoxDecoration(
                          gradient: AppGradients.primaryGradient,
                          shape: BoxShape.circle,
                        ),
                        child: IconButton(
                          onPressed: widget.onPlayPause,
                          icon: Icon(
                            widget.isPlaying ? Icons.pause : Icons.play_arrow,
                            color: AppColors.textPrimary,
                            size: 32,
                          ),
                        ),
                      ),
                      
                      // Next Button
                      IconButton(
                        onPressed: widget.onNext,
                        icon: const Icon(
                          Icons.skip_next,
                          color: AppColors.textSecondary,
                          size: 28,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.2);
  }
}
