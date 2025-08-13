import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:lottie/lottie.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/app_constants.dart';
import 'homepage.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<OnboardingItem> _onboardingItems = [
    OnboardingItem(
      title: 'Your Music, Your Way',
      description: 'Create personalized playlists, discover new artists, and enjoy your favorite tracks with our intelligent recommendation system.',
      animationPath: 'assets/animations/animation1.json',
      icon: Icons.favorite,
    ),
    OnboardingItem(
      title: 'Music is Better Together',
      description: 'Share playlists with friends, collaborate on music collections, and connect with fellow music lovers around the world.',
      animationPath: 'assets/animations/animation2.json',
      icon: Icons.people,
    ),
    OnboardingItem(
      title: 'For Listeners and Musicians',
      description: 'Whether you\'re discovering music or creating it, our platform supports both listeners and artists with powerful tools.',
      animationPath: 'assets/animations/animation3.json',
      icon: Icons.music_note,
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onPageChanged(int page) {
    setState(() {
      _currentPage = page;
    });
  }

  void _nextPage() {
    if (_currentPage < _onboardingItems.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      _completeOnboarding();
    }
  }

  void _skipOnboarding() {
    _completeOnboarding();
  }

  Future<void> _completeOnboarding() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('hasSeenOnboarding', true);
    
    if (mounted) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const HomePage()),
        (route) => false,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isWeb = screenSize.width > 600;
    
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: AppGradients.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Skip Button
              Align(
                alignment: Alignment.topRight,
                child: Padding(
                  padding: EdgeInsets.all(isWeb ? AppSizes.paddingLarge : AppSizes.paddingMedium),
                  child: TextButton(
                    onPressed: _skipOnboarding,
                    child: Text(
                      'Skip',
                      style: AppTextStyles.body2.copyWith(
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w500,
                        fontSize: isWeb ? 16 : 14,
                      ),
                    ),
                  ),
                ),
              ).animate().fadeIn(delay: 200.ms).slideX(begin: 0.3),
              
              // Page Content
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  onPageChanged: _onPageChanged,
                  itemCount: _onboardingItems.length,
                  itemBuilder: (context, index) {
                    return OnboardingItemWidget(
                      item: _onboardingItems[index],
                      index: index,
                    );
                  },
                ),
              ),
              
              // Page Indicators and Navigation
              Padding(
                padding: EdgeInsets.all(isWeb ? AppSizes.paddingXLarge : AppSizes.paddingLarge),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Page Indicators
                    Row(
                      children: List.generate(
                        _onboardingItems.length,
                        (index) => Container(
                          margin: EdgeInsets.only(right: isWeb ? 12 : 8),
                          width: _currentPage == index ? (isWeb ? 32 : 24) : (isWeb ? 12 : 8),
                          height: isWeb ? 10 : 8,
                          decoration: BoxDecoration(
                            color: _currentPage == index 
                                ? AppColors.primary 
                                : AppColors.textSecondary.withValues(alpha: 0.3),
                            borderRadius: BorderRadius.circular(isWeb ? 5 : 4),
                          ),
                        ).animate().scale(delay: 100.ms),
                      ),
                    ),
                    
                    // Next/Get Started Button
                    TextButton(
                      onPressed: _nextPage,
                      child: Text(
                        _currentPage == _onboardingItems.length - 1 ? 'Get Started' : 'Next',
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.primary,
                          fontWeight: FontWeight.w600,
                          fontSize: isWeb ? 18 : 16,
                        ),
                      ),
                    ).animate().fadeIn(delay: 300.ms).slideX(begin: -0.3),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class OnboardingItem {
  final String title;
  final String description;
  final String animationPath;
  final IconData icon;

  OnboardingItem({
    required this.title,
    required this.description,
    required this.animationPath,
    required this.icon,
  });
}

class OnboardingItemWidget extends StatelessWidget {
  final OnboardingItem item;
  final int index;

  const OnboardingItemWidget({
    super.key,
    required this.item,
    required this.index,
  });

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isWeb = screenSize.width > 600;
    final isTablet = screenSize.width > 400 && screenSize.width <= 600;
    
    // Responsive sizing
    final animationSize = isWeb ? 297.5 : (isTablet ? 255.0 : 170.0); // Reduced by 15%
    final iconSize = isWeb ? 80.0 : (isTablet ? 70.0 : 50.0);
    final titleFontSize = isWeb ? 22.4 : (isTablet ? 20.8 : 16.0); // Reduced by 20%
    final descriptionFontSize = isWeb ? 18.0 : (isTablet ? 17.0 : 14.0);
    final maxContentWidth = isWeb ? 600.0 : (isTablet ? 500.0 : double.infinity);
    
    return Padding(
      padding: EdgeInsets.fromLTRB(
        isWeb ? AppSizes.paddingLarge : AppSizes.paddingMedium,
        0, // No top padding
        isWeb ? AppSizes.paddingLarge : AppSizes.paddingMedium,
        isWeb ? AppSizes.paddingLarge : AppSizes.paddingMedium,
      ),
      child: Center(
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: maxContentWidth),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              // Animation Section (50% of space)
              Expanded(
                flex: 5,
                child: Center(
                  child: SizedBox(
                    width: animationSize,
                    height: animationSize,
                    child: Lottie.asset(
                      item.animationPath,
                      fit: BoxFit.contain,
                      repeat: true,
                    ),
                  ),
                ),
              ).animate().fadeIn(delay: (index * 200).ms).slideY(begin: 0.3),
              
              // Content Section (50% of space)
              Expanded(
                flex: 5,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Icon
                    Container(
                      width: iconSize,
                      height: iconSize,
                      decoration: BoxDecoration(
                        gradient: AppGradients.primaryGradient,
                        borderRadius: BorderRadius.circular(AppSizes.radiusLarge),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.primary.withValues(alpha: 0.3),
                            blurRadius: 10,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Icon(
                        item.icon,
                        size: iconSize * 0.5,
                        color: AppColors.textPrimary,
                      ),
                    ).animate().scale(delay: (index * 200 + 300).ms).then().shake(),
                    
                    SizedBox(height: isWeb ? AppSizes.paddingMedium : AppSizes.paddingSmall),
                    
                    // Title
                    Text(
                      item.title,
                      style: AppTextStyles.heading2.copyWith(
                        fontSize: titleFontSize,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                      textAlign: TextAlign.center,
                    ).animate().fadeIn(delay: (index * 200 + 400).ms).slideY(begin: 0.3),
                    
                    SizedBox(height: isWeb ? AppSizes.paddingSmall : 4),
                    
                    // Description
                    Padding(
                      padding: EdgeInsets.symmetric(
                        horizontal: isWeb ? AppSizes.paddingLarge : AppSizes.paddingSmall,
                      ),
                      child: Text(
                        item.description,
                        style: AppTextStyles.body2.copyWith(
                          fontSize: descriptionFontSize,
                          color: AppColors.textSecondary,
                          height: 1.4,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ).animate().fadeIn(delay: (index * 200 + 500).ms).slideY(begin: 0.3),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
