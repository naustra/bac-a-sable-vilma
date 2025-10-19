#!/usr/bin/env python3
"""
Configuration des clés API pour les différentes sources d'images
"""

import os

# Configuration des APIs
API_KEYS = {
    'unsplash': '13whIoqJGm34CmTq_kiFHcS8S2IZ_VQqh3c5Nto3JgU',  # Clé intégrée
    'pexels': 'pkX7JBK8UmJ1CEs1wxJtlmmW23LXIOQYrhRySyNa2Pi2m3CwwosnnLih',  # Clé intégrée
    'pixabay': '25509242-01b42e750ab44d9c177d95999',  # Clé intégrée
    'wikimedia': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJkNmRjYzc5NmY5NzMzODE1NmFlMmQxOGFkMzE0OGY4NyIsImp0aSI6Ijg0NDNkMjY0M2Y1NGE1YjZjYzE1YmI4OGM0NTE5YTY5ZTM5MmU1ZDU0YTZhZTQ0MzBmOWJhNTQ4YTQyNjBmMmYzODkzMDY1Y2Y2ODQ5ZTJmIiwiaWF0IjoxNzYwOTA1OTkxLjY5MDQ4NywibmJmIjoxNzYwOTA1OTkxLjY5MDQ4OSwiZXhwIjozMzMxNzgxNDc5MS42ODg2MjUsInN1YiI6IjgwMDQwNTQyIiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.PLkgiMBZy4vPxr1c_4WcXqzTAW8fH1mpNgw1cFPfckbGpQt4AZXadPLOXM-ABiLnuFWIX63_85LJlOZ3kdVVC8usCHx-TYzjFMtsJHq1mK37SieTgMH3Ps0RV1uYBxGFkSwYP3j5uSu9fOxCkugMKYY7W_d0cFfbd75SqgpAbGLq3Hvtkor_b8JnI3UPryxKVJgUV2HZoffR5Ya97rIuDmYlptGXajoIdMAn4yifcR64FlYrYQnzj_aESmefEF8K0GvHylMii8NCs46C_3ZLuEmRHDFp7hEThFpDNQiF2dW9P-HMS7MeWQq6JPAPtZ8F0GZccuYDC1tcKvYeQTIY0nKNF38oAreFR5nMSKR_aXt5WcCX3qt4-g83POrDcfZdykdzHxSVB1O0dgNKryPXjHbFzpGu69EFg8aNjRAuuCjiLJi7V7HUbs4hH4LQr5gEYpXSCyEwQlFXeCCFz-lFBx4gJ_Z8uJEDTbb8OWADN-7bhVDC2GsF2i2VH5dMeul8TnVrJZxVNvkIzYI-D795w1u0qE3TsCAFLcW2FYIXbsBe3BMd2gyNGSJg_OHHsxAfayqKdU25TcdpkFACxnpcpmnwvkRY3gJqPWSCxBD9QWu0ATVx7snCXGplkBipTDcn1nBvQTqEo67A7046x_NGXX5mcmwy8f2aGuijQnvCZYE',  # Clé Wikimedia
}

# URLs des APIs
API_URLS = {
    'unsplash': 'https://api.unsplash.com',
    'pexels': 'https://api.pexels.com/v1',
    'pixabay': 'https://pixabay.com/api',
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
    'pixabay': {
        'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0'
    },
    'wikipedia': {
        'User-Agent': 'EducationalImageDownloader/2.0 (https://github.com/educational-tools; educational use) requests/2.31.0'
    },
    'wikimedia': {
        'Authorization': f'Bearer {API_KEYS["wikimedia"]}' if API_KEYS['wikimedia'] else '',
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
    if not API_KEYS['pixabay']:
        missing_keys.append('PIXABAY_API_KEY')
    if not API_KEYS['wikimedia']:
        missing_keys.append('WIKIMEDIA_API_KEY')

    if missing_keys:
        print("⚠️  Clés API manquantes:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n📝 Instructions:")
        print("   1. Unsplash: https://unsplash.com/developers")
        print("   2. Pexels: https://pexels.com/api")
        print("   3. Pixabay: https://pixabay.com/api/docs/")
        print("   4. Wikimedia: https://meta.wikimedia.org/wiki/API:Main_page")
        print("   5. Définir les variables d'environnement:")
        print("      export UNSPLASH_API_KEY='votre_cle'")
        print("      export PEXELS_API_KEY='votre_cle'")
        print("      export PIXABAY_API_KEY='votre_cle'")
        print("      export WIKIMEDIA_API_KEY='votre_cle'")
        return False

    return True

def get_available_sources():
    """Retourne les sources disponibles selon les clés API configurées"""
    sources = ['wikipedia']  # Toujours disponible (pas de clé API requise)

    if API_KEYS['unsplash']:
        sources.append('unsplash')
    if API_KEYS['pexels']:
        sources.append('pexels')
    if API_KEYS['pixabay']:
        sources.append('pixabay')
    if API_KEYS['wikimedia']:
        sources.append('wikimedia')

    return sources

if __name__ == "__main__":
    print("🔑 Configuration des APIs")
    print("=" * 40)

    sources = get_available_sources()
    print(f"✅ Sources disponibles: {', '.join(sources)}")

    if not check_api_keys():
        print("\n⚠️  Certaines sources ne seront pas disponibles")
