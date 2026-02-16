from plugins.dns.dns_plugin import Plugin as DNSPlugin
from plugins.subdomain.subdomain_plugin import Plugin as SubdomainPlugin
from plugins.certificate.certificate_plugin import Plugin as CertificatePlugin
from plugins.endpoint.endpoint_plugin import Plugin as EndpointPlugin
from plugins.email.email_plugin import Plugin as EmailPlugin
from plugins.phone.phone_plugin import Plugin as PhonePlugin
from plugins.service.service_plugin import Plugin as ServicePlugin

plugin_registry = {
    "A": DNSPlugin("A"),
    "AAAA": DNSPlugin("AAAA"),
    "MX": DNSPlugin("MX"),
    "NS": DNSPlugin("NS"),
    "TXT": DNSPlugin("TXT"),
    "SOA": DNSPlugin("SOA"),
    "PTR": DNSPlugin("PTR"),
    "subdomain": SubdomainPlugin(),
    "certificate": CertificatePlugin(),
    "endpoint": EndpointPlugin(),
    "email": EmailPlugin(),
    "phone": PhonePlugin(),
    "service": ServicePlugin(),
}
"""
Zentrale Registrierung der Plugins (z.B. für "A", "PTR", "subdomain").

Wird von API-Routen verwendet, um das passende Plugin zu finden.
"""

def get_plugin(attribute: str):
    """
    Gibt das Plugin für ein bestimmtes Attribut zurück (case-insensitive).

    Args:
        attribute (str): z.B. "A", "subdomain"

    Returns:
        Plugin | None: Gefundenes Plugin oder None
    """
    return plugin_registry.get(attribute.upper()) or plugin_registry.get(attribute.lower())

def get_all_plugins():
    """
    Gibt alle registrierten Plugins zurück (für Setup etc.)
    """
    return list(plugin_registry.values())