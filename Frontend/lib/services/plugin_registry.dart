/// Plugin-Registry, die alle verfügbaren Plugin-Services auflistet.
import 'base_plugin_service.dart';

/// Verfügbare Plugins, z.B. DNS-Record-Typen, Subdomains, Zertifikate, etc.
final Map<String, BasePluginService> pluginRegistry = {
  "A-Record": BasePluginService("A"),
  "AAAA-Record": BasePluginService("AAAA"),
  "MX-Record": BasePluginService("MX"),
  "NS-Record": BasePluginService("NS"),
  "TXT-Record": BasePluginService("TXT"),
  "SOA-Record": BasePluginService("SOA"),
  "PTR-Record": BasePluginService("PTR"),
  "Subdomain": BasePluginService("subdomain"),
  "Zertifikat": BasePluginService("certificate"),
  "Endpunkt": BasePluginService("endpoint"),
  "E-Mail": BasePluginService("email"),
  "Telefonnummer": BasePluginService("phone"),
  "Dienst": BasePluginService("service"),
};
