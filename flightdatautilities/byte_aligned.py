# For '717' sync pattern see ARINC 717-12 document section 5.3.1.2.
# For '573' sync pattern see ARINC 573-7 document Attachment 8-2.
# 'Custom 1' is a non-standard customised sync pattern.
# 573 may not be technically correct as the bit order is ambiguous in the specification.
# This was rectified in the ARINC 717 standard.

WPS = (64, 128, 256, 512, 1024, 2048)
SYNC_PATTERNS = {
    '573': (0xE24, 0x1DA, 0xE25, 0x1DB),
    '717': (0x247, 0x5B8, 0xA47, 0xDB8),
    'Custom 1': (0x0E0, 0x0E4, 0x0E8, 0x0EC),
}
MODES = SYNC_PATTERNS.keys()
STANDARD_MODES = ('573', '717')

