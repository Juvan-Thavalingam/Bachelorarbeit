import 'package:flutter/material.dart';
import 'home_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userController = TextEditingController();
  final _passController = TextEditingController();
  bool _loadingPassword = true;
  String? _error;

  final String _validUser = "admin";
  String? _validPassword;

  /// Holt Passwort vom Backend
  Future<void> _fetchPassword() async {
    try {
      final res = await http.get(Uri.parse("http://localhost:8000/api/admin-password"));
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _validPassword = data["password"];
          _loadingPassword = false;
        });
      } else {
        setState(() {
          _error = "⚠️ Passwort konnte nicht geladen werden";
          _loadingPassword = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = "❌ Netzwerkfehler: $e";
        _loadingPassword = false;
      });
    }
  }


  /// Führt den Login-Prozess durch
  Future<void> _login() async {
    final user = _userController.text.trim();
    final pass = _passController.text;

    if (user == _validUser && pass == _validPassword) {
      await _saveLogin();
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    } else {
      setState(() {
        _error = "❌ Falscher Benutzername oder Passwort";
      });
    }
  }

  /// Speichert den Loginstatus
  Future<void> _saveLogin() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool("isLoggedIn", true);
    await prefs.setInt("lastActive", DateTime.now().millisecondsSinceEpoch);
  }

  @override
  void initState() {
    super.initState();
    _fetchPassword();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Digitaler Twin Login")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(
              controller: _userController,
              decoration: const InputDecoration(labelText: "Benutzername"),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _passController,
              decoration: const InputDecoration(labelText: "Passwort"),
              obscureText: true,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _validPassword == null ? null : _login,
              child: const Text("Anmelden"),
            ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),
          ],
        ),
      ),
    );
  }
}
