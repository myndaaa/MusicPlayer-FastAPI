import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../constants/app_constants.dart';
import '../widgets/custom_button.dart';
import '../services/auth_service.dart';
import '../widgets/song_search_widget.dart';
import '../widgets/music_player_widget.dart';
import '../widgets/genre_create_widget.dart';
import '../widgets/song_upload_widget.dart';
import '../widgets/song_list_widget.dart';
import 'homepage.dart';

class Dashboard extends StatefulWidget {
  const Dashboard({super.key});

  @override
  State<Dashboard> createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> with TickerProviderStateMixin {
  final AuthService _authService = AuthService();
  Map<String, dynamic>? _userData;
  bool _isLoading = true;
  int _currentTabIndex = 0;
  Map<String, dynamic>? _currentSong;
  List<Map<String, dynamic>> _playlist = [];
  int _currentSongIndex = 0;
  bool _isPlaying = false;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _loadUserData();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_userData != null) {
      final tabCount = _buildTabs().length;
      if (_tabController.length != tabCount) {
        _tabController.dispose();
        _tabController = TabController(
          length: tabCount,
          vsync: this,
        );
      }
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadUserData() async {
    final userData = await _authService.getUserData();
    setState(() {
      _userData = userData;
      _isLoading = false;
    });
  }

  Future<void> _handleLogout() async {
    await _authService.logout();
    if (mounted) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const HomePage()),
        (route) => false,
      );
    }
  }

  void _onSongSelected(Map<String, dynamic> song) {
    setState(() {
      _currentSong = song;
      if (!_playlist.contains(song)) {
        _playlist.add(song);
      }
      _currentSongIndex = _playlist.indexOf(song);
      _isPlaying = true;
    });
  }

  void _onPlayPause(bool isPlaying) {
    setState(() {
      _isPlaying = isPlaying;
    });
  }

  void _onSongChanged(int index) {
    setState(() {
      _currentSongIndex = index;
      _currentSong = _playlist[index];
    });
  }

  List<Widget> _buildTabs() {
    final tabs = <Widget>[];
    
    // All users can search and play music
    tabs.add(const Tab(text: 'Search & Play'));
    tabs.add(const Tab(text: 'All Songs'));
    
    // Admin specific tabs
    if (_userData?['role'] == 'admin') {
      tabs.add(const Tab(text: 'Manage Genres'));
    }
    
    // Artist/Musician specific tabs
    if (_userData?['role'] == 'musician') {
      tabs.add(const Tab(text: 'Upload Song'));
    }
    
    return tabs;
  }

  List<Widget> _buildTabViews() {
    final views = <Widget>[];
    
    // Search & Play tab
    views.add(SongSearchWidget(
      onSongSelected: _onSongSelected,
      showFilters: true,
    ));
    
    // All Songs tab
    views.add(SongListWidget(
      onSongSelected: _onSongSelected,
    ));
    
    // Admin specific views
    if (_userData?['role'] == 'admin') {
      views.add(const GenreCreateWidget());
    }
    
    // Artist/Musician specific views
    if (_userData?['role'] == 'musician') {
      views.add(const SongUploadWidget());
    }
    
    return views;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        body: Container(
          decoration: const BoxDecoration(
            gradient: AppGradients.backgroundGradient,
          ),
          child: const Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            ),
          ),
        ),
      );
    }

    if (_userData == null) {
      return Scaffold(
        body: Container(
          decoration: const BoxDecoration(
            gradient: AppGradients.backgroundGradient,
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(AppSizes.paddingLarge),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Dashboard',
                        style: AppTextStyles.heading1,
                      ),
                      CustomButton(
                        text: 'Logout',
                        onPressed: _handleLogout,
                        isOutlined: true,
                        icon: Icons.logout,
                      ),
                    ],
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.all(AppSizes.paddingLarge),
                    decoration: BoxDecoration(
                      gradient: AppGradients.cardGradient,
                      borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
                      border: Border.all(
                        color: AppColors.error.withValues(alpha: 0.3),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          Icons.error_outline,
                          size: 60,
                          color: AppColors.error,
                        ),
                        const SizedBox(height: AppSizes.paddingMedium),
                        Text(
                          'Failed to load user data',
                          style: AppTextStyles.heading2.copyWith(
                            color: AppColors.error,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Spacer(),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppGradients.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.all(AppSizes.paddingLarge),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Welcome, ${_userData!['username'] ?? 'User'}!',
                          style: AppTextStyles.heading2,
                        ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.3),
                        Text(
                          'Role: ${_userData!['role']?.toString().toUpperCase() ?? 'USER'}',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ).animate().fadeIn(delay: 400.ms).slideX(begin: -0.3),
                      ],
                    ),
                    CustomButton(
                      text: 'Logout',
                      onPressed: _handleLogout,
                      isOutlined: true,
                      icon: Icons.logout,
                    ).animate().fadeIn(delay: 600.ms).slideX(begin: 0.3),
                  ],
                ),
              ),
              
              // Tab Bar
              Container(
                margin: const EdgeInsets.symmetric(horizontal: AppSizes.paddingLarge),
                decoration: BoxDecoration(
                  gradient: AppGradients.cardGradient,
                  borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                  border: Border.all(
                    color: AppColors.primary.withValues(alpha: 0.3),
                  ),
                ),
                child: TabBar(
                  controller: _tabController,
                  indicator: BoxDecoration(
                    gradient: AppGradients.primaryGradient,
                    borderRadius: BorderRadius.circular(AppSizes.radiusMedium),
                  ),
                  labelColor: AppColors.textPrimary,
                  unselectedLabelColor: AppColors.textSecondary,
                  tabs: _buildTabs(),
                ),
              ).animate().fadeIn(delay: 800.ms).slideY(begin: -0.2),
              
              const SizedBox(height: AppSizes.paddingMedium),
              
              // Tab Views
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: _buildTabViews(),
                ),
              ).animate().fadeIn(delay: 1000.ms).slideY(begin: 0.2),
              
              // Music Player
              if (_currentSong != null)
                MusicPlayerWidget(
                  currentSong: _currentSong,
                  playlist: _playlist,
                  currentIndex: _currentSongIndex,
                  onSongChanged: _onSongChanged,
                  onPlayPause: _onPlayPause,
                  isPlaying: _isPlaying,
                  isMinimized: true,
                ).animate().slideY(begin: 1.0, end: 0.0).fadeIn(),
            ],
          ),
        ),
      ),
    );
  }
}
