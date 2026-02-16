import 'package:file_saver/file_saver.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'plugin_registry.dart';

class ApiService {
  static Future<void> exportJson(String domain, Map<String, dynamic> data, {bool pretty = false}) async {
    final Map<String, dynamic> enriched = {};

    for (final entry in data.entries) {
      final key = entry.key;
      final values = entry.value;

      final plugin = pluginRegistry[key];
      if (plugin != null) {
        final describe = await plugin.describe();
        final descriptionText = describe["Beschreibung"] ?? "Keine Beschreibung verfügbar.";

        enriched[key] = [
          {"Beschreibung": descriptionText},
          ...values,
        ];
      } else {
        enriched[key] = values; // fallback, falls Plugin nicht gefunden
      }
    }

    final encoder = pretty ? const JsonEncoder.withIndent('  ') : const JsonEncoder();
    final String jsonString = encoder.convert({domain: enriched});

    final Uint8List bytes = Uint8List.fromList(utf8.encode(jsonString));

    await FileSaver.instance.saveFile(
      name: 'digitaler_twin_$domain',
      bytes: bytes,
      ext: 'json',
      mimeType: MimeType.json,
    );
  }
}
