# Anix OS Official Branding & Overrides
PRODUCT_BRAND := Nothing
PRODUCT_DEVICE := Tetris
PRODUCT_MANUFACTURER := Nothing
PRODUCT_MODEL := CMF Phone 1

# Anix OS Specifics
PRODUCT_PROPERTY_OVERRIDES += \
    ro.anix.version=1.0-OFFICIAL \
    ro.anix.build.type=OFFICIAL \
    ro.anix.maintainer=#archsu \
    ro.anix.branding=AnixOS \
    ro.build.display.id=AnixOS-1.0-Tetris-OFFICIAL-#archsu \
    ro.surface_flinger.supports_background_blur=1 \
    ro.sf.blurs_are_expensive=0

# Disable OTA check for now
PRODUCT_PROPERTY_OVERRIDES += \
    anix.ota.enabled=false
