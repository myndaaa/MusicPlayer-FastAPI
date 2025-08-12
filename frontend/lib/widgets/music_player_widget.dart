import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'dart:async';
import '../constants/app_constants.dart';
import '../services/song_service.dart';
import 'custom_button.dart';

class MusicPlayerWidget extends StatefulWidget {
  final Map<String, dynamic>? currentSong;
  final List<Map<String, dynamic>> playlist;
  final int currentIndex;
  final Function(int)? onSongChanged;
  final Function(bool)? onPlayPause;
  final bool isPlaying;
  final bool isMinimized;

  const MusicPlayerWidget({
    super.key,
    this.currentSong,
    required this.playlist,
    required this.currentIndex,
    this.onSongChanged,
    this.onPlayPause,
    this.isPlaying = false,
    this.isMinimized = false,
  });

  @override
  State<MusicPlayerWidget> createState() => _MusicPlayerWidgetState();
}

class _MusicPlayerWidgetState extends State<MusicPlayerWidget>
    with TickerProviderStateMixin {
  late AnimationController _rotationController;
  late AnimationController _pulseController;
  Timer? _progressTimer;
  double _currentProgress = 0.0;
  double _totalDuration = 0.0;
  bool _isDragging = false;
  bool _isFileMissing = false;
  final SongService _songService = SongService();

  @override
  void initState() {
    super.initState();
    _rotationController = AnimationController(
      duration: const Duration(seconds: 10),
      vsync: this,
    );
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    if (widget.isPlaying) {
      _startProgressTimer();
      _rotationController.repeat();
    }
  }

  @override
  void didUpdateWidget(MusicPlayerWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.isPlaying != oldWidget.isPlaying) {
      if (widget.isPlaying) {
        _startProgressTimer();
        _rotationController.repeat();
      } else {
        _stopProgressTimer();
        _rotationController.stop();
      }
    }
    
    if (widget.currentSong != oldWidget.currentSong) {
      _resetProgress();
      _checkFileExists();
    }
  }

  @override
  void dispose() {
    _rotationController.dispose();
    _pulseController.dispose();
    _stopProgressTimer();
    super.dispose();
  }

  void _startProgressTimer() {
    _progressTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
      if (!_isDragging && widget.isPlaying) {
        setState(() {
          _currentProgress += 0.1;
          if (_currentProgress >= _totalDuration) {
            _currentProgress = _totalDuration;
            _nextSong();
          }
        });
      }
    });
  }

  void _stopProgressTimer() {
    _progressTimer?.cancel();
    _progressTimer = null;
  }

  void _resetProgress() {
    setState(() {
      _currentProgress = 0.0;
      _totalDuration = widget.currentSong?['song_duration']?.toDouble() ?? 0.0;
    });
  }

  Future<void> _checkFileExists() async {
    if (widget.currentSong != null) {
      final songId = widget.currentSong!['id'];
      final exists = await _songService.checkSongFileExists(songId);
      setState(() {
        _isFileMissing = !exists;
      });
    }
  }

  void _nextSong() {
    if (widget.onSongChanged != null && widget.currentIndex < widget.playlist.length - 1) {
      widget.onSongChanged!(widget.currentIndex + 1);
    }
  }

  void _previousSong() {
    if (widget.onSongChanged != null && widget.currentIndex > 0) {
      widget.onSongChanged!(widget.currentIndex - 1);
    }
  }

  void _togglePlayPause() {
    if (_isFileMissing) {
      _showFileMissingAlert();
      return;
    }
    
    if (widget.onPlayPause != null) {
      widget.onPlayPause!(!widget.isPlaying);
    }
  }

  void _showFileMissingAlert() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: AppColors.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
          ),
          title: Row(
            children: [
              Icon(
                Icons.error_outline,
                color: AppColors.error,
                size: 24,
              ),
              const SizedBox(width: AppSizes.paddingSmall),
              Text(
                'Song Unavailable',
                style: AppTextStyles.heading2.copyWith(
                  color: AppColors.error,
                  fontSize: 18,
                ),
              ),
            ],
          ),
          content: Text(
            'This song\'s audio file is missing or unavailable.',
            style: AppTextStyles.body1.copyWith(
              color: AppColors.textPrimary,
            ),
          ),
          actions: [
            CustomButton(
              text: 'OK',
              onPressed: () => Navigator.of(context).pop(),
              height: 40,
            ),
          ],
        );
      },
    );
  }

  void _onProgressChanged(double value) {
    setState(() {
      _currentProgress = value;
    });
  }

  void _onProgressStart(double value) {
    setState(() {
      _isDragging = true;
    });
  }

  void _onProgressEnd(double value) {
    setState(() {
      _isDragging = false;
      _currentProgress = value;
    });
  }

  String _formatDuration(double seconds) {
    final minutes = (seconds / 60).floor();
    final remainingSeconds = (seconds % 60).floor();
    return '${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    if (widget.currentSong == null) {
      return const SizedBox.shrink();
    }

    final song = widget.currentSong!;
    final title = song['title'] ?? '';
    final artistName = song['artist_name'];
    final bandName = song['band_name'];
    final coverImage = song['cover_image'];

    if (widget.isMinimized) {
      return _buildMinimizedPlayer(song, title, artistName, bandName, coverImage);
    }

    return _buildFullPlayer(song, title, artistName, bandName, coverImage);
  }

  Widget _buildMinimizedPlayer(
    Map<String, dynamic> song,
    String title,
    String? artistName,
    String? bandName,
    String? coverImage,
  ) {
    return Container(
      height: 80,
      decoration: BoxDecoration(
        gradient: AppGradients.cardGradient,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(AppSizes.radiusLarge),
          topRight: Radius.circular(AppSizes.radiusLarge),
        ),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.3),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMedium),
        child: Row(
          children: [
            // Cover Image
            Container(
              width: 50,
              height: 50,
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
                              size: 20,
                            ),
                          );
                        },
                      ),
                    )
                  : AnimatedBuilder(
                      animation: _rotationController,
                      builder: (context, child) {
                        return Transform.rotate(
                          angle: _rotationController.value * 2 * 3.14159,
                          child: const Icon(
                            Icons.music_note,
                            color: AppColors.textPrimary,
                            size: 20,
                          ),
                        );
                      },
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
                  if (artistName != null || bandName != null)
                    Text(
                      artistName ?? bandName ?? '',
                      style: AppTextStyles.body2.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 12,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            
            // Controls
            Row(
              children: [
                IconButton(
                  onPressed: _previousSong,
                  icon: const Icon(
                    Icons.skip_previous,
                    color: AppColors.primary,
                    size: 24,
                  ),
                ),
                AnimatedBuilder(
                  animation: _pulseController,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: widget.isPlaying ? 1.0 + (_pulseController.value * 0.1) : 1.0,
                      child: IconButton(
                        onPressed: _togglePlayPause,
                        icon: Icon(
                          widget.isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled,
                          color: AppColors.primary,
                          size: 40,
                        ),
                      ),
                    );
                  },
                ),
                IconButton(
                  onPressed: _nextSong,
                  icon: const Icon(
                    Icons.skip_next,
                    color: AppColors.primary,
                    size: 24,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    ).animate().slideY(begin: 1.0, end: 0.0).fadeIn();
  }

  Widget _buildFullPlayer(
    Map<String, dynamic> song,
    String title,
    String? artistName,
    String? bandName,
    String? coverImage,
  ) {
    return Container(
      height: 200,
      decoration: BoxDecoration(
        gradient: AppGradients.cardGradient,
        borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.3),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingLarge),
        child: Column(
          children: [
            // Song Info Row
            Row(
              children: [
                // Cover Image
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                    gradient: coverImage != null 
                        ? null 
                        : AppGradients.primaryGradient,
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withValues(alpha: 0.3),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: coverImage != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                          child: Image.network(
                            coverImage,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                decoration: BoxDecoration(
                                  gradient: AppGradients.primaryGradient,
                                  borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                                ),
                                child: const Icon(
                                  Icons.music_note,
                                  color: AppColors.textPrimary,
                                  size: 32,
                                ),
                              );
                            },
                          ),
                        )
                      : AnimatedBuilder(
                          animation: _rotationController,
                          builder: (context, child) {
                            return Transform.rotate(
                              angle: _rotationController.value * 2 * 3.14159,
                              child: const Icon(
                                Icons.music_note,
                                color: AppColors.textPrimary,
                                size: 32,
                              ),
                            );
                          },
                        ),
                ),
                
                const SizedBox(width: AppSizes.paddingLarge),
                
                // Song Details
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: AppTextStyles.heading2.copyWith(
                          color: AppColors.textPrimary,
                          fontSize: 18,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: AppSizes.paddingSmall),
                      if (artistName != null || bandName != null)
                        Text(
                          artistName ?? bandName ?? '',
                          style: AppTextStyles.body1.copyWith(
                            color: AppColors.textSecondary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      const SizedBox(height: AppSizes.paddingSmall),
                      Text(
                        '${_formatDuration(_currentProgress)} / ${_formatDuration(_totalDuration)}',
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: AppSizes.paddingLarge),
            
            // Progress Bar
            SliderTheme(
              data: SliderTheme.of(context).copyWith(
                activeTrackColor: AppColors.primary,
                inactiveTrackColor: AppColors.primary.withValues(alpha: 0.2),
                thumbColor: AppColors.primary,
                thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
                trackHeight: 4,
                overlayShape: const RoundSliderOverlayShape(overlayRadius: 16),
              ),
              child: Slider(
                value: _currentProgress.clamp(0.0, _totalDuration),
                max: _totalDuration,
                onChanged: _onProgressChanged,
                onChangeStart: _onProgressStart,
                onChangeEnd: _onProgressEnd,
              ),
            ),
            
            const SizedBox(height: AppSizes.paddingMedium),
            
            // Controls
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  onPressed: _previousSong,
                  icon: const Icon(
                    Icons.skip_previous,
                    color: AppColors.primary,
                    size: 32,
                  ),
                ),
                const SizedBox(width: AppSizes.paddingMedium),
                AnimatedBuilder(
                  animation: _pulseController,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: widget.isPlaying ? 1.0 + (_pulseController.value * 0.1) : 1.0,
                      child: IconButton(
                        onPressed: _togglePlayPause,
                        icon: Icon(
                          widget.isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled,
                          color: AppColors.primary,
                          size: 60,
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(width: AppSizes.paddingMedium),
                IconButton(
                  onPressed: _nextSong,
                  icon: const Icon(
                    Icons.skip_next,
                    color: AppColors.primary,
                    size: 32,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    ).animate().fadeIn().slideY(begin: 0.2);
  }
}
