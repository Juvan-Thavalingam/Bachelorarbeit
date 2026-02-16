/// Hauptstartpunkt der Flutter-App.
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';


void main() {
  runApp(const MyApp());
}

/// Root-Widget der App, entscheidet je nach Login-Zustand über den Startbildschirm.
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  /// Entscheidet basierend auf Login-Status und Timeout, ob Login- oder HomeScreen angezeigt wird.
  Future<Widget> _determineStartScreen() async {
    final prefs = await SharedPreferences.getInstance();
    final isLoggedIn = prefs.getBool("isLoggedIn") ?? false;

    // Optional: Timeout prüfen
    final lastActive = prefs.getInt("lastActive") ?? 0;
    final now = DateTime.now().millisecondsSinceEpoch;
    final timeout = 10 * 60 * 1000; // 10 Minuten

    if (isLoggedIn && (now - lastActive) < timeout) {
      return const HomeScreen();
    } else {
      return const LoginScreen();
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Digital Twin Viewer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: FutureBuilder<Widget>(
        future: _determineStartScreen(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return snapshot.data!;
          } else {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }
        },
      ),
    );
  }
}
