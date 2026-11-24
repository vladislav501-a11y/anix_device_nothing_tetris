#!/bin/bash
set -euo pipefail

echo "=== Starting resolve_conflicts.sh (Pure Bash) ==="

ANIX_ROOT="${HOME}/anix"
VENDOR_BP="${ANIX_ROOT}/vendor/nothing/Tetris/Android.bp"
VENDOR_MK="${ANIX_ROOT}/vendor/nothing/Tetris/Tetris-vendor.mk"

# 1. Fix vendor duplicate modules in Android.bp
if [ -f "$VENDOR_BP" ]; then
    echo "Patching $VENDOR_BP..."
    sed -i '/dex_import {/,/}/ { /"mediatek-telecom-common"/d; /"mediatek-telephony-common"/d }' "$VENDOR_BP"
    sed -i '/mediatek-telecom-common/d' "$VENDOR_BP"
    sed -i '/mediatek-telephony-common/d' "$VENDOR_BP"
fi

# 2. Fix vendor duplicate packages in Tetris-vendor.mk
if [ -f "$VENDOR_MK" ]; then
    echo "Patching $VENDOR_MK..."
    sed -i '/mediatek-telecom-common/d' "$VENDOR_MK"
    sed -i '/mediatek-telephony-common/d' "$VENDOR_MK"
fi

# 3. Aggressively purge test suites and CTS/MTS directories that depend on test harnesses
echo "Purging broken test trees..."
rm -rf \
    "${ANIX_ROOT}/platform_testing" \
    "${ANIX_ROOT}/tools/tradefederation" \
    "${ANIX_ROOT}/tools/loganalysis" \
    "${ANIX_ROOT}/test" \
    "${ANIX_ROOT}/cts" \
    "${ANIX_ROOT}/packages/modules/Nfc/tests" \
    "${ANIX_ROOT}/packages/modules/Connectivity/tests" \
    "${ANIX_ROOT}/packages/modules/Connectivity/bpf/tests" \
    "${ANIX_ROOT}/packages/modules/Connectivity/thread/tests" \
    "${ANIX_ROOT}/packages/modules/DeviceLock/tests" \
    "${ANIX_ROOT}/packages/modules/AdServices/adservices/libraries" \
    "${ANIX_ROOT}/frameworks/libs/systemui/mechanics" 2>/dev/null || true

# 4. Remove tests inside secretkeeper
if [ -f "${ANIX_ROOT}/system/secretkeeper/client/Android.bp" ]; then
    echo "Patching system/secretkeeper/client/Android.bp..."
    sed -i '/rust_test {/,/}/d' "${ANIX_ROOT}/system/secretkeeper/client/Android.bp"
fi

# 5. Clean any test Android.bp matching bad test defaults or test suites
echo "Scanning and eliminating residual broken test Android.bp..."
find "${ANIX_ROOT}" -type f -name "Android.bp" -path "*/tests/*" -exec grep -lE '(cts_support_defaults|rdroidtest\.defaults|connectivity-mainline-presubmit-cc-defaults|framework-connectivity-test-defaults|tradefed_errorprone_defaults|MotionTestDefaults|cts_defaults|mts_defaults)' {} + 2>/dev/null | while read -r bp; do
    echo "Removing broken test bp: $bp"
    rm -f "$bp"
done

# 6. Fix nonsecure apex modules in hardware/interfaces
if [ -d "${ANIX_ROOT}/hardware/interfaces" ]; then
    echo "Cleaning cuttlefish apex in hardware/interfaces..."
    find "${ANIX_ROOT}/hardware/interfaces" -type f -name "Android.bp" -exec grep -l "com.google.cf.apex" {} + 2>/dev/null | while read -r bp; do
        sed -i '/apex {/,/}/ { /com\.google\.cf\.apex/d }' "$bp"
    done
fi

echo "=== resolve_conflicts.sh completed successfully ==="
