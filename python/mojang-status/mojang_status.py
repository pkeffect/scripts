#!/usr/bin/env python3
"""
Comprehensive Mojang/Minecraft Services Status Checker
Checks all current operational Mojang endpoints with proper status indicators
"""

import requests
from datetime import datetime
from typing import Dict, Tuple

# Configuration
TIMEOUT = 10
USER_AGENT = "MojangStatusChecker/1.0"
HEADERS = {"User-Agent": USER_AGENT}

# Test UUIDs and usernames for validation
TEST_UUID = "853c80ef3c3749fdaa49938b674adae6"  # jeb_
TEST_USERNAME = "jeb_"
TEST_LIBRARY = "com/mojang/authlib/3.16.29/authlib-3.16.29.jar"

# Service definitions with proper endpoints
SERVICES = {
    "🎮 Core Services": {
        "Session Server (Auth)": {
            "url": f"https://sessionserver.mojang.com/session/minecraft/profile/{TEST_UUID}",
            "method": "GET",
            "expected": 200
        },
        "Minecraft Services API": {
            "url": f"https://api.minecraftservices.com/minecraft/profile/lookup/name/{TEST_USERNAME}",
            "method": "GET",
            "expected": 200
        },
        "Blocked Servers List": {
            "url": "https://sessionserver.mojang.com/blockedservers",
            "method": "GET",
            "expected": 200
        }
    },
    
    "📦 Download Services": {
        "Version Manifest (Primary)": {
            "url": "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
            "method": "GET",
            "expected": 200
        },
        "Version Manifest (Legacy)": {
            "url": "https://launchermeta.mojang.com/mc/game/version_manifest.json",
            "method": "GET",
            "expected": 200
        },
        "Libraries Server": {
            "url": f"https://libraries.minecraft.net/{TEST_LIBRARY}",
            "method": "HEAD",
            "expected": 200
        },
        "Launcher Content": {
            "url": "https://launchercontent.mojang.com/v2/javaPatchNotes.json",
            "method": "GET",
            "expected": 200
        }
    },
    
    "🎨 Assets & Textures": {
        "Textures Server": {
            "url": "http://textures.minecraft.net/version/1",
            "method": "GET",
            "expected": [200, 404]  # 404 is expected for root
        }
    },
    
    "🔧 Legacy APIs": {
        "Mojang API (Legacy)": {
            "url": f"https://api.mojang.com/users/profiles/minecraft/{TEST_USERNAME}",
            "method": "GET",
            "expected": [200, 403]  # 403 is common due to bugs
        }
    },
    
    "🔐 Authentication": {
        "Xbox Live Auth": {
            "url": "https://user.auth.xboxlive.com/user/authenticate",
            "method": "POST",
            "expected": [400, 415]  # Expects valid payload, 400/415 means endpoint is up
        },
        "XSTS Token Service": {
            "url": "https://xsts.auth.xboxlive.com/xsts/authorize",
            "method": "POST",
            "expected": [400, 415]
        }
    }
}


def check_service(name: str, config: Dict) -> Tuple[str, int, str]:
    """Check a single service and return status"""
    try:
        method = config.get("method", "GET")
        expected = config["expected"]
        if not isinstance(expected, list):
            expected = [expected]
        
        if method == "GET":
            response = requests.get(config["url"], headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        elif method == "HEAD":
            response = requests.head(config["url"], headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        elif method == "POST":
            response = requests.post(config["url"], headers=HEADERS, timeout=TIMEOUT)
        
        status_code = response.status_code
        
        if status_code in expected:
            return "✅", status_code, "ONLINE"
        elif status_code == 429:
            return "⚠️", status_code, "RATE LIMITED"
        elif status_code in [500, 502, 503, 504]:
            return "❌", status_code, "SERVER ERROR"
        else:
            return "⚠️", status_code, "ISSUES"
            
    except requests.exceptions.Timeout:
        return "❌", 0, "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return "❌", 0, "CONNECTION FAILED"
    except requests.exceptions.RequestException as e:
        return "❌", 0, f"ERROR: {type(e).__name__}"


def get_latest_version() -> str:
    """Fetch the latest Minecraft version"""
    try:
        response = requests.get(
            "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        return data.get("latest", {}).get("release", "Unknown")
    except:
        return "Unable to fetch"


def print_header():
    """Print header with timestamp"""
    print("\n" + "="*70)
    print("🎮 MOJANG/MINECRAFT SERVICES STATUS CHECKER 🎮".center(70))
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def print_services():
    """Check and print all services"""
    for category, services in SERVICES.items():
        print(f"\n{category}")
        print("-" * 70)
        
        for service_name, config in services.items():
            icon, code, status = check_service(service_name, config)
            code_str = f"[{code}]" if code > 0 else ""
            print(f"{icon} {service_name:<35} {status:<20} {code_str}")


def print_version_info():
    """Print latest Minecraft version"""
    print("\n" + "="*70)
    print("📋 ADDITIONAL INFORMATION")
    print("-" * 70)
    version = get_latest_version()
    print(f"Latest Minecraft Java Edition: {version}")


def print_footer():
    """Print footer with legend"""
    print("\n" + "="*70)
    print("LEGEND")
    print("-" * 70)
    print("✅ ONLINE          - Service is fully operational")
    print("⚠️  ISSUES         - Service responding but with unexpected status")
    print("❌ OFFLINE/ERROR   - Service is not responding or has errors")
    print("="*70 + "\n")


def main():
    """Main execution"""
    print_header()
    print_services()
    print_version_info()
    print_footer()


if __name__ == "__main__":
    main()