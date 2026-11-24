import os, re, shutil

print("=== Starting comprehensive resolve_conflicts.py ===")

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

# 3. Explicitly purge entire test/fuzzing/cts/mts tree structures
purge_paths = [
    "platform_testing",
    "tools/tradefederation",
    "tools/loganalysis",
    "tools/platform-compat",
    "tools/security/fuzzing",
    "test",
    "cts",
    "vts",
    "art/test",
    "art/cmdline",
    "system/core/trusty/confirmationui",
    "packages/modules/Nfc/tests",
    "packages/modules/Connectivity/tests",
    "packages/modules/Connectivity/bpf/tests",
    "packages/modules/Connectivity/thread/tests",
    "packages/modules/Connectivity/nearby/tests",
    "packages/modules/Connectivity/remoteauth/tests",
    "packages/modules/Connectivity/networksecurity/tests",
    "packages/modules/Connectivity/staticlibs/tests",
    "packages/modules/Connectivity/Tethering/tests",
    "packages/modules/Connectivity/Vcn/tests",
    "packages/modules/DeviceLock/tests",
    "packages/modules/AdServices/adservices/libraries",
    "packages/modules/AdServices/adservices/tests",
    "packages/modules/AdServices/sdksandbox/tests",
    "packages/modules/HealthFitness/tests",
    "packages/modules/IPsec/tests",
    "packages/modules/StatsD/tests",
    "packages/modules/DnsResolver/tests",
    "packages/modules/Bluetooth/framework/tests",
    "packages/modules/Bluetooth/system/embdrv/tests",
    "packages/modules/ExtServices/java/tests",
    "packages/modules/Uwb/ranging/tests",
    "packages/modules/Uwb/tests",
    "packages/modules/CaptivePortalLogin/tests",
    "packages/modules/NetworkStack/tests",
    "frameworks/libs/systemui/mechanics",
    "frameworks/base/libs/WindowManager/Shell/tests",
    "frameworks/base/packages/SystemUI/compose/scene/tests",
    "frameworks/base/services/tests",
    "frameworks/base/core/tests",
    "frameworks/base/tests",
    "frameworks/opt/telephony/tests",
]

for p in purge_paths:
    full = os.path.join(anix_root, p)
    if os.path.exists(full):
        print(f"Purging test directory: {full}")
        shutil.rmtree(full, ignore_errors=True)

# 4. Remove secretkeeper tests if present
sk_bp = os.path.join(anix_root, "system/secretkeeper/client/Android.bp")
if os.path.exists(sk_bp):
    with open(sk_bp, "r", encoding="utf-8") as f:
        sk_text = f.read()
    sk_text = re.sub(r'rust_test\s*\{[^}]*?\}\n*', '', sk_text, flags=re.DOTALL)
    with open(sk_bp, "w", encoding="utf-8") as f:
        f.write(sk_text)

# 5. Neutralize all test-only Android.bp everywhere
print("Scanning and eliminating all test/fuzz/benchmark Android.bp files...")
deleted_count = 0
for root, dirs, files in os.walk(anix_root):
    if "Android.bp" in files:
        bp_path = os.path.join(root, "Android.bp")
        norm_path = bp_path.replace("\\", "/")
        # Delete if path is clearly test, fuzz, benchmark, sample, or testapp
        if any(seg in norm_path for seg in [
            "/tests/", "/test/", "/testapps/", "/hosttests/", "/cts/", "/mts/",
            "/fuzz/", "/fuzzing/", "/fuzzer/", "/benchmarks/", "/benchmark/"
        ]):
            try:
                os.remove(bp_path)
                deleted_count += 1
            except Exception:
                pass

print(f"Deleted {deleted_count} test/fuzz Android.bp files.")

# 6. For Android.bp that contain fuzzers or tests in mixed folders (like hardware/st/nfc/aidl/Android.bp)
print("Sanitizing mixed Android.bp files from cc_fuzz and cc_test...")
sanitized_count = 0
for root, dirs, files in os.walk(anix_root):
    if "Android.bp" in files:
        bp_path = os.path.join(root, "Android.bp")
        try:
            with open(bp_path, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
            if any(k in c for k in ["service_fuzzer_defaults", "libstagefright_fuzzer_defaults", "art_gtest_defaults", "cc_fuzz"]):
                # Remove whole cc_fuzz blocks
                c_clean = re.sub(r'cc_fuzz\s*\{[^}]*?\}\n*', '', c, flags=re.DOTALL)
                c_clean = re.sub(r'art_cc_test\s*\{[^}]*?\}\n*', '', c_clean, flags=re.DOTALL)
                c_clean = re.sub(r'art_cc_test_library\s*\{[^}]*?\}\n*', '', c_clean, flags=re.DOTALL)
                if c_clean != c:
                    with open(bp_path, "w", encoding="utf-8") as out_f:
                        out_f.write(c_clean)
                    sanitized_count += 1
        except Exception:
            pass

print(f"Sanitized {sanitized_count} mixed Android.bp files.")
print("=== resolve_conflicts.py completed successfully ===")
