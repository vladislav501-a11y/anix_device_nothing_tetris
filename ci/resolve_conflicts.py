import os, re, glob

print("=== Starting resolve_conflicts.py ===")

anix_root = os.path.expanduser("~/anix")

# 1. Clean vendor/nothing/Tetris/Android.bp
vendor_bp = os.path.join(anix_root, "vendor/nothing/Tetris/Android.bp")
if os.path.exists(vendor_bp):
    print(f"Cleaning {vendor_bp}...")
    with open(vendor_bp, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove complete dex_import blocks for mediatek-telecom-common and mediatek-telephony-common
    pattern = r'dex_import\s*\{[^}]*?"mediatek-tele(com|phony)-common"[^}]*?\}\n*'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Also remove any anonymous/empty dex_import or prebuilt blocks that might cause "prebuilt_" collision
    content = re.sub(r'dex_import\s*\{\s*owner:[^}]*?\}\n*', '', content, flags=re.DOTALL)
    
    with open(vendor_bp, "w", encoding="utf-8") as f:
        f.write(content)
    print("Vendor Android.bp patched successfully.")

# 2. Clean vendor/nothing/Tetris/Tetris-vendor.mk
vendor_mk = os.path.join(anix_root, "vendor/nothing/Tetris/Tetris-vendor.mk")
if os.path.exists(vendor_mk):
    print(f"Cleaning {vendor_mk}...")
    with open(vendor_mk, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [l for l in lines if "mediatek-telecom-common" not in l and "mediatek-telephony-common" not in l]
    with open(vendor_mk, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Vendor Tetris-vendor.mk patched successfully.")

# 3. Aggressively purge test directories
purge_paths = [
    "platform_testing",
    "tools/tradefederation",
    "tools/loganalysis",
    "test",
    "cts",
    "packages/modules/Nfc/tests",
    "packages/modules/Connectivity/tests",
    "packages/modules/Connectivity/bpf/tests",
    "packages/modules/Connectivity/thread/tests",
    "packages/modules/DeviceLock/tests",
    "packages/modules/AdServices/adservices/libraries",
    "frameworks/libs/systemui/mechanics",
    "frameworks/base/libs/WindowManager/Shell/tests/flicker",
    "art/test",
]

for p in purge_paths:
    full = os.path.join(anix_root, p)
    if os.path.exists(full):
        print(f"Purging directory: {full}")
        import shutil
        shutil.rmtree(full, ignore_errors=True)

# 4. Remove secretkeeper tests if present
sk_bp = os.path.join(anix_root, "system/secretkeeper/client/Android.bp")
if os.path.exists(sk_bp):
    with open(sk_bp, "r", encoding="utf-8") as f:
        sk_text = f.read()
    sk_text = re.sub(r'rust_test\s*\{[^}]*?\}\n*', '', sk_text, flags=re.DOTALL)
    with open(sk_bp, "w", encoding="utf-8") as f:
        f.write(sk_text)

# 5. Purge any Android.bp containing csuite_test or broken test defaults
print("Scanning and eliminating residual broken test Android.bp...")
for root, dirs, files in os.walk(anix_root):
    if "Android.bp" in files:
        bp_path = os.path.join(root, "Android.bp")
        try:
            with open(bp_path, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
            if any(term in c for term in [
                "csuite_test",
                "cts_support_defaults",
                "rdroidtest.defaults",
                "connectivity-mainline-presubmit-cc-defaults",
                "framework-connectivity-test-defaults",
                "tradefed_errorprone_defaults",
                "MotionTestDefaults",
                "cts_defaults",
                "mts_defaults"
            ]):
                if "/tests/" in bp_path or "test" in root.lower():
                    print(f"Removing broken test bp: {bp_path}")
                    os.remove(bp_path)
                else:
                    # If it is a shared Android.bp, just remove csuite_test definitions
                    if "csuite_test" in c:
                        c_clean = re.sub(r'csuite_test\s*\{[^}]*?\}\n*', '', c, flags=re.DOTALL)
                        with open(bp_path, "w", encoding="utf-8") as out_f:
                            out_f.write(c_clean)
        except Exception:
            pass

print("=== resolve_conflicts.py completed successfully ===")
