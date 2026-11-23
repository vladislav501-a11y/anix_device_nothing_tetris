import os, re, shutil

# 1. Fix vendor duplicate modules
vendor_bp = os.path.expanduser("~/anix/vendor/nothing/Tetris/Android.bp")
if os.path.exists(vendor_bp):
    with open(vendor_bp, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(rdex_imports*{s*name:s*mediatek-telecom-common[sS]*?n}n?, , content)
    content = re.sub(rdex_imports*{s*name:s*mediatek-telephony-common[sS]*?n}n?, , content)
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

# 2. Disable unused test / platform directories that cause missing host/tradefed/cuttlefish dependencies
dirs_to_purge = [
    os.path.expanduser("~/anix/platform_testing"),
    os.path.expanduser("~/anix/tools/tradefederation"),
    os.path.expanduser("~/anix/tools/loganalysis"),
    os.path.expanduser("~/anix/test/suite_harness")
]
for d in dirs_to_purge:
    if os.path.exists(d):
        shutil.rmtree(d, ignore_errors=True)
        print(f"Purged {d}")

# 3. Fix nonsecure apex modules in hardware/interfaces that reference missing com.google.cf.apex keys
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
                        new_data = re.sub(rapexs*{[^}]*com.google.cf.apex[^}]*}, , data)
                        with open(bp_path, "w", encoding="utf-8") as f:
                            f.write(new_data)
                        print(f"Patched cuttlefish apex in: {bp_path}")
                except Exception as e:
                    print(f"Error patching {bp_path}: {e}")
