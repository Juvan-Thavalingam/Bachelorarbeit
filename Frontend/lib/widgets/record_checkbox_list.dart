/// Checkbox-Liste für DNS- und Plugin-Typen.
import 'package:flutter/material.dart';
import '../services/plugin_registry.dart';

class RecordCheckboxList extends StatefulWidget {
  final Map<String, bool> recordSelections;
  final void Function(String, bool) onChanged;

  const RecordCheckboxList({
    super.key,
    required this.recordSelections,
    required this.onChanged,
  });

  @override
  State<RecordCheckboxList> createState() => _RecordCheckboxListState();
}

class _RecordCheckboxListState extends State<RecordCheckboxList> {
  Future<void> _showPluginInfo(String key) async {
    final plugin = pluginRegistry[key];
    if (plugin != null) {
      final info = await plugin.describe();
      final title = info["name"] ?? key;
      final desc = info["Beschreibung"] ?? "Keine Beschreibung verfügbar.";
      final columns = (info["columns"] as List?)?.join("\n• ") ?? "";

      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text(title),
          content: Text("$desc\n\n📄 Spalten:\n• $columns"),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text("Schliessen"),
            )
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: widget.recordSelections.entries.map((entry) {
        return CheckboxListTile(
          value: entry.value,
          onChanged: (val) => widget.onChanged(entry.key, val ?? false),
          title: Row(
            children: [
              Expanded(child: Text(entry.key)),
              IconButton(
                icon: const Icon(Icons.info_outline, size: 18),
                tooltip: "Info anzeigen",
                onPressed: () => _showPluginInfo(entry.key),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
