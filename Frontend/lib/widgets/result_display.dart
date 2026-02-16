import 'package:flutter/material.dart';
import 'json_table.dart';
import 'dart:convert';

/// Widget zur Darstellung von Scan-Ergebnissen.
/// Erkennt automatisch JSON-Daten (List/Map) und zeigt sie ggf. tabellarisch an.
class ResultDisplay extends StatelessWidget {
  final String text;

  const ResultDisplay({
    super.key,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;
    final dynamicMaxHeight = screenHeight * 0.8; // z.B. 80 % der Bildschirmhöhe

    dynamic parsed;

    try {
      parsed = jsonDecode(text);
    } catch (_) {
      return _asText(text, context);
    }

    // Sonderfälle: "info" oder "error"
    if (parsed is List && parsed.length == 1 && parsed.first is Map<String, dynamic>) {
      final map = parsed.first as Map<String, dynamic>;
      if (map.containsKey("info")) {
        return _asText(map["info"].toString(), context);
      } else if (map.containsKey("error")) {
        return _asText(map["error"].toString(), context, isError: true);
      }
    }

    // Normale Tabelle
    if (parsed is List && parsed.isNotEmpty && parsed.first is Map<String, dynamic>) {
      return JsonTable(
        data: List<Map<String, dynamic>>.from(parsed),
        maxHeight: dynamicMaxHeight,
      );
    }

    return _asText(text, context);
  }

  Widget _asText(String value, BuildContext context, {bool isError = false}) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Text(
        value,
        style: TextStyle(
          fontFamily: 'monospace',
          color: isError ? Colors.red : Colors.black,
        ),
      ),
    );
  }
}
