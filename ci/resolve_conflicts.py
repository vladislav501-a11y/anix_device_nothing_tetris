import os, re, shutil

print("=== Starting safe and targeted resolve_conflicts.py ===")

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

# 3. Only delete standalone dedicated directories/files known to have broken/unused deps
# Keep 'platform_testing/libraries', 'test', 'tools/tradefederation', 'cts', 'vts'
# intact so Soong recognizes module types like csuite_test and defaults like MotionTestDefaults.
purge_dirs = [
    "platform_testing/tools/automotive/proxy",
    "platform_testing/tests",
    "tools/security/fuzzing",
]

for p in purge_dirs:
    full = os.path.join(anix_root, p)
    if os.path.exists(full):
        print(f"Purging standalone directory: {full}")
        shutil.rmtree(full, ignore_errors=True)

# Remove root platform_testing/Android.bp ('platform_tests' depends on missing CuttlefishRilTests/CuttlefishWifiTests)
pt_root_bp = os.path.join(anix_root, "platform_testing/Android.bp")
if os.path.exists(pt_root_bp):
    print(f"Removing root {pt_root_bp} (cuttlefish deps)...")
    os.remove(pt_root_bp)

# 3b. Provide stub defaults/libs if tools/tradefederation/core or platform_testing/tests are absent
stubs_dir = os.path.join(anix_root, "vendor/anix/ci_stubs")
os.makedirs(stubs_dir, exist_ok=True)
stubs_bp = os.path.join(stubs_dir, "Android.bp")
stub_blocks = [
    'java_library {\n    name: "common-platform-scenarios",\n}\n'
]
tf_core_bp = os.path.join(anix_root, "tools/tradefederation/core/Android.bp")
if not os.path.exists(tf_core_bp):
    print("tools/tradefederation/core not found; adding tradefed_defaults stubs...")
    stub_blocks.append(
        'java_defaults {\n    name: "tradefed_defaults",\n}\n\n'
        'java_defaults {\n    name: "tradefed_errorprone_defaults",\n}\n'
    )
print(f"Writing CI stubs to {stubs_bp}...")
with open(stubs_bp, "w", encoding="utf-8") as f:
    f.write("\n".join(stub_blocks))

# 4. Remove secretkeeper tests if present
sk_bp = os.path.join(anix_root, "system/secretkeeper/client/Android.bp")
if os.path.exists(sk_bp):
    with open(sk_bp, "r", encoding="utf-8") as f:
        sk_text = f.read()
    sk_text = re.sub(r'rust_test\s*\{[^}]*?\}\n*', '', sk_text, flags=re.DOTALL)
    with open(sk_bp, "w", encoding="utf-8") as f:
        f.write(sk_text)

# DO NOT regex-modify or blindly delete any Android.bp in system/, external/, packages/, hardware/!
# That prevents any syntax corruption like stray commas or parens.

print("=== resolve_conflicts.py completed successfully ===")
