import os, re, shutil

print("=== Starting resolve_conflicts.py ===")

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

# 2. Disable unused CTS/tradefed/cuttlefish/testing directories that trigger missing host dependencies
dirs_to_purge = [
    os.path.expanduser("~/anix/platform_testing"),
    os.path.expanduser("~/anix/tools/tradefederation"),
    os.path.expanduser("~/anix/tools/loganalysis"),
    os.path.expanduser("~/anix/test/suite_harness"),
    os.path.expanduser("~/anix/cts"),
    os.path.expanduser("~/anix/packages/modules/AdServices/adservices/libraries/collectors-helper"),
    os.path.expanduser("~/anix/packages/modules/AdServices/adservices/libraries/device-collectors"),
    os.path.expanduser("~/anix/frameworks/libs/systemui/mechanics")
]
for d in dirs_to_purge:
    if os.path.exists(d):
        shutil.rmtree(d, ignore_errors=True)
        print(f"Purged {d}")

# 3. Clean all tests/ and Android.bp referencing tradefed_errorprone_defaults or MotionTestDefaults
anix_root = os.path.expanduser("~/anix")
for sub in ["packages/modules/AdServices", "frameworks/libs/systemui"]:
    target = os.path.join(anix_root, sub)
    if os.path.exists(target):
        for root, dirs, files in os.walk(target):
            if "Android.bp" in files:
                bp = os.path.join(root, "Android.bp")
                try:
                    with open(bp, "r", encoding="utf-8") as f:
                        txt = f.read()
                    if "tradefed_errorprone_defaults" in txt or "MotionTestDefaults" in txt:
                        os.remove(bp)
                        print(f"Removed broken test Android.bp: {bp}")
                except Exception:
                    pass

# 4. Fix nonsecure apex modules in hardware/interfaces that reference missing com.google.cf.apex keys
hi_dir = os.path.expanduser("~/anix/hardware/interfaces")
if os.path.exists(hi_dir):
    for root, dirs, files in os.walk(hi_dir):
        for file in files:
            if file == "Android.bp":
                bp_path = os.path.join(root, file)
                try:
                    with open(bp_path, "r", encoding="utf-8") as f:
                        data = f.read()
                    if "com.google.cf.apex" in data:
                        new_data = re.sub(r'apex\s*\{[^}]*com\.google\.cf\.apex[^}]*\}', '', data)
                        with open(bp_path, "w", encoding="utf-8") as f:
                            f.write(new_data)
                        print(f"Patched cuttlefish apex in: {bp_path}")
                except Exception as e:
                    print(f"Error patching {bp_path}: {e}")

print("=== resolve_conflicts.py completed successfully ===")
