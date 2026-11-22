import os, re

# 1. Fix vendor duplicate modules
vendor_bp = os.path.expanduser("~/anix/vendor/nothing/Tetris/Android.bp")
if os.path.exists(vendor_bp):
    with open(vendor_bp, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'dex_import\s*\{\s*name:\s*"mediatek-telecom-common"[\s\S]*?\n\}\n?', '', content)
    content = re.sub(r'dex_import\s*\{\s*name:\s*"mediatek-telephony-common"[\s\S]*?\n\}\n?', '', content)
    with open(vendor_bp, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed vendor/nothing/Tetris/Android.bp duplicate modules")

vendor_mk = os.path.expanduser("~/anix/vendor/nothing/Tetris/Tetris-vendor.mk")
if os.path.exists(vendor_mk):
    with open(vendor_mk, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [l for l in lines if "mediatek-telecom-common" not in l and "mediatek-telephony-common" not in l]
    with open(vendor_mk, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Fixed vendor/nothing/Tetris/Tetris-vendor.mk duplicate packages")

# 2. Disable unused platform_testing directory (contains dead cuttlefish test dependencies)
pt_bp = os.path.expanduser("~/anix/platform_testing/Android.bp")
if os.path.exists(pt_bp):
    os.remove(pt_bp)
    print("Removed ~/anix/platform_testing/Android.bp to prevent cuttlefish test errors")
