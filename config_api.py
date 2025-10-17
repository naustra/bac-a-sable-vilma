#!/usr/bin/env python3
"""
Configuration des clés API pour les différentes sources d'images
"""

import os

# Configuration des APIs
API_KEYS = {
    'unsplash': '13whIoqJGm34CmTq_kiFHcS8S2IZ_VQqh3c5Nto3JgU',  # Clé intégrée
    'pexels': 'pkX7JBK8UmJ1CEs1wxJtlmmW23LXIOQYrhRySyNa2Pi2m3CwwosnnLih',  # Clé intégrée
}

# URLs des APIs
API_URLS = {
    'unsplash': 'https://api.unsplash.com',
    'pexels': 'https://api.pexels.com/v1',
    'wikipedia': 'https://en.wikipedia.org/w/api.php',
    'wikimedia': 'https://commons.wikimedia.org/w/api.php'
}

# Headers par défaut
API_HEADERS = {
    'unsplash': {
        'Authorization': f'Client-ID {API_KEYS["unsplash"]}' if API_KEYS['unsplash'] else ''
    },
    'pexels': {
        'Authorization': API_KEYS['pexels'] if API_KEYS['pexels'] else ''
    },
    'wikipedia': {
        'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0'
    },
    'wikimedia': {
        'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0'
    }
}

def check_api_keys():
    """Vérifie si les clés API sont configurées"""
    missing_keys = []

    if not API_KEYS['unsplash']:
        missing_keys.append('UNSPLASH_API_KEY')
    if not API_KEYS['pexels']:
        missing_keys.append('PEXELS_API_KEY')

    if missing_keys:
        print("⚠️  Clés API manquantes:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n📝 Instructions:")
        print("   1. Unsplash: https://unsplash.com/developers")
        print("   2. Pexels: https://pexels.com/api")
        print("   3. Définir les variables d'environnement:")
        print("      export UNSPLASH_API_KEY='votre_cle'")
        print("      export PEXELS_API_KEY='votre_cle'")
        return False

    return True

def get_available_sources():
    """Retourne les sources disponibles selon les clés API configurées"""
    sources = ['wikipedia', 'wikimedia']  # Réactivés avec l'API REST

    if API_KEYS['unsplash']:
        sources.append('unsplash')
    if API_KEYS['pexels']:
        sources.append('pexels')

    return sources

if __name__ == "__main__":
    print("🔑 Configuration des APIs")
    print("=" * 40)

    sources = get_available_sources()
    print(f"✅ Sources disponibles: {', '.join(sources)}")

    if not check_api_keys():
        print("\n⚠️  Certaines sources ne seront pas disponibles")
