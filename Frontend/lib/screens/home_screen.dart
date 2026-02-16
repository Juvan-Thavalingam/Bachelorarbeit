import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../widgets/record_checkbox_list.dart';
import '../widgets/filter_checkbox.dart';
import '../widgets/result_display.dart';
import '../services/api_service.dart';
import 'login_screen.dart';
import '../services/plugin_registry.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _controller = TextEditingController();
  final Map<String, bool> recordSelections = {
    'A-Record': false,
    'AAAA-Record': false,
    'MX-Record': false,
    'NS-Record': false,
    'TXT-Record': false,
    'SOA-Record': false,
    'PTR-Record': false,
    'Subdomain': false,
    'Zertifikat': false,
    'Endpunkt': false,
    'E-Mail': false,
    'Telefonnummer': false,
    'Dienst': false
  };
  Map<String, bool> filterSelections = {};

  final plugins = pluginRegistry;
  bool allSelected = false;
  Map<String, List<dynamic>> responseMap = {};
  Map<String, dynamic> scanStatusMap = {};
  bool isLoading = false;

  void toggleAll(bool? value) {
    setState(() {
      allSelected = value ?? false;
      recordSelections.updateAll((key, _) => allSelected);
    });
  }

  Future<void> withLoading(Future<void> Function() action) async {
    setState(() => isLoading = true);
    try {
      await action();
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  Future<void> _scan() async {
    await withLoading(() async {
      final domain = _controller.text.trim();
      if (domain.isEmpty) return;
      filterSelections = Map.fromEntries(recordSelections.entries.where((entry) => entry.value));
      final Map<String, dynamic> statusMap = {};
      for (final entry in filterSelections.entries) {
        final plugin = plugins[entry.key];
        if (plugin != null) {
          final status = await plugin.scan(domain);
          if (status.startsWith("❌") || status.contains("Fehler") || status.contains("error")) {
            statusMap[entry.key] = {"error": status};
          } else {
            statusMap[entry.key] = {"info": status};
          }
        }
      }
      setState(() => scanStatusMap = statusMap);
    });
  }

  Future<void> _getAndDisplay() async {
  await withLoading(() async {
    final domain = _controller.text.trim();
    if (domain.isEmpty) return;

    final activeSelections = recordSelections.entries
        .where((entry) => entry.value)
        .map((entry) => entry.key)
        .toList();

    Map<String, List<dynamic>> results = {};
    for (final key in activeSelections) {
      final plugin = plugins[key];
      if (plugin != null) {
        final records = await plugin.getValues(domain);
        results[key] = records;
      }
    }

    setState(() {
      responseMap = results;
    });
  });
}



  Future<void> _export() async {
    final domain = _controller.text.trim();
    if (domain.isEmpty) return;

    final activeSelections = recordSelections.entries
        .where((entry) => entry.value)
        .map((entry) => entry.key)
        .toList();

    if (activeSelections.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("⚠️ Keine Attribute ausgewählt")),
      );
      return;
    }

    Map<String, dynamic> results = {};
    for (final key in activeSelections) {
      final plugin = plugins[key];
      if (plugin != null) {
        final records = await plugin.getValues(domain);
        results[key] = records;
      }
    }

    if (results.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("❌ Keine Daten zum Exportieren gefunden")),
      );
      return;
    }

    await ApiService.exportJson(domain, results,pretty: true);
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Digitaler Twin'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
            tooltip: "Abmelden",
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: _controller,
              decoration: const InputDecoration(
                labelText: 'Domain (z.B. example.com)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            CheckboxListTile(
              title: const Text("Alle auswählen"),
              value: allSelected,
              onChanged: toggleAll,
            ),
            const SizedBox(height: 10),
            RecordCheckboxList(
              recordSelections: recordSelections,
              onChanged: (key, value) {
                setState(() {
                  recordSelections[key] = value;
                  allSelected = recordSelections.values.every((v) => v);
                });
              },
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                ElevatedButton(
                  onPressed: isLoading ? null : _scan,
                  child: const Text("Scan starten"),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton(
                    onPressed: isLoading ? null : _getAndDisplay,
                    child: const Text("Anzeigen"),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: isLoading ? null : _export,
                  child: const Text("Exportieren"),
                ),
              ],
            ),

            const SizedBox(height: 20),
            Filter_Checkbox(
              filterSelections: filterSelections,
              onChanged: (String key, bool value) {
                setState(() {
                  filterSelections[key] = value;
                  // Sofortige Aktualisierung der Ergebnisse nach jeder Änderung
                  _getAndDisplay();  // Stellen Sie sicher, dass diese Methode die filterSelections nutzt, um die Daten zu holen
                });
              },
            ),


            if (scanStatusMap.isNotEmpty)
              ...scanStatusMap.entries.map((entry) {
                final status = entry.value;
                final isError = status.containsKey("error");
                return Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    "🔍 ${entry.key}: ${status[isError ? "error" : "info"]}",
                    style: TextStyle(
                      color: isError ? Colors.red : Colors.green,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                );
              }),
            const SizedBox(height: 20),
            if (isLoading)
              const Center(child: CircularProgressIndicator()),
            const SizedBox(height: 20),
            const Text(
              "Ergebnisse:",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 10),
            if (responseMap.isNotEmpty)
              ...responseMap.entries.map((entry) => Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "📄 ${entry.key}:",
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 5),
                  ResultDisplay(text: jsonEncode(entry.value)),
                  const SizedBox(height: 20),
                ],
              )),
          ],
        ),
      ),
    );
  }
}
