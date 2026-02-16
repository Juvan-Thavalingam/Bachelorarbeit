/// Abstrakte Service-Klasse für Plugins, um Scan- und Get-Anfragen an das Backend zu senden.
import 'package:http/http.dart' as http;
import 'dart:convert';

class BasePluginService {
  /// Der Attributname (zB. "A", "MX", "subdomain").
  final String attribute;

  BasePluginService(this.attribute);

  /// Sendet einen Scan-Request für die gegebene Domain.
  Future<String> scan(String domain) async {
    final url = Uri.parse("http://localhost:8000/scan?attribute=$attribute&domain=$domain");

    try {
      final res = await http.get(url);
      final decoded = utf8.decode(res.bodyBytes);
      final json = jsonDecode(decoded);
      return json['error'] ?? json['status'] ?? '⚠️ Keine Antwort';
    } catch (e) {
      return "❌ Fehler bei Scan ($attribute): $e";
    }
  }

  /// Holt die gespeicherten Werte für die gegebene Domain.
  Future<List<dynamic>> getValues(String domain) async {
    final url = Uri.parse("http://localhost:8000/get?attribute=$attribute&domain=$domain");

    try {
      final res = await http.get(url);
      final decoded = utf8.decode(res.bodyBytes);
      final json = jsonDecode(decoded);
      return json is List ? json : [json];
    } catch (e) {
      return [{"error": "❌ Fehler beim Abrufen ($attribute): $e"}];
    }
  }

  Future<Map<String, dynamic>> describe() async {
  final url = Uri.parse("http://localhost:8000/describe?attribute=$attribute");

  try {
    final res = await http.get(url);
    if (res.statusCode == 200) {
      final decoded = utf8.decode(res.bodyBytes);
      final json = jsonDecode(decoded);
      return json is Map<String, dynamic> ? json : {};
    } else {
      return {"error": "Serverfehler ${res.statusCode}"};
    }
  } catch (e) {
    return {"error": "❌ Fehler beim Laden der Beschreibung: $e"};
  }
}


}
